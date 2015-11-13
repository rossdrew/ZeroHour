#ZeroHour

Experiments and working code for Rally/Trello integration.  Functions include:-

 - Check which users exist on Rally and Trello
 - Getting Tasks and Artifacts from Rally and sorting into objects.
 - Converting HTML in Rally descriptions to Markdown for Trello
 - Extracting defect type from Rally ID
 - Extracting Rally ID from Trello Ticket title
 - Ordering Rally Artifacts by DragAndDropOrder

#migrateRally-Trello.py

  Script to migrate all relevant Rally Artifacts to Trello.  So far it:-

 - builds a list of e-mails by comparing developer full names between Rally and Python. <i>(this is necessary as e-mails of users other than the one making requests are not</i>availiable in Trello) 
 - gets all Tasks from Rally that are not complete and are in the user list above
 - sorts tasks into Rally parent artifacts (Defects, User Stories)
 - figures out an order based on Rally DragAndDropOrder
 - adds each of the Rally parent artifacts as a Trello ticket with the Rally tasks as list items in Trello

#synch_RallyToTrello.py

 Script to synch Rally Artifacts with Trello Tickets.  So far it:-

 - Gets list of Rally artifacts and sub-Tasks
 - Gets a list of Trello tickets
 - Checks which Artifacts/Tickets exist in both and which only exist in one or the other

#Plans

 Create a ZeroHour class to hold config details.

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