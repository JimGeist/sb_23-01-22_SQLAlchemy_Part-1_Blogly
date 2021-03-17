# sb_23-01-22_SQLAlchemy_Part-1_Blogly


## Assignment Details
Assignment involved creation of Blogly, a blogger application with Flask, Python, PostgreSQL, and SQL Alchemy. This portion of the assignment consisted of the User - pages to list users, add a new user, view an individual user, edit a user with server routes to support listing, adding, editing, viewing and deleting a user.

unittests were created for listing users, viewing an individual user, editing a user (the view portions of the form), and deleting a user.


### DIFFICULTIES 
Multiple buttons on a page when only one button is tied to a form action, form defaulting to a get even though a post was needed, weird SQL Alchemy cases where the image url was not populated, then when a value was provided in an edit, SQL Alchemy was using the value for the image_url as the id . . but somehow the edit still occurred. And the delete video should be deleted. The approach and explanation Colt offered were weak and the video presentation felt rushed.

I also found it odd to have a model of the database table in a program that deviates from the actual database schema. The video had an example of a default value for hunger = 20 getting applied by SQL Alchemy -- and it is enforced by SQL Alchemy not the database. The default value is not part of the table description when you view the table in PostgreSQL. 

I understand the concept of SQL Alchemy, but right now, I prefer writing the SQL and am not seeing the benefit of the abstraction SQL Alchemy provides.
