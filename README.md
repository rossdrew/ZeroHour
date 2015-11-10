#integration_rally-trello

Experiments and working code for Rally/Trello integration.

rallyToTrelloMigration is currently an under development script to migrate all relevant Rally Artifacts to Trello.  So far it:-

 - builds a list of e-mails by comparing developer full names between Rally and Python. <i>(this is necessary as e-mails of users other than the one making requests are not</i>availiable in Trello) 
 - gets all Tasks from Rally that are not complete and are in the user list above
 - sorts tasks into Rally parent artifacts (Defects, User Stories)
 - figures out an order based on Rally DragAndDropOrder
 - adds each of the Rally parent artifacts as a Trello ticket with the Rally tasks as list items in Trello
