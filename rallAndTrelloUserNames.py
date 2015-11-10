import sys
import requests
import pyral 		# XXX Doesn't support Python 3 & requires custom coded pyral XXX
import trello

from pyral import Rally, rallyWorkset

#Rally Setup
RALLY_URI = ""
RALLY_USER = ""
RALLY_PASS = ""

rally = Rally(RALLY_URI, RALLY_USER, RALLY_PASS)
#############
#Trello Setup
DEBUG_OUTPUT = True
TRELLO_ID = ""
TRELLO_USER = ""
TRELLO_TOKEN = ""
TRELLO_BOARD 	= ""
TRELLO_LIST 	= ""

trelloApi = trello.TrelloApi(TRELLO_ID)
trelloApi.set_token(TRELLO_TOKEN)

boards = trello.Members(TRELLO_ID, TRELLO_TOKEN).get_board(TRELLO_USER)
testBoard = [board for board in boards if board['name'] == TRELLO_BOARD][0]
boardList = [list for list in trello.Boards(TRELLO_ID, TRELLO_TOKEN).get_list(testBoard['id']) if list['name'] == TRELLO_LIST][0]
#############

#Username (trello) <-- Full Name --> E-mail (rally)
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

for user in emailToUserName:
	print user
################################