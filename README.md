# sb_23-02-11_SQLAlchemy_Part-2_Blogly


## Assignment Details
Assignment involved adding the ability to create, view, edit, and delete posts. A model was created for the posts table and the templates and routes were created.

unittests were created for viewing a post, editing a post (the view portions of the form) and deleting a post. Test of the view user was expanded to check for the posts. 

Model.py was expanded to include add and edit functions. unittest cases **were not** built for any of the functions in model.py. I definitely see the benefit of moving the db-related portions of the adds and edits to their own functions because they can now get tested.


### ENHANCEMENTS
- refactored code by moving the add and edit database-specific tasks to model.py.
- post creation time displayed as Mon Mar 5, 2021 9:30 AM.
- flash messages added to display the result of a successful add and successful edit. Flash message will also indicate edits that were not necessary because no data changed.
- delete button is disabled when the user has posts.


### DIFFICULTIES 
Test cases -- for unknown reasons, deleting the post invalidated all the post tests that executed before the delete. Time was also lost with the setup functions because the tables are cleared and a user and post are added before each test (the user id for the post was hard coded as 1). The user id is not always 1.
