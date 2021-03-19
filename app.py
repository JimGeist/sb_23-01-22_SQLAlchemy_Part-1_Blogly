"""Blogly application."""

from flask import Flask, request, redirect, render_template, redirect, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post
from datetime import datetime

app = Flask(__name__)

# Flask and SQL Alchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "SECRET!"
# debug = DebugToolbarExtension(app)

connect_db(app)


def change_occurred(from_vals, to_vals):
    """ compares lists of from and to values to ensure a change occurred """

    if (len(from_vals) == len(to_vals)):
        for fr, to in zip(from_vals, to_vals):
            if (fr != to):
                return True
        # all from and to values matched. NO change occurred
        return False
    else:
        # The lengths of the lists should match.
        # For now, return True
        return True


@app.route("/")
def blogly_home():
    """ Blogly Home Page """

    return redirect("/users")


@app.route("/users")
def list_users():
    """ Blogly Users w/ Add New User button """

    db_users = User.query.all()

    return render_template("list_users.html", users=db_users)


@app.route("/users/new")
def add_user_form():
    """ Blogly Add New User Form """

    return render_template("add_user.html")


@app.route("/users/new", methods=["POST"])
def add_user_process():
    """ Process Blogly Add New User Form """

    # extract form data, add, commit, then redirect to /users
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    image_url = request.form["image-url"]

    new_user = User(first_name=first_name.strip(),
                    last_name=last_name.strip(), image_url=image_url.strip())
    db.session.add(new_user)
    db.session.commit()
    return redirect("/users")


@app.route("/users/<int:user_id>")
def view_user(user_id):
    """ Show the details about a single Blogly user """

    db_user = User.query.get_or_404(user_id)
    # ??? do null values cause issues on the server side?
    # I see a lot of instances in the log where an incorrect
    # parameter is used by SQL Alchemy and they typically happen
    # on records with nulls.

    # ??? should put somthing in place to disable delete
    # when posts exist
    return render_template("view_user.html", user=db_user)


@app.route("/users/<int:user_id>/edit")
def edit_user(user_id):
    """ Edit the details about a single Blogly user """

    db_user = User.query.get_or_404(user_id)

    return render_template("edit_user.html", user=db_user)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user_process(user_id):
    """ Process the edit of a single Blogly user """

    # db_user = User.query.get_or_404(user_id)
    db_user = User.query.get(user_id)

    # extract form data, edit, commit, then redirect to /users
    f_name = request.form["first-name"].strip()
    l_name = request.form["last-name"].strip()
    url = request.form["image-url"].strip()

    if (change_occurred([db_user.first_name, db_user.last_name, db_user.image_url], [f_name, l_name, url])):
        db_user.first_name = f_name.strip()
        db_user.last_name = l_name.strip()
        db_user.image_url = url.strip()
        db.session.commit()

    return redirect(f"/users/{user_id}")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user_process(user_id):
    """ Process the delete of a single Blogly user """

    db_user = User.query.get_or_404(user_id)

    db.session.delete(db_user)
    db.session.commit()

    return redirect("/users")


@app.route("/posts/<int:post_id>")
def view_post(post_id):
    """ Show the information in a post """

    db_post = Post.query.get_or_404(post_id)
    full_name = db_post.user.get_full_name()
    created_date = datetime.strftime(
        db_post.created_at, "%a %b %d, %Y %I:%M %p").replace(" 0", " ")
    return render_template("view_post.html", post=db_post, user_full_name=full_name, created=created_date)


@app.route("/users/<int:user_id>/posts/new")
def add_post_form(user_id):
    """ Show form to add a post for user user_id. """
    user_data = {}
    user_data["id"] = user_id
    user_data["name"] = User.query.get(user_id).get_full_name()

    return render_template("add_post.html", user=user_data)


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def add_post_process(user_id):
    """ Process the add post form. The post is added and the user is
       redirected to the user detail page, /users/<user_id> """

    # extract form data, add post, commit, then redirect to /users
    post_title = request.form["post-title"]
    post_content = request.form["post-content"]

    new_post = Post(title=post_title.strip(),
                    content=post_content.strip(),
                    user_id=user_id)
    db.session.add(new_post)
    db.session.commit()
    return redirect(f"/users/{ user_id }")


@app.route("/posts/<int:post_id>/edit")
def edit_post(post_id):
    """ Edit the details in a single post """

    post_data = {"id": post_id}
    db_post = Post.query.get_or_404(post_id)
    post_data["title"] = db_post.title
    post_data["content"] = db_post.content
    post_data["user_id"] = db_post.user_id

    return render_template("edit_post.html", post=post_data)


@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post_process(post_id):
    """ Process the edit of a post. Return to users/<user_id> """

    # db_user = User.query.get_or_404(user_id)
    db_post = Post.query.get_or_404(post_id)

    user_id = db_post.user.id
    # extract form data, commit, then redirect to /users
    f_title = request.form["post-title"].strip()
    f_content = request.form["post-content"].strip()

    if (change_occurred([db_post.title, db_post.content], [f_title, f_content])):
        db_post.id = post_id
        db_post.title = f_title
        db_post.content = f_content
        db.session.commit()

    return redirect(f"/users/{user_id}")


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post_process(post_id):
    """ Process the delete of a single post """

    db_post = Post.query.get_or_404(post_id)
    user_id = db_post.user_id

    db.session.delete(db_post)
    db.session.commit()

    return redirect(f"/users/{user_id}")
