#integration_rally-trello

Experiments and working code for Rally/Trello integration.

rallyToTrelloMigration is currently an under development script to migrate all relevant Rally Artifacts to Trello.  So far it:-

 - builds a list of e-mails by comparing developer full names between Rally and Python. <i>(this is necessary as e-mails of users other than the one making requests are not</i>availiable in Trello) 
 - gets all Tasks from Rally that are not complete and are in the user list above
 - sorts tasks into Rally parent artifacts (Defects, User Stories)
 - figures out an order based on Rally DragAndDropOrder
 - adds each of the Rally parent artifacts as a Trello ticket with the Rally tasks as list items in Trello

#Plans

 Next step is to allow two way-syncing so that changes on one reflect on the other.  This raises the issue of HTML->Markdown and back.  html2text does the first step perfectly but I can't find anything to put it back the way it was, the HTML is always changed.

 Also
  - Servers, usernames, passwords all need to be passed in as arguments
  - Code needs to be cleaned and split up and possibly unit tests extended

#Issues

 pyral (1.1.1) doesn't support Python 3 and has an existing bug where retrieving a list of Rally users throws an error (which for some reason we get with every user once before it succeeds), I've added a fix for this on the pyral repo and <a href="https://github.com/RallyTools/RallyRestToolkitForPython/pull/70">submitted a pull request</a> but as it stands, a custom pyral install is required.
 The change is in <i>restapi.py</i> around line 575 where UserProfile is accessed

<code>
 	        if not mups:
 	            problem = "unable to find a matching UserProfile record for User: %s  UserProfile: %s"
                if hasattr(user, 'UserProfile'):
                    problem = problem % (user.DisplayName, user.UserProfile)
                warning("%s" % problem)
                continue
            else:
</code>

 another issue is that this script is Task-centric, meaning any artifact that has no corresponding tasks, wont be included.