import os
import unittest
import pathlib
from flask import session
from dotenv import load_dotenv

from author.models import Author
from application import db
from application import create_app as create_app_base
from utils.test_db import TestDB

env_dir = pathlib.Path(__file__).parents[1]
load_dotenv(os.path.join(env_dir, '.flaskenv'))

wrong_password = 'test456'
login_error = 'Incorrect email or password.'


class AuthorTest(unittest.TestCase):
    def create_app(self):
        return create_app_base(
            SQLALCHEMY_DATABASE_URI=self.db_uri,
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY='Testing Secret'
        )

    def setUp(self):
        self.test_db = TestDB()
        self.db_uri = self.test_db.create_db()
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client()
        self.data = AuthorTest.user_dict()
        with self.app_factory.app_context():
            db.create_all()

    def tearDown(self):
        with self.app_factory.app_context():
            db.drop_all()
        self.test_db.drop_db()

    @staticmethod
    def user_dict():
        return dict(
            full_name='John Doe',
            email='jdoe@example.com',
            password='test123',
            confirm_password='test123'
        )

    def register_standard(self, context=None):
        context = context if context is not None else self.app
        return context.post('/register', data=self.data, follow_redirects=True)

    def login_standard(self, context=None):
        context = context if context is not None else self.app
        return context.post('/login', data=self.data, follow_redirects=True)

    def test_user_registration_feedback(self):
        rv = self.register_standard()
        assert 'You are now registered' in str(rv.data)

    def test_user_registration_database_record(self):
        with self.app as context:
            rv = self.register_standard(context)
            assert Author.query.filter_by(email=self.data['email']).count() == 1

    def test_user_registration_duplicate_email(self):
        self.register_standard()
        rv = self.register_standard()
        assert f"{self.data['email']} is already in use." in str(rv.data)

    def test_user_registration_passwords_do_not_match(self):
        self.data['confirm_password'] = wrong_password
        rv = self.register_standard()
        assert 'Passwords must match.' in str(rv.data)

    def test_user_login_session(self):
        self.register_standard()
        with self.app as context:
            self.login_standard(context)
            assert session['id'] == 1

    def test_user_login_wrong_password(self):
        self.register_standard()
        self.data['password'] = wrong_password
        rv = self.login_standard()
        assert login_error in str(rv.data)

    def test_user_login_no_account(self):
        rv = self.login_standard()
        assert login_error in str(rv.data)

    def test_user_logout_session(self):
        self.register_standard()
        with self.app as context:
            self.login_standard(context)
            context.get('/logout', follow_redirects=True)
            assert session.get('id') is None
