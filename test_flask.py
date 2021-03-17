from unittest import TestCase

from app import app
from models import db, User

# Use a test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# Don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class BloglyTests(TestCase):
    """Tests for Blobly."""

    def setUp(self):
        """Add blogly user."""

        User.query.delete()

        new_user = User(first_name="Blogly Q.",
                        last_name="Testuser", image_url="")
        db.session.add(new_user)
        db.session.commit()

        self.user_id = new_user.id
        self.user = new_user

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_list_users(self):
        with app.test_client() as client:
            # a redirect will occur to /users
            resp = client.get("/", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Blogly Q. Testuser', html)
            self.assertIn('Add User', html)

    def test_view_users(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Blogly Q. Testuser', html)

            self.assertIn('Edit</button>', html)

            self.assertIn('Delete', html)

    def test_edit_user(self):
        with app.test_client() as client:
            # Even though it is an edit, the form has viewable elements
            #  about user.
            resp = client.get(f"/users/{self.user_id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('name="first-name"', html)

            self.assertIn('Blogly Q.', html)

            self.assertIn('name="last-name"', html)

            self.assertIn('Testuser', html)

            self.assertIn('name="image-url"', html)

            self.assertIn('Save', html)

            self.assertIn('Cancel', html)

    def test_delete_user_process(self):
        with app.test_client() as client:
            # Test the delete. We should redirect to an empty
            # users list.
            resp = client.post(
                f"/users/{self.user_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Blogly Users</h1>', html)
            self.assertIn('Add User', html)
            self.assertNotIn('Blogly Q. Testuser', html)
