import csv, pyral, trello, getpass, requests, urllib
from urllib import quote_plus

DEBUG_OUTPUT = True
TRELLO_ID = "984edd6395e2c74b5a35ffec6400be0b"
print "Connecting to Trello (with ID '{}')...".format(TRELLO_ID)

trelloApi = trello.TrelloApi(TRELLO_ID)

TRELLO_USER = "r"
TRELLO_TOKEN = ""
TRELLO_BOARD 	= ""
TRELLO_LIST 	= ""

def get_token_url(app_name, expires='30days', write_access=True):
	return 'https://trello.com/1/authorize?key=%s&name=%s&expiration=%s&response_type=token&scope=%s' % (TRELLO_ID, quote_plus(app_name), expires, 'read,write,account' if write_access else 'read')

#Trello: Get token to use
#url = trelloApi.get_token_url("Rally Integration")  #Cant use this as additional scope (account) is needed to view e-mail
#url = get_token_url("Rally Integration") 
#print "Token URL: '{}'".format(url)
trelloApi.set_token(TRELLO_TOKEN)

boards = trello.Members(TRELLO_ID, TRELLO_TOKEN).get_board(TRELLO_USER)
testBoard = [board for board in boards if board['name'] == TRELLO_BOARD][0]
boardList = [list for list in trello.Boards(TRELLO_ID, TRELLO_TOKEN).get_list(testBoard['id']) if list['name'] == TRELLO_LIST][0]

##Get users?!?!
boardMembers = trello.Boards(TRELLO_ID, TRELLO_TOKEN).get_member(testBoard['id'])
##XXX I can only view my own trello e-mail
##Solution = Keep a hard coded list or derive e-mail from full name via Rally
for member in boardMembers:
	#print trello.Members(TRELLO_ID, TRELLO_TOKEN).get(member['id'])
	print "{} ({})".format(member['fullName'], member['username'])

#boards = trello.Members(TRELLO_ID, TRELLO_TOKEN).get_board(TRELLO_USER)
#backlogBoard = [board for board in boards if board['name'] == "Backlog"][0]
#backlogList = [list for list in trello.Boards(TRELLO_ID, TRELLO_TOKEN).get_list(backlogBoard['id']) if list['name'] == "Backlog"][0]

#class TrelloDebug():
#	"""Class for some simply Trello debug ouput"""
	#Get all the cards from everywhere!
#	def collectCards(self, withOutput):
#		cards = []
#		for board in boards:
#		    boardLists = trello.Boards(TRELLO_ID, TRELLO_TOKEN).get_list(board['id'])
#		    for boardList in boardLists:
#		    	cardsOnList = trello.Lists(TRELLO_ID, TRELLO_TOKEN).get_card(boardList['id'])
#		    	cards.extend(cardsOnList)
#		    	if withOutput:
#		    		print "Collecting {} cards from '{}'.'{}'".format(len(cardsOnList), board['name'], boardList['name'])
#		return cards;

	#Print out how many cards where found and their names and descriptions
#	def describeCards(self, cards):
#		print "{} cards found.  Printing listing...".format(len(cards))
#		for card in cards:
#			print "{}\n\t{}".format(card['name'], card['desc'])


#tDebug = TrelloDebug()
#cards = tDebug.collectCards(DEBUG_OUTPUT)
#tDebug.describeCards(cards
