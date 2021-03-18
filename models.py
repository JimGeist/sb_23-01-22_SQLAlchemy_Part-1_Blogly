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

    # last_name is nullable -- Cher, Prince, Beyoncé
    last_name = db.Column(db.String(25),
                          nullable=True)

    image_url = db.Column(db.Text,
                          nullable=True)

    def __repr__(self):
        """Show info about user."""

        return f"<Blogly #{self.id} {self.first_name} {self.last_name} image url: {self.image_url} >"

    def get_full_name(self):
        """Get the full name """
        full_name = f"{self.first_name} {self.last_name}"

        return full_name.strip()
