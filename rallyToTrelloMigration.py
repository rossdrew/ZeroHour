import sys
import requests, trello, pyral #NOTE: pyral Doesn't support Python 3 
import csv
import getpass
import datetime				
import re
import html2text
import urllib

from pyral import Rally, rallyWorkset

DEBUG_OUTPUT 	  = True  				#Show debug output
UNDER_DEVELOPMENT = True   				#Set when under development so that unit tests are run
CHANGE_LOG 		  = 'change.log' 		
MIGRATION_FILE 	  = 'migration.list'

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

TRELLO_ID 	 	= ""
TRELLO_BOARD 	= ""
TRELLO_LIST 	= ""
TRELLO_USER 	= ""
TRELLO_TOKEN 	= ""

RALLY_URI 		= ""
RALLY_USER 		= ""
RALLY_PASS 		= ""
RALLY_PREFIX 	= re.compile(r'^[A-Z]*[^[0-9]]*')

print '[Migrating Rally -> Trello]'

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

def squashTrelloCards(rally, cardList = []):
	"""Return a list of top level TrelloCard objects with associated Trellot Tasks sorted into them
	   Requires a Rally object to make requests on object to figure out WorkItem (parent)"""

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
	return trelloCards

def buildMigrationList(rally, backupMigrationListToFile, inclusionQuery):
	"""Get all Rally artifacts that match required criteria"""
	print "Retrieving list of Rally artifacts to migrate..."

	if backupMigrationListToFile: migrationList = open(MIGRATION_FILE, 'w')

	openTasks = []
	response = rally.get('Task', fetch="FormattedID", query=inclusionQuery, order='DragAndDropRank') 	
	print "\t{} Tasks found".format(response.resultCount)	
	for story in response:
		openTasks.append(story.FormattedID)
		if backupMigrationListToFile: migrationList.write("{}\n".format(story.FormattedID))
		if DEBUG_OUTPUT: print "Added {} to migration list...".format(story.FormattedID)

	print "...{} artifacts collected.".format(len(openTasks))
	if backupMigrationListToFile: migrationList.close()
	return openTasks

def addTrelloCard(card, tasks, boardList):
	"""Add 'card' to LIVE Trello with 'tasks'"""
	cardArtifactType = getRallyArtifactTypeFromID(card.FormattedID)
	print "Adding {} ({})...".format(cardArtifactType, card.FormattedID)
#Card
	remoteTrelloCards = trello.Cards(TRELLO_ID, TRELLO_TOKEN)
	descriptionAsMarkdown = html2text.html2text(card.Description)
	cardTitle = "{} - {}".format(card.FormattedID, card.Name)
	try:
		#Adding Defect (DE8547)... 400 Client Error: Bad Request for url: https://trello.com/1/cards?token=6fc2b7af09291eac30e5bef39da14f37a0e5a469c6f2b85023fcc8212083b2d3&key=984edd6395e2c74b5a35ffec6400be0b
		cardOnTrello = remoteTrelloCards.new(cardTitle, boardList['id'], descriptionAsMarkdown) 
	#Tasks
		trelloChecklists = trello.Checklists(TRELLO_ID, TRELLO_TOKEN)
		taskList = remoteTrelloCards.new_checklist(cardOnTrello['id'], None)
		trelloChecklists.update_name(taskList['id'], "Tasks")
		for task in tasks:
			trelloChecklists.new_checkItem(taskList['id'], task.Name)

		changeLog.write("{} Added Trello card with {} tasks, for {}\n".format(datetime.datetime.now(), len(tasks), card.FormattedID))

	except Exception as ex: #TODO More info
		template = "An exception of type {0} occured. Arguments:\n{1!r}"
		message = template.format(type(ex).__name__, ex.args)
		print message
		changeLog.write("{} ERROR adding trello card {}: {}\n\t{}\n".format(datetime.datetime.now(), card.FormattedID, type(ex).__name__, ex.args))
	

def orderCards(cards):
	"""Return a DragAndDropRank ordered array of TrelloCard (cards) ID"""
	print "Calculating DragAndDropRank order..."
	orderedParentCards = [] ##get a list of all cards
	for cardID in cards:
		cardArtifactType = getRallyArtifactTypeFromID(cardID)
		items = rally.get(cardArtifactType, fetch=True, query="({})".format("FormattedID = {}".format(cardID)), order='DragAndDropRank')
		orderedParentCards.extend(items)
	#Order parent cards by DragAndDropRank
	orderedParentCards.sort(key=lambda c: c.DragAndDropRank, reverse=True)
	return orderedParentCards

def getUserAndEmailList():
	"""Return a dict of Trello usernames to Rally/Trello e-mails using full name to link them
			[Username (trello) <-- Full Name (Both) --> E-mail (rally)]
	This is necessary because Trello users can only view their own e-mail addresses"""
	emailList = dict()
	all_users = rally.getAllUsers()
	for user in all_users:
		rallyName = ("{} {}".format(user.FirstName, user.LastName)).lower()
		emailList[rallyName] = user.EmailAddress

	boardMembers = trello.Boards(TRELLO_ID, TRELLO_TOKEN).get_member(testBoard['id'])
	emailToUserName = dict()
	for member in boardMembers:
		trelloName = ("{}".format(member['fullName'])).lower()
		emailToUserName[member['username']] = emailList[trelloName]

	return emailToUserName

def buildRallyArtifactInclusionQuery():
	users_rallyToTrello = getUserAndEmailList() 
	users_query = getRallyUserNameQueryString(users_rallyToTrello)
	#return "(State != Completed) {}".format(users_query) 
	return "(State != Completed) {}".format(users_query) 

def printTrelloCards(trelloCards):
	"""Output heirachical list provided trello cards"""
	print "\n****** WorkProducts and Children ******"
	for cardID in trelloCards:
		print "{} : {}".format(trelloCards[cardID].cardID, getRallyArtifactTypeFromID(cardID))
		for task in trelloCards[cardID].tasks:
			print "\t{} : {}".format(task.FormattedID, getRallyArtifactTypeFromID(task.FormattedID))
	print "***************************************\n"


#Trello Setup
print 'Setting up Trello (trello v(0.9.1))...'
trelloApi = trello.TrelloApi(TRELLO_ID)
trelloApi.set_token(TRELLO_TOKEN)
boards = trello.Members(TRELLO_ID, TRELLO_TOKEN).get_board(TRELLO_USER)
testBoard = [board for board in boards if board['name'] == TRELLO_BOARD][0]
backlogList = [list for list in trello.Boards(TRELLO_ID, TRELLO_TOKEN).get_list(testBoard['id']) if list['name'] == TRELLO_LIST][0]

#Rally Setup
print 'Setting up Rally (pyral v{version})...'.format(version = pyral.__version__)
rally = Rally(RALLY_URI, RALLY_USER, RALLY_PASS)

#Log file setup - if we can't prevent stupid, we should audit it
print "Setting up log file..."
changeLog = open(CHANGE_LOG, 'a')

artifactInclusionQuery = buildRallyArtifactInclusionQuery()
if DEBUG_OUTPUT: print artifactInclusionQuery

tasksForMigration = buildMigrationList(rally, True, artifactInclusionQuery)
trelloCards = squashTrelloCards(rally, tasksForMigration)
if DEBUG_OUTPUT: printTrelloCards(trelloCards)

orderedParentCards = orderCards(trelloCards)

#Go through ordered parent list, use associated cards in trelloCards
for card in orderedParentCards:
	addTrelloCard(card, trelloCards[card.FormattedID].tasks, backlogList)

#FINALISE
changeLog.close()

#Unit Testing using doctest  
if UNDER_DEVELOPMENT and __name__ == '__main__':
   	import doctest
   	doctest.testmod()