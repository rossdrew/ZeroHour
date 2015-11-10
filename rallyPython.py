import sys
import requests
import pyral 		# XXX Doesn't support Python 3 XXX
import trello

from pyral import Rally, rallyWorkset

DEBUG_OUTPUT = True
LOG_OUTPUT = False

RALLY_URI = ""
RALLY_USER = ""
RALLY_PASS = ""

print 'Testing pyral v{version}...'.format(version = pyral.__version__)

options = [arg for arg in sys.argv[1:] if arg.startswith('--')]
args    = [arg for arg in sys.argv[1:] if arg not in options]

print 'Connecting to Rally...'
#(1) Connect via command line arguments
#server, user, password, apikey, workspace, project = rallyWorkset(options)   #--> config.py
#rally = Rally(server, user, password, workspace=workspace, project=project)

#(2) Connect via hard coded values
rally = Rally(RALLY_URI, RALLY_USER, RALLY_PASS)
print "OK!"

if LOG_OUTPUT:
	rally.enableLogging()

subscriptionName = rally.subscriptionName()
workspace = rally.getWorkspace()
print 'Subscribed to \'{}\', Workspace: {}'.format(subscriptionName, workspace.Name)

class RallyDebug():
	"""Class for some simply Rally debug ouput"""
	#Show a list of projects
	def listProjects(self):
		for pr in rally.getProjects():
 			print "{} ({})".format(pr.Name, pr.oid)

 	#Show a list of workspaces
 	def listWorkspaces(self):
		for ws in rally.getWorkspaces():
 			print "{} ({})".format(ws.Name, ws.oid)

 	#Show a heirachical list of projects and workspaces
 	def listAll(self):
 		workspaces = rally.getWorkspaces()
		for wksp in workspaces:
		    print "%s %s" % (wksp.oid, wksp.Name)
		    projects = rally.getProjects(workspace=wksp.Name)
		    for proj in projects:
		        print "\t%12.12s  %s" % (proj.oid, proj.Name)


rallyDebug = RallyDebug()

#Rally: Project Details
#print rally.getProject('AmFam PL Phase 2').details()


#TODO Get user e-mail from first and last name


all_users = rally.getAllUsers()

for user in all_users:
	print "{} {}, {}".format(user.FirstName, user.LastName, user.EmailAddress)
# 	print user.Name
	# tz   = user.UserProfile.TimeZone or 'default'
	# role = user.Role or '-No Role-'
	# values = (int(user.oid), user.Name, user.UserName, role, tz)
	# print("%12.12d %-24.24s %-30.30s %-12.12s" % values)


#Rally : Get all artifacts that are not closed
#migrationList = open('migration.list', 'w')
#openArtifacts = []
#What will we be using from Rally.ARTIFACT_TYPE.values()? ['Story','Story','Defect','DefectSuite','Task','TestCase','TestSet','PortfolioItem']
#for artifactType in ['Defect', 'Story']: 
#	response = rally.get(artifactType, fetch="FormattedID", query='State != Closed')
#	print "{} {}s found".format(response.resultCount, artifactType)	
#	for story in response:
#		openArtifacts.append(story.FormattedID)
#		migrationList.write("{}\n".format(story.FormattedID))#TODO just the ID
#		if DEBUG_OUTPUT:
#			print "Added {}...".format(story.FormattedID)
#	
#print "{} TOTAL stories added ".format(len(openArtifacts))

#response = rally.get('Defect', fetch=fields, query=criterion, order="FormattedID", spagesize=200, limit=400)
#print response.resultCount, "qualifying {}".format(Rally.ARTIFACT_TYPE)

##Finalize
#migrationList.close()