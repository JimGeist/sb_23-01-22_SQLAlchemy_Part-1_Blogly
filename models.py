"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy, time
import flask_sqlalchemy

# flask_sqlalchemy.time.gmtime()
# time.struct_time(tm_year=2021, tm_mon=3, tm_mday=18, tm_hour=23, tm_min=32, tm_sec=20, tm_wday=3, tm_yday=77, tm_isdst=0)
# datetime.strptime(
#                 cookie_data_out["date_last_activity"], "%Y-%m-%d %H:%M:%S.%f")

db = SQLAlchemy()


def connect_db(app):
    """ Associate the flask application app with SQL Alchemy and 
        initialize SQL Alchemy
    """
    db.app = app
    db.init_app(app)


# MODELS
class User(db.Model):
    """ User model for blobly users table  """

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


class Post(db.Model):
    """ User model for blobly users table  """

    __tablename__ = 'posts'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    title = db.Column(db.String(128),
                      nullable=False)

    content = db.Column(db.Text,
                        nullable=False)

    created_at = db.Column(db.DateTime(timezone=True),
                           default=time.strftime("%Y-%m-%d %H:%M:%S %z"),
                           nullable=False)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'))

    user = db.relationship('User', backref='posts')

    def __repr__(self):
        """Show post information """

        return f"<Blogly #{self.id} title: '{self.title}' content: '{self.content}' created_at: {self.created_at} >"
