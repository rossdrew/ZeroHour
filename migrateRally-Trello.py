import ZeroHour as zerohour
import sys

options = [arg for arg in sys.argv[1:] if arg.startswith('--')]
args    = [arg for arg in sys.argv[1:] if arg not in options]

cmdLineOptions = zerohour.parseCommandLineOptions(options)

zerohour.initTrello(cmdLineOptions)
tBoard = zerohour.getTrelloBoard(cmdLineOptions['trelloID'], cmdLineOptions['trelloToken'], cmdLineOptions['trelloUser'], cmdLineOptions['trelloBoard'])
tList = zerohour.getTrelloList(cmdLineOptions['trelloID'], cmdLineOptions['trelloToken'], tBoard, cmdLineOptions['trelloList'])

rally = zerohour.initRally(cmdLineOptions)

print "Logging changes to change.log..."
changeLog = open("change.log", 'a')

#artifactQuery = zerohour.buildRallyArtifactInclusionQuery(rally, cmdLineOptions['trelloID'], cmdLineOptions['trelloToken'], tBoard)
#tasksForMigration = zerohour.getRallyRallyArtifactList(rally, artifactQuery, 'migration.list')
#trelloCards = zerohour.sortTrelloTasksIntoArtifacts(rally, tasksForMigration)
#orderedParentCards = zerohour.orderCards(rally, trelloCards)
#zerohour.addTrelloCards(orderedParentCards, trelloCards, cmdLineOptions['trelloID'], cmdLineOptions['trelloToken'], tList, changeLog)

zerohour.syncRallyAndPython(rally, cmdLineOptions['trelloID'], cmdLineOptions['trelloToken'], tBoard)

#FINALIZE
changeLog.close()