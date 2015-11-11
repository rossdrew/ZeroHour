import sys
import requests, trello, pyral #NOTE: pyral Doesn't support Python 3 and bug #40 is an issue
import csv
import getpass
import datetime				
import re
import html2text
import urllib

from pyral import Rally, rallyWorkset

UNDER_DEVELOPMENT = True
DEBUG_OUTPUT = True

options = [arg for arg in sys.argv[1:] if arg.startswith('--')]
args    = [arg for arg in sys.argv[1:] if arg not in options]

def parseCommandLineOptions(cmdLineOptions):
	"""Parse arguments into script constants
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
	requiredOptions = {'trelloID', 'trelloUser', 'trelloBoard', 'trelloList'}
	print 'Setting up Trello (trello v(0.9.1))...'
	if 'trelloToken' not in cmdLineOptions:
		url = trelloApi.get_token_url("Rally Integration") 
		print "ERROR: trelloToken required: Token URL: '{}'".format(url)
		sys.exit()

	if not requiredOptions.issubset(cmdLineOptions):
		print "ERROR: One of more of the required Trello options ({}) missing.".format(requiredOptions)
		sys.exit()

	trelloApi = trello.TrelloApi(cmdLineOptions['trelloID'])

	trelloApi.set_token(cmdLineOptions['trelloToken'])
	return trelloApi

def getTrelloBoard(trelloID, trelloToken, trelloUserName, boardName):
	"""Return a Trello Board object from Trello server"""
	boards = trello.Members(trelloID, trelloToken).get_board(trelloUserName)
	tBoards = [board for board in boards if board['name'] == boardName]
	if len(tBoards) < 1:
		print "ERROR: Trello board '{}' not found.".format(boardName)
		sys.exit()
	return tBoards[0]

def getTrelloList(trelloID, trelloToken, trelloBoard, trelloListName):
	"""Return a Trello List object from Trello server"""
	tLists = [list for list in trello.Boards(trelloID, trelloToken).get_list(trelloBoard['id']) if list['name'] == trelloListName]
	if len(tLists) < 1:
		print "ERROR: Trello list '{}' not found.".format(cmdLineOptions['trelloList'])
		sys.exit()
	tList = tLists[0]

def initRally(cmdLineOptions):
	requiredOptions = {'rallyServer','rallyUser','rallyPassword'}
	print 'Setting up Rally (pyral v{version})...'.format(version = pyral.__version__)
	if not requiredOptions.issubset(cmdLineOptions):
		print "ERROR: One of more of the required Rally options ({}) missing.".format(requiredOptions)
		sys.exit()
	return Rally(cmdLineOptions['rallyServer'], cmdLineOptions['rallyUser'], cmdLineOptions['rallyPassword'])

################################
#        Script Start          #
################################

cmdLineOptions = parseCommandLineOptions(options)

initTrello(cmdLineOptions)
tBoard = getTrelloBoard(cmdLineOptions['trelloID'], cmdLineOptions['trelloToken'], cmdLineOptions['trelloUser'], cmdLineOptions['trelloBoard'])
tList = getTrelloList(cmdLineOptions['trelloID'], cmdLineOptions['trelloToken'], tBoard, cmdLineOptions['trelloList'])

rally = initRally(cmdLineOptions)

print "Logging changes to change.log..."
changeLog = open("change.log", 'a')




#FINALIZE
changeLog.close()

#Unit Testing using doctest  
if UNDER_DEVELOPMENT and __name__ == '__main__':
   	import doctest
   	doctest.testmod()