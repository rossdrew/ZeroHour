import sys
import requests, trello, pyral #NOTE: pyral Doesn't support Python 3 and bug #40 is an issue
import csv
import getpass
import datetime				
import re
import html2text
import urllib

from pyral import Rally, rallyWorkset

"""
        ZeroHour Package v0.2
[Package for linking Rally and Trello]

**** Requires a custom version of pyral ****

TODO : Deal with command line arguments better.  
       Perhaps a ZeroHourProperties class that 
       holds all the values and move the global 
       vars in there as well.

     : Extend to sync Rally and Trello

"""

UNDER_DEVELOPMENT = True
DEBUG_OUTPUT = True

RALLY_PREFIX 	= re.compile(r'^[A-Z]*[^[0-9]]*')

def parseCommandLineOptions(cmdLineOptions):
	"""Parse arguments (a list) into a dictionary
	No idea why the argument order gets messed up

	>>> parseCommandLineOptions(['--testa=a','--testb=b','--testc=c'])
	{'testa': 'a', 'testc': 'c', 'testb': 'b'}"""
	optionsDictionary = dict()

	for option in cmdLineOptions:
		parts = option[2:].split('=')
		optionsDictionary[parts[0]] = parts[1]
	return optionsDictionary

def initTrello(cmdLineOptions):
	"""Return a trelloApi that has the token set.  If no token provided, output token URL.  Also check required arguments are present"""
	requiredOptions = {'trelloUser', 'trelloBoard', 'trelloList'}
	print 'Setting up Trello (trello v(0.9.1))...'

	if 'trelloID' in cmdLineOptions:
		trelloApi = trello.TrelloApi(cmdLineOptions['trelloID'])
	else:
		print "ERROR: No trelloID specified"
		sys.exit()

	if 'trelloToken' not in cmdLineOptions:
		url = trelloApi.get_token_url("Rally Integration") 
		print "ERROR: trelloToken required: Token URL: '{}'".format(url)
		sys.exit()

	if not requiredOptions.issubset(cmdLineOptions):
		print "ERROR: One of more of the required Trello options ({}) missing.".format(requiredOptions)
		sys.exit()

	trelloApi.set_token(cmdLineOptions['trelloToken'])
	return trelloApi

def getTrelloBoardsForUser(trelloID, trelloToken, trelloUserName):
	boards = trello.Members(trelloID, trelloToken).get_board(trelloUserName)
	return boards

def getTrelloBoard(trelloID, trelloToken, trelloUserName, boardName):
	"""Return a Trello Board object from Trello server"""
	boards = getTrelloBoardsForUser(trelloID, trelloToken, trelloUserName)
	tBoards = [board for board in boards if board['name'] == boardName]
	if len(tBoards) < 1:
		print "ERROR: Trello board '{}' not found.".format(boardName)
		sys.exit()
	return tBoards[0]

def getTrelloListsForBoard(trelloID, trelloToken, trelloBoard):
	"""Return all lists for the given Trello board"""
	lists = trello.Boards(trelloID, trelloToken).get_list(trelloBoard['id'])
	return lists

def getAllTrelloTicketsForBoard(trelloID, trelloToken, trelloBoard):
	"""Return a list of all Trello tickets from all lists for the given board"""
	lists = getTrelloListsForBoard(trelloID, trelloToken, trelloBoard)
	cardsInBoard = []
	for list in lists:
		cardsInList = trello.Lists(trelloID, trelloToken).get_card(list['id'])
		print "Adding {} cards for {}".format(len(cardsInList), list['name'])
		cardsInBoard += cardsInList
	return cardsInBoard


def getTrelloList(trelloID, trelloToken, trelloBoard, trelloListName):
	"""Return a Trello List object from Trello server"""
	allTrelloLists = getTrelloListsForBoard(trelloID, trelloToken, trelloBoard)
	tLists = [list for list in allTrelloLists if list['name'] == trelloListName]
	if len(tLists) < 1:
		print "ERROR: Trello list '{}' not found.".format(cmdLineOptions['trelloList'])
		sys.exit()
	return tLists[0]

def getRallyArtifactTypeFromID(FullFormattedID):
	"""Returns Rally.ARTIFACT_TYPE given a FormattedID by extracting the prefix and looking it up in pyral
		e.g. DE7410 = [DE]7410 = 'Defect'

		>>> getRallyArtifactTypeFromID('DE7410')
		'Defect'
		>>> getRallyArtifactTypeFromID('S1234')
		'Story'
		>>> getRallyArtifactTypeFromID('US1234')
		'Story'
		"""

	return Rally.ARTIFACT_TYPE[re.search(RALLY_PREFIX, FullFormattedID).group(0)]

def initRally(cmdLineOptions):
	requiredOptions = {'rallyServer','rallyUser','rallyPassword'}
	print 'Setting up Rally (pyral v{version})...'.format(version = pyral.__version__)
	if not requiredOptions.issubset(cmdLineOptions):
		print "ERROR: One of more of the required Rally options ({}) missing.".format(requiredOptions)
		sys.exit()
	return Rally(cmdLineOptions['rallyServer'], cmdLineOptions['rallyUser'], cmdLineOptions['rallyPassword'])

def getUserAndEmailList(rally, trelloID, trelloToken, trelloBoard):
	"""Return a dict of Trello usernames to Rally/Trello e-mails using full name to link them
			[Username (trello) <-- Full Name (Both) --> E-mail (rally)]
	This is necessary because Trello users can only view their own e-mail addresses"""
	emailList = dict()
	all_users = rally.getAllUsers() #XXX This call crashes pyral 1.1.1 - Custom pyral changes are needed
	for user in all_users:
		rallyName = ("{} {}".format(user.FirstName, user.LastName)).lower()
		emailList[rallyName] = user.EmailAddress

	boardMembers = trello.Boards(trelloID, trelloToken).get_member(trelloBoard['id'])
	emailToUserName = dict()
	for member in boardMembers:
		trelloName = ("{}".format(member['fullName'])).lower()
		emailToUserName[member['username']] = emailList[trelloName]

	return emailToUserName

def getRallyUserNameQueryString(nameDictionary):
	"""Return query string which includes all users listen in nameDictionary such that:-

		((((
			(Owner.UserName = "a@evogi.com") OR (Owner.UserName = "b@evogi.com")
		   ) OR (Owner.UserName = "c@evogi.com")
		  ) OR (Owner.UserName = "d@evogi.com")
		 ) OR (Owner.UserName = "e@evogi.com")
		)

	- First condition is standard ((name = a) OR (name = b))
	- For every extra condition, prepend with '(' then add 'OR (new condition)' and finish with ')''

	>>> getRallyUserNameQueryString({'steve' : 'steve@evogi.com'})
	'AND (Owner.UserName = "steve@evogi.com")'
	>>> getRallyUserNameQueryString({'steve' : 'steve@evogi.com', 'bob' : 'bob@evogi.com'})
	'AND ((Owner.UserName = "steve@evogi.com") OR (Owner.UserName = "bob@evogi.com"))'
	"""
	usersQuery = ""
	i = 1
	for user in nameDictionary:
		userQuery = "(Owner.UserName = \"{}\")".format(nameDictionary[user])
		if i > 1:
			usersQuery = "({} OR {})".format(usersQuery, userQuery)
		else:
			usersQuery = userQuery
		i+=1
	return "AND {}".format(usersQuery)

def buildRallyArtifactInclusionQuery(rally, trelloID, trelloToken, trelloBoard):
	users_rallyToTrello = getUserAndEmailList(rally, trelloID, trelloToken, trelloBoard) 
	users_query = getRallyUserNameQueryString(users_rallyToTrello)
	inclusionQuery = "(State != Completed) {}".format(users_query) 
	if DEBUG_OUTPUT: print "Getting Rally tasks in the criteria '{}'".format(inclusionQuery)
	return inclusionQuery

def getRallyRallyArtifactList(rally, inclusionQuery, migrationFile=""):
	"""Get all Rally artifacts that match required criteria"""
	print "Retrieving list of Rally artifacts to migrate..."

	backupMigrationListToFile = len(migrationFile) > 0

	if backupMigrationListToFile: migrationList = open(migrationFile, 'w')

	openTasks = []
	response = rally.get('Task', fetch="FormattedID", query=inclusionQuery, order='DragAndDropRank') 	
	print "\t{} Tasks found".format(response.resultCount)	
	for story in response:
		openTasks.append(story.FormattedID)
		if backupMigrationListToFile: migrationList.write("{}\n".format(story.FormattedID))
		if DEBUG_OUTPUT: print "Added {} to Rally tasks...".format(story.FormattedID)

	print "...{} artifacts collected.".format(len(openTasks))
	if backupMigrationListToFile: migrationList.close()
	return openTasks

class TrelloCard:
	"""Representation of a card on Trello, essentially a 'Defect' or 'UserStory' containing multiple 'Task's"""
	def __init__(self, cardID):
		self.cardID = cardID
		self.tasks = []
		self.orderValue = 0

	def setOrderValue(self, val):
		self.orderValue = val

	def addTask(self, task):
		self.tasks.append(task)

def printTrelloCards(trelloCards):
	"""Output heirachical list provided trello cards"""
	print "\n****** WorkProducts and Children ******"
	for cardID in trelloCards:
		print "{} : {}".format(trelloCards[cardID].cardID, getRallyArtifactTypeFromID(cardID))
		for task in trelloCards[cardID].tasks:
			print "\t{} : {}".format(task.FormattedID, getRallyArtifactTypeFromID(task.FormattedID))
	print "***************************************\n"

def sortArtifactsIntoTrelloTasks(rally, cardList = []):
	"""Return a list of top level TrelloCard objects with associated Trello Tasks sorted into them
	   Requires a Rally object to make requests on object to figure out WorkItem (parent)"""

	print "Sorting Trello Tasks into parent Artifacts/Cards"
	trelloCards = dict()
	for id in cardList:
		items = rally.get('Task', fetch=True, query="({})".format("FormattedID = {}".format(id)))
		if items.resultCount is 1:
			rallyItem = items.next()
			parentFormattedID = getattr(rallyItem.WorkProduct, 'FormattedID')
			
			if parentFormattedID not in trelloCards:
				if DEBUG_OUTPUT: print "Creating card {}".format(parentFormattedID)
				trelloCard = TrelloCard(parentFormattedID)
				trelloCards[parentFormattedID] = trelloCard

			if DEBUG_OUTPUT: print "\tAdding {} to card {}".format(rallyItem.FormattedID, parentFormattedID)
			trelloCards[parentFormattedID].addTask(rallyItem)
	if DEBUG_OUTPUT: printTrelloCards(trelloCards)
	return trelloCards

def orderCards(rally, cards):
	"""Return a DragAndDropRank ordered array of TrelloCard (cards) ID"""
	print "Calculating DragAndDropRank order..."
	orderedParentCards = [] ##get a list of all cards
	countDone = 0
	for cardID in cards:
		cardArtifactType = getRallyArtifactTypeFromID(cardID)
		items = rally.get(cardArtifactType, fetch=True, query="({})".format("FormattedID = {}".format(cardID)), order='DragAndDropRank')
		orderedParentCards.extend(items)
	#Order parent cards by DragAndDropRank
	orderedParentCards.sort(key=lambda c: c.DragAndDropRank, reverse=True)
	return orderedParentCards

def addTrelloTasklist(trelloCard, tasks, trelloID, trelloToken):
	remoteTrelloCards = trello.Cards(trelloID, trelloToken)
	trelloChecklists = trello.Checklists(trelloID, trelloToken)
	taskList = remoteTrelloCards.new_checklist(trelloCard['id'], None)
	trelloChecklists.update_name(taskList['id'], "Tasks")
	for task in tasks:
		trelloChecklists.new_checkItem(taskList['id'], task.Name)

def addTrelloCard(cardTitle, description, trelloID, trelloToken, trelloList):
	remoteTrelloCards = trello.Cards(trelloID, trelloToken)
	cardOnTrello = remoteTrelloCards.new(cardTitle, trelloList['id'], description)
	return cardOnTrello

def addTrelloCardWithTasks(card, tasks, trelloID, trelloToken, trelloList, changeLog):
	"""Add 'card' to LIVE Trello with 'tasks'"""
	cardArtifactType = getRallyArtifactTypeFromID(card.FormattedID)
	print "Adding {} ({})...".format(cardArtifactType, card.FormattedID)
	descriptionAsMarkdown = html2text.html2text(card.Description)
	cardTitle = "{} - {}".format(card.FormattedID, card.Name)

	try:
		cardOnTrello = addTrelloCard(cardTitle, descriptionAsMarkdown, trelloID, trelloToken, trelloList)
		addTrelloTasklist(cardOnTrello, tasks, trelloID, trelloToken)
		changeLog.write("{} Added Trello card with {} tasks, for {}\n".format(datetime.datetime.now(), len(tasks), card.FormattedID))
	except Exception as ex: #TODO More info - Should only catch ConnectionError and HTTPError
		template = "An exception of type {0} occured. \nArguments:{1!r}"
		message = template.format(type(ex).__name__, ex.args)
		print message
		changeLog.write("{} ERROR adding trello card {}: {}\n\t{}\n".format(datetime.datetime.now(), card.FormattedID, type(ex).__name__, ex.args))
	
def addTrelloCards(orderedParentCards, trelloCards, trelloID, trelloToken, trelloList, changeLog):
	for card in orderedParentCards:
		addTrelloCardWithTasks(card, trelloCards[card.FormattedID].tasks, trelloID, trelloToken, trelloList, changeLog)

def migrateRallyArtifactsToTrello(rally, trelloID, trelloToken, trelloBoard):
	"""Migrate non-closed Rally artifacts to Trello as Cards (Artifacts) and Checklists (Tasks) if they have a matching user on the given trelloBoard"""
	artifactQuery = buildRallyArtifactInclusionQuery(rally, trelloID, trelloToken, trelloBoard)
	tasksForMigration = getRallyRallyArtifactList(rally, artifactQuery, 'migration.list')
	trelloCards = sortArtifactsIntoTrelloTasks(rally, tasksForMigration)
	orderedParentCards = orderCards(rally, trelloCards)
	zerohour.addTrelloCards(orderedParentCards, trelloCards, trelloID, trelloToken, tList, changeLog)


def syncRallyAndPython(rally, trelloID, trelloToken, trelloBoard):
	print "Synching Rally to Trello board {}".format(trelloBoard['name'])
	#get all Rally tickets 
	artifactQuery = buildRallyArtifactInclusionQuery(rally, trelloID, trelloToken, trelloBoard)
	rallyTasks = getRallyRallyArtifactList(rally, artifactQuery, 'rallyArtifact.list')
	trelloCards = sortArtifactsIntoTrelloTasks(rally, rallyTasks)

	#get all Trello tickets (that's every ticket on a given board, in every list)
	lists = getTrelloListsForBoard(trelloID, trelloToken, trelloBoard)
	tickets = getAllTrelloTicketsForBoard(trelloID, trelloToken, trelloBoard)

	#Compare all details from tickets and trelloCards

	#   TODO "Merge" changes...HOW!?!?
	#TODO Add Rally Artifacts that dont exist in Trello
