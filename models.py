"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy, time
from sqlalchemy.exc import IntegrityError


db = SQLAlchemy()


def connect_db(app):
    """ Associate the flask application app with SQL Alchemy and
        initialize SQL Alchemy
    """
    db.app = app
    db.init_app(app)


# MODELS

class Tag(db.Model):
    """ Tag model for blogly tags table. There is a many to many relationship
        between tags and posts.
    """

    __tablename__ = 'tags'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    name = db.Column(db.String(64),
                     nullable=False,
                     unique=True)

    def __repr__(self):
        """Show tag information """

        return f"<Tag #{self.id} {self.name} >"


class PostTag(db.Model):
    """ PostTag model for blogly Posts_Tags table. Posts_Tags table connects the posts to the
        tags.
    """

    __tablename__ = 'posts_tags'

    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.id'),
                        primary_key=True)

    tag_id = db.Column(db.Integer,
                       db.ForeignKey('tags.id'),
                       primary_key=True)


class User(db.Model):
    """ User model for blogly users table  """

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

        return f"<User #{self.id} {self.first_name} {self.last_name} image url: {self.image_url} >"

    def get_full_name(self):
        """Get the full name """
        full_name = f"{self.first_name} {self.last_name}"

        return full_name.strip()


class Post(db.Model):
    """ User model for blogly users table  """

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

    # through relationship to tags and backref posts
    tags = db.relationship('Tag',
                           secondary='posts_tags',
                           backref='posts')

    def __repr__(self):
        """Show post information """

        return f"<Post #{self.id} title: '{self.title}' content: '{self.content}' created_at: {self.created_at} >"


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


def db_add_user(first_name, last_name, image_url):
    """ adds a user to the users table """

    msg = {}

    new_user = User(first_name=first_name.strip(),
                    last_name=last_name.strip(), image_url=image_url.strip())

    db.session.add(new_user)
    db.session.commit()

    msg["text"] = f"{new_user.get_full_name()} created."
    msg["severity"] = "okay"

    return msg


def db_add_post(title, content, keys, user_id):
    """ adds a post with title = title and content = content to the posts table.
        When keys contains values appended with tag-xx, the tag with id xx is 
        attached to the post.
    """

    msg = {}

    new_post = Post(title=title.strip(),
                    content=content.strip(),
                    user_id=user_id)

    db.session.add(new_post)
    db.session.commit()

    tag_list = []
    # handle the tags
    for key in keys:
        if (key.startswith("tag-")):
            tag_id = key.replace("tag-", "")
            # whisky-face time!
            tag_to_add = Tag.query.get(tag_id)
            new_post.tags.append(tag_to_add)
            db.session.add(new_post)
            db.session.commit()
            tag_list.append(str(tag_to_add.name))

    if (len(tag_list) > 0):
        if (len(tag_list) == 1):
            msg["text"] = f"Post'{new_post.title}' with tag '{ tag_list[0] }' created."
        else:
            msg["text"] = f"Post'{new_post.title}' with tags { str(tag_list).replace('[', '').replace(']','') } created."

    else:
        # post did not have tags.
        msg["text"] = f"Post '{ new_post.title }' created."

    msg["severity"] = "okay"

    return msg


def db_add_tag(tag_name):
    """ adds a tag to the tags table """

    msg = {}

    new_tag = Tag(name=tag_name.strip())

    db.session.add(new_tag)

    try:
        db.session.commit()
        msg["text"] = f"{new_tag.name} created."
        msg["severity"] = "okay"

    except IntegrityError:
        db.session.rollback()
        msg["text"] = f"'{new_tag.name}' tag was NOT created - '{new_tag.name}' already exists."
        msg["severity"] = "error"

    return msg


def db_edit_user(id, first_name, last_name, image_url):
    """ Updates the user when changes have occurred """

    db_user = User.query.get_or_404(id)

    msg = {}

    if (change_occurred([db_user.first_name, db_user.last_name, db_user.image_url],
                        [first_name, last_name, image_url])):

        db_user.first_name = first_name
        db_user.last_name = last_name
        db_user.image_url = image_url

        db.session.commit()

        msg["text"] = f"{db_user.get_full_name()} successfully updated."
        msg["severity"] = "okay"

    else:
        msg["text"] = f"There were no changes!"
        msg["severity"] = "warning"

    return msg


def db_edit_post(post_id, title, content, keys):
    """ Updates the post when changes have occurred """

    db_post = Post.query.get_or_404(post_id)
    user_id = db_post.user.id

    # msg needs to include the user_id for proper routing
    msg = {"user_id": user_id}

    # compare tags to see whether a change occurred
    tags_check = have_tags_changed(post_id, keys)

    if (change_occurred([db_post.title, db_post.content], [title, content])):

        db_post.title = title
        db_post.content = content

        db.session.commit()

        msg["text"] = f"{db_post.title} successfully updated. "
        msg["severity"] = "okay"
        post_text_changed = True
    else:
        post_text_changed = False
        msg["text"] = "There were no changes! "
        msg["severity"] = "warning"

    if (tags_check["tags_changed"]):
        # get the tags for the post
        # remove (delete) any tag on the post that is not in the form list

        # any tags to remove from post?
        if (len(tags_check["remove_tags"]) > 0):
            remove_tags_objs = PostTag.query.filter(
                PostTag.post_id == post_id, PostTag.tag_id.in_(tags_check["remove_tags"])).all()
            for idx in range(len(remove_tags_objs)):
                db.session.delete(remove_tags_objs[idx])

            db.session.commit()

            if (idx == 0):
                msg["text"] = f"{msg['text']}Removed 1 tag from post. "
            else:
                msg["text"] = f"{msg['text']}Removed {idx + 1} tags from post. "

        if (len(tags_check["add_tags"]) > 0):
            for tag in tags_check["add_tags"]:
                add_tag = PostTag(post_id=post_id, tag_id=tag)
                db.session.add(add_tag)
                db.session.commit()

            if (len(tags_check['add_tags']) == 1):
                msg["text"] = f"{msg['text']}Added 1 tag to post. "
            else:
                msg["text"] = f"{msg['text']}Added {len(tags_check['add_tags'])} tags to post. "

        # handle messaging
        msg_temp = (msg['text']).replace("There were no changes! ", "")
        msg["text"] = msg_temp
        msg["severity"] = "okay"

    return msg


def db_edit_tag(tag_id, name):
    """ Updates the tag identified by tag_id when changes have occurred """

    db_tag = Tag.query.get_or_404(tag_id)

    msg = {}

    if (change_occurred([db_tag.name], [name])):

        db_tag.name = name

        try:
            db.session.commit()

            msg["text"] = f"{db_tag.name} successfully updated."
            msg["severity"] = "okay"

        except IntegrityError:
            db.session.rollback()
            msg["text"] = f"'{db_tag.name}' was NOT changed - '{name}' already exists."
            msg["severity"] = "error"

    else:
        msg["text"] = f"There were no changes!"
        msg["severity"] = "warning"

    return msg


def db_delete_user(user_id):
    """ Delete a single user from the users table. """

    db_user = User.query.get(user_id)

    if (db_user == None):
        # user_id does not exist
        msg = {"text": "The Blogly user was not found and was not deleted."}
        msg["severity"] = "error"
    else:
        # the user was found. Delete the user.
        user_name = db_user.get_full_name()
        db.session.delete(db_user)
        db.session.commit()
        msg = {"text": f"User '{user_name}' was deleted."}
        msg["severity"] = "okay"

    return msg


def db_delete_post(post_id):
    """ Delete a single post from the posts table and any references to the post from 
        the posts-tags table. 
    """

    db_post = Post.query.get(post_id)
    if (db_post == None):
        # post_id does not exist
        msg = {"text": "The post was not found and was not deleted."}
        msg["severity"] = "error"
    else:
        user_id = db_post.user.id

        # msg needs to include the user_id for proper routing
        msg = {"user_id": user_id}

        # delete any tags to this post. Relationship was created without cascading delete.
        remove_tags_objs = PostTag.query.filter(
            PostTag.post_id == post_id).all()
        if (len(remove_tags_objs) > 0):
            for idx in range(len(remove_tags_objs)):
                db.session.delete(remove_tags_objs[idx])

            db.session.commit()

        # Delete the post.
        post_title = db_post.title
        db.session.delete(db_post)
        db.session.commit()
        msg["text"] = f"Post '{post_title}' was deleted."
        msg["severity"] = "okay"

    return msg


def db_delete_tag(tag_id):
    """ Delete a single tag from the tags table. """

    db_tag = Tag.query.get(tag_id)

    if (db_tag == None):
        # tag_id does not exist
        msg = {"text": "The tag was not found and was not deleted."}
        msg["severity"] = "error"
    else:
        # the tag was found. Delete the tag.
        tag_name = db_tag.name
        db.session.delete(db_tag)
        db.session.commit()
        msg = {"text": f"Tag '{tag_name}' was deleted."}
        msg["severity"] = "okay"

    return msg


def db_get_all_tags(post_id):
    """ Gets all the tags from the tags table. Mark the tag as checked 
        when it exists on post_id.
        Returns the following list:
        (
            {   id:      < id for the tag >
                name:    < name of the tag >
                checked: < 'checked' when found on post, otherwise '' >
            }, ...
        )
    """

    tags_out = []
    tags_temp = {}

    # build a dictionary WITH tag_id as a key with the values.
    db_tags = Tag.query.all()
    for tag in db_tags:
        tags_temp[tag.id] = {
            "id": tag.id,
            "name": tag.name,
            "checked": ""
        }

    post_tags = Post.query.get(post_id).tags
    if (len(post_tags) > 0):
        # using the id from a tag on the post, set "checked" where appropriate in tags_temp
        for p_tag in post_tags:
            tags_temp[p_tag.id]["checked"] = "checked"

    # values in tags_temp are added to list tags_out
    for key in tags_temp.keys():
        tags_out.append(tags_temp[key])

    # print(f"\n\ndb_get_all_tags: post_tags: {post_tags}", flush=True)
    # print(f"\n\n    tags_out: {tags_out}\n", flush=True)

    return tags_out


def have_tags_changed(post_id, keys):
    """ Compares the db tags and the form tags (in 'keys')
        to see if a tag change occurred.
        Returns a dictionary:
        {
            tags_changed: < True when the tags have changed, otherwise False >,
            remove_tags: < when tags_changed is true, remove_tags has a list of tag ids, 
                if any, that require removal from the post. List is empty, [], when there
                are no tags to remove. remove_tags key and list do not exist when 
                tags_changed is False (no tag changes) >
            add_tags: < when tags_changed is true, add_tags has a list of tag ids, 
                if any, that need to get added to a post. The list is empty, [], when there
                are no tags to add to the post. add_tags key and list do not exist when
                tags_changed is False (no tag changes) >
        }
    """

    # pull the tag ids out of keys from the form
    tags_form = []
    for key in keys:
        if (key.startswith("tag-")):
            tags_form.append(int(key.replace("tag-", "")))

    # pull the tag ids from the db post tags
    tags_db = []
    post_tags = Post.query.get(post_id).tags
    for p_tag in post_tags:
        tags_db.append(p_tag.id)

    # made sets of tags_db and tags_form
    db_tag_set = set(tags_db)
    form_tag_set = set(tags_form)

    remove_tags = db_tag_set - form_tag_set
    add_tags = form_tag_set - db_tag_set

    if ((len(remove_tags) > 0) or (len(add_tags) > 0)):
        # we have changes
        results = {"tags_changed": True}
        results["remove_tags"] = list(remove_tags)
        results["add_tags"] = list(add_tags)
    else:
        results = {"tags_changed": False}

    return results
