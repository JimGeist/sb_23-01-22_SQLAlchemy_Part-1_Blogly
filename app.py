"""Blogly application."""

from flask import Flask, request, redirect, render_template, redirect, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag
from models import db_add_user, db_edit_user, db_delete_user
from models import db_add_post, db_edit_post, db_delete_post
from models import db_add_tag, db_edit_tag, db_delete_tag, db_get_all_tags
from datetime import datetime

app = Flask(__name__)

# Flask and SQL Alchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "SECRET!"
# debug = DebugToolbarExtension(app)

connect_db(app)


@app.route("/")
def blogly_home():
    """ Blogly Home Page """

    return redirect("/users")


#
# USER-RELATED ROUTES
#

@app.route("/users")
def list_users():
    """ Blogly Users w/ Add New User button """

    db_users = User.query.all()

    return render_template("list_users.html", headline="Blogly Users", users=db_users)


@app.route("/users/new")
def add_user_form():
    """ Blogly Add New User Form """

    return render_template("add_user.html", headline="Add New Blogly User")


@app.route("/users/new", methods=["POST"])
def add_user_process():
    """ Process Blogly Add New User Form """

    # extract form data, add, commit, then redirect to /users
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    image_url = request.form["image-url"]

    msg = db_add_user(first_name, last_name, image_url)

    flash(msg["text"], msg["severity"])

    return redirect("/users")


@app.route("/users/<int:user_id>")
def view_user(user_id):
    """ Show the details about a single Blogly user """

    db_user = User.query.get_or_404(user_id)
    # ??? do null values cause issues on the server side?
    # I see a lot of instances in the log where an incorrect
    # parameter is used by SQL Alchemy and they typically happen
    # on records with nulls.

    # allow_delete = True if len(db_user.posts) == 0 else False
    disable_delete = "" if len(db_user.posts) == 0 else "disabled "
    return render_template("view_user.html", headline="Blogly User",
                           user=db_user, disable_delete=disable_delete)


@app.route("/users/<int:user_id>/edit")
def edit_user(user_id):
    """ Edit the details about a single Blogly user """

    db_user = User.query.get_or_404(user_id)

    return render_template("edit_user.html",
                           headline=f"Edit Blogly {db_user.get_full_name()}",
                           user=db_user)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user_process(user_id):
    """ Process the edit of a single Blogly user """

    # extract form data, edit, commit, then redirect to /users
    first_name = request.form["first-name"].strip()
    last_name = request.form["last-name"].strip()
    image_url = request.form["image-url"].strip()

    msg = db_edit_user(user_id, first_name, last_name, image_url)

    flash(msg["text"], msg["severity"])

    return redirect(f"/users/{user_id}")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user_process(user_id):
    """ Process the delete of a single Blogly user """

    msg = db_delete_user(user_id)

    flash(msg["text"], msg["severity"])

    return redirect("/users")


#
# POST-RELATED ROUTES
#

@app.route("/posts/<int:post_id>")
def view_post(post_id):
    """ Show the information in a post """

    db_post = Post.query.get_or_404(post_id)
    full_name = db_post.user.get_full_name()
    created_date = datetime.strftime(
        db_post.created_at, "%a %b %d, %Y %I:%M %p").replace(" 0", " ")
    db_tags = db_post.tags
    return render_template("view_post.html",
                           headline=db_post.title,
                           post=db_post, user_full_name=full_name, created=created_date, tags=db_tags)


@app.route("/users/<int:user_id>/posts/new")
def add_post_form(user_id):
    """ Show form to add a post for user user_id. """
    user_data = {}
    user_data["id"] = user_id
    user_data["name"] = User.query.get(user_id).get_full_name()

    db_tags = Tag.query.all()
    return render_template("add_post.html", headline=f"Add Post for { user_data['name'] }",
                           user=user_data, tags=db_tags)


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def add_post_process(user_id):
    """ Process the add post form. The post is added and the user is
       redirected to the user detail page, /users/<user_id> """

    post_title = request.form["post-title"]
    post_content = request.form["post-content"]

    formkeys = request.form.keys()
    keys = list(formkeys)

    msg = db_add_post(post_title, post_content, keys, user_id)

    flash(msg["text"], msg["severity"])

    return redirect(f"/users/{ user_id }")


@app.route("/posts/<int:post_id>/edit")
def edit_post(post_id):
    """ Edit the details in a single post """

    post_data = {"id": post_id}
    db_post = Post.query.get_or_404(post_id)
    post_data["title"] = db_post.title
    post_data["content"] = db_post.content
    post_data["user_id"] = db_post.user_id

    # db_get_all_tags returns the following list:
    # [
    #     {   id:      < id for the tag >,
    #         name:    < name of the tag >,
    #         checked: < 'checked' when found on post, otherwise '' >
    #     }, ...
    # ]
    # The list includes all tags. checked is set to checked when the tag
    #  is on post_id.
    tag_usage = db_get_all_tags(post_id)

    return render_template("edit_post.html",
                           headline=f"Edit Post '{ post_data['title'] }'",
                           post=post_data,
                           tags=tag_usage)


@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post_process(post_id):
    """ Process the edit of a post. Return to users/<user_id> """

    # extract form data, extract key values (keys have the tags),
    #  then redirect to /users
    f_title = request.form["post-title"].strip()
    f_content = request.form["post-content"].strip()

    formkeys = request.form.keys()
    keys = list(formkeys)

    # msg will also include a field for the user_id for routing.
    msg = db_edit_post(post_id, f_title, f_content, keys)

    flash(msg["text"], msg["severity"])

    return redirect(f"/users/{msg['user_id']}")


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post_process(post_id):
    """ Process the delete of a single post """

    # db_post = Post.query.get_or_404(post_id)
    # user_id = db_post.user_id

    # db.session.delete(db_post)
    # db.session.commit()

    # msg will also include a field for the user_id for routing.
    msg = db_delete_post(post_id)

    flash(msg["text"], msg["severity"])

    # Use /users route when we have an 'error', otherwise use /users/{user_id}
    if (msg["severity"] == "error"):
        return redirect("/users")
    else:
        return redirect(f"/users/{msg['user_id']}")


#
# TAG-RELATED ROUTES
#

@app.route("/tags")
def list_tags():
    """ Lists all tags, with links to the tag detail page. 
        Page includes a button to Add Tag
    """

    db_tags = Tag.query.all()

    return render_template("list_tags.html", headline="Tags", tags=db_tags)


@app.route("/tags/<int:tag_id>")
def view_tag(tag_id):
    """ Show the posts tagged with the tag. The listed posts will link to the view for a post.
        Page includes buttons to edit and delete the tag. 
    """

    db_tag = Tag.query.get_or_404(tag_id)
    # find the posts using the tag
    db_posts = db_tag.posts
    return render_template("view_tag.html",
                           headline=db_tag.name,
                           tag_id=db_tag.id,
                           posts=db_posts)


@app.route("/tags/new")
def add_tag_form():
    """ Show form to add a new tag. """

    return render_template("add_tag.html", headline="Add a tag")


@app.route("/tags/new", methods=["POST"])
def add_tag_process():
    """ Process the add tag form. The new tag is added and the user is
       redirected to the tags list """

    # extract form data, call function to add tag, handle messaging,
    #  then redirect to /tags
    tag_name = request.form["tag-name"]

    msg = db_add_tag(tag_name)

    flash(msg["text"], msg["severity"])

    return redirect(f"/tags")


@app.route("/tags/<int:tag_id>/edit")
def edit_tag(tag_id):
    """ Edit a tag """

    tag_data = {"id": tag_id}
    db_tag = Tag.query.get_or_404(tag_id)
    tag_data["name"] = db_tag.name

    return render_template("edit_tag.html", headline=f"Edit '{ tag_data['name'] }' tag", tag=tag_data)


@app.route("/tags/<int:tag_id>/edit", methods=["POST"])
def edit_tag_process(tag_id):
    """ Process the edit of a tag. Return to /tags """

    # extract form data, process edit, then redirect to /tags
    f_name = request.form["tag-name"].strip()

    msg = db_edit_tag(tag_id, f_name)

    flash(msg["text"], msg["severity"])

    return redirect("/tags")


@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag_process(tag_id):
    """ Process the delete of a single tag """

    msg = db_delete_tag(tag_id)

    flash(msg["text"], msg["severity"])

    return redirect("/tags")
