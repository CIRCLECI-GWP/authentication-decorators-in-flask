"""Tests for User Authentication"""
import unittest
import json

from flask.testing import FlaskClient
from library.main import app, db
from config import app_config


def get_login_token(client: FlaskClient, user_details: str) -> str:
    """Method to get a login token."""
    user_register = client.post('/signup', data=user_details, content_type="application/json")
    assert user_register.status_code == 201, "User registration failed during token retrieval."

    user_login = client.post('/login', data=user_details, content_type="application/json")
    assert user_login.status_code == 201, "User login failed during token retrieval."

    token = json.loads(user_login.data.decode())
    return token['token']


class TestAuth(unittest.TestCase):
    """Test case for blueprint for authentication."""

    def setUp(self) -> None:
        """Set up the test client and database."""
        self.app = app
        self.app.config.from_object(app_config['testing'])
        self.client = self.app.test_client()
        self.user_details = json.dumps({
            'password': 'testing_p@ssword',
            'username': 'new_user'
        })

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_register_user(self) -> None:
        """Test a successful user registration."""
        user_register = self.client.post('/signup', data=self.user_details, content_type="application/json")
        result = json.loads(user_register.data)

        self.assertEqual(result['message'], "registered successfully")
        self.assertEqual(user_register.status_code, 201)

    def test_user_login(self) -> None:
        """Test a successful user login."""
        user_register = self.client.post('/signup', data=self.user_details, content_type="application/json")
        self.assertEqual(user_register.status_code, 201)

        user_login = self.client.post('/login', data=self.user_details, content_type="application/json")
        self.assertEqual(user_login.status_code, 201)

    def test_user_logged_in_user_can_get_books(self) -> None:
        """Test fetching books with a logged-in user."""
        login_token = get_login_token(self.client, self.user_details)
        headers = {
            'Content-Type': "application/json",
            'x-access-token': login_token
        }
        fetch_books = self.client.get('/bookapi/books', headers=headers)
        response = json.loads(fetch_books.data.decode())

        self.assertEqual(fetch_books.status_code, 200)
        self.assertEqual(response, {"Books": []})

    def test_user_without_valid_token_cannot_get_books(self) -> None:
        """Test fetching books with an invalid token."""
        headers = {
            'Content-Type': "application/json",
            'x-access-token': 'invalid-token'
        }
        fetch_books = self.client.get('/bookapi/books', headers=headers)
        response = json.loads(fetch_books.data.decode())

        self.assertEqual(fetch_books.status_code, 401)
        self.assertEqual(response['message'], 'Invalid token!')

    def test_user_logged_in_user_can_add_books(self) -> None:
        """Test adding books with a logged-in user."""
        login_token = get_login_token(self.client, self.user_details)
        headers = {
            'Content-Type': "application/json",
            'x-access-token': login_token
        }
        book_data = json.dumps({
            'title': 'New Book',
            'author': 'Author Name'
        })
        add_book = self.client.post('/bookapi/addbook', data=book_data, headers=headers)
        response = json.loads(add_book.data.decode())

        self.assertEqual(add_book.status_code, 200)
        self.assertEqual(response['message'], 'new book created')