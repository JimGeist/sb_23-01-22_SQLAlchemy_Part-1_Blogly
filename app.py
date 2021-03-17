"""Blogly application."""

from flask import Flask, request, redirect, render_template, redirect, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)

# Flask and SQL Alchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "SECRET!"
# debug = DebugToolbarExtension(app)

connect_db(app)

# once you have a design, you no longer need to call db.create_all()
# db.create_all()


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

    return render_template("users.html", users=db_users)


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


@app.route("/users/<user_id>")
def view_user(user_id):
    """ Show the details about a single Blogly user """

    db_user = User.query.get_or_404(user_id)

    return render_template("view_user.html", user=db_user)


@app.route("/users/<user_id>/edit")
def edit_user(user_id):
    """ Edit the details about a single Blogly user """

    db_user = User.query.get_or_404(user_id)

    return render_template("edit_user.html", user=db_user)


@app.route("/users/<user_id>/edit", methods=["POST"])
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


@app.route("/users/<user_id>/delete", methods=["POST"])
def delete_user_process(user_id):
    """ Process the delete of a single Blogly user """

    db_user = User.query.get_or_404(user_id)

    db.session.delete(db_user)
    db.session.commit()

    return redirect("/users")
