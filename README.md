#integration_rally-trello

Experiments and working code for Rally/Trello integration.

rallyToTrelloMigration is currently an under development script to migrate all relevant Rally Artifacts to Trello.  So far it:-

 - builds a list of e-mails by comparing developer full names between Rally and Python. <i>(this is necessary as e-mails of users other than the one making requests are not</i>availiable in Trello) 
 - gets all Tasks from Rally that are not complete and are in the user list above
 - sorts tasks into Rally parent artifacts (Defects, User Stories)
 - figures out an order based on Rally DragAndDropOrder
 - adds each of the Rally parent artifacts as a Trello ticket with the Rally tasks as list items in Trello


#Issues

 pyral (1.1.1) doesn't support Python 3 and has an existing bug where retrieving a list of Rally users throws an error (which for some reason we get with every user once before it succeeds), I've added a fix for this on the pyral repo and <a href="https://github.com/RallyTools/RallyRestToolkitForPython/pull/70">submitted a pull request</a> but as it stands, a custom pyral install is required.
 The change is in <i>restapi.py</i> around line 575 where UserProfile is accessed

<code>
 	            if not mups:
                if hasattr(user, 'UserProfile'):
                    problem = problem % (user.DisplayName, user.UserProfile)
                warning("%s" % problem)
                continue
            else:
</code>