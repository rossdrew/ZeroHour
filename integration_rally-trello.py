import sys
import requests, trello, pyral #NOTE: pyral Doesn't support Python 3 and bug #40 is an issue
import csv
import getpass
import datetime				
import re
import html2text
import urllib

from pyral import Rally, rallyWorkset

RALLY_SERVER 	= ""
RALLY_USER 		= ""
RALLY_PASSWORD 	= ""

TRELLO_ID 	 	= "984edd6395e2c74b5a35ffec6400be0b"
TRELLO_BOARD 	= ""
TRELLO_LIST 	= ""
TRELLO_USER 	= ""
TRELLO_TOKEN 	= ""

options = [arg for arg in sys.argv[1:] if arg.startswith('--')]
args    = [arg for arg in sys.argv[1:] if arg not in options]

for option in options:
	parts = option[2:].split('=')
	optionName = parts[0]
	optionValue = parts[1]

	if optionName == 'rallyServer':
		RALLY_SERVER = optionValue
	elif optionName == 'rallyUser':
		RALLY_USER = optionValue
	elif optionName == 'rallyPassword':
		RALLY_PASSWORD = optionValue
	elif optionName == 'trelloServer':
		XTRELLO_SERVER= optionValue
	elif optionName == 'trelloUsername':
		TRELLO_USER = optionValue
	elif optionName == 'trelloBoard':
		TRELLO_BOARD = optionValuel
	elif optionName == 'trelloList':
		TRELLO_LIST = optionValuel


print "{} connecting to {}".format(RALLY_USER, RALLY_SERVER)