"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """ Associate the flask application app with SQL Alchemy and 
        initialize SQL Alchemy
    """
    db.app = app
    db.init_app(app)


# MODELS
class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    first_name = db.Column(db.String(25),
                           nullable=False)

    last_name = db.Column(db.String(25),
                          nullable=True)

    image_url = db.Column(db.Text,
                          nullable=True)

    def __repr__(self):
        """Show info about user."""

        return f"<Blogly User#{self.id} first name: {self.first_name} last name: {self.last_name} image url: {self.image_url} >"
