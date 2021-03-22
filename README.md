# sb_23-02-11_SQLAlchemy_Part-3_Blogly - Tags for Posts


## Assignment Details
Assignment involved adding the ability to create, view, edit, and delete tags. Post view, add, and edit forms and route were updated to support the adding and removing tags from posts. A model was created for the tags table and since tagging is a many-to-many operation, a posts_tags 'join' table was also created.

No new unittests were created for any of the tag routes or new functions. It is strictly a timing issue. 

Model.py was expanded to include delete functions for users, posts, and tags. 

Leaving this as Part3 in git / git hub instead of merging back into master.


### ENHANCEMENTS
- If anything, commits only occur on an edit when data has changed between the form and database.


### DIFFICULTIES 
Deleting from the posts_tags table. It took some iterations to get the delete logic working. I know I am missing something and found it frustrating because ```DELETE FROM posts_tags WHERE post_id = {post_id};``` would have been so much quicker and easier. Granted, I did make things complicated for myself (I don't know why) but I just could not type the code to delete all tags from a post during an edit when I knew some tags may get added back in and that started the whole add_tag and remove_tag lists boondoggle.
