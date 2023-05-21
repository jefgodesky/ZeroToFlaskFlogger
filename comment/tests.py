import datetime
import unittest

from comment.models import Comment
from author.tests import AuthorTest
from application import db, create_app as create_app_base
from settings import ANONYMOUS_COMMENTER_NAME
from utils.test_db import TestDB

text = 'This is a test comment.'
commenter_name = 'Jane Doe'


class CommentTest(unittest.TestCase):
    def create_app(self):
        return create_app_base(
            SQLALCHEMY_DATABASE_URI=self.db_uri,
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY='Testing Key'
        )

    def setUp(self):
        self.test_db = TestDB()
        self.db_uri = self.test_db.create_db()
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client()
        self.author_data = AuthorTest.user_dict()
        with self.app_factory.app_context():
            db.create_all()

    def tearDown(self):
        with self.app_factory.app_context():
            self.test_db.drop_db()

    def test_new_anonymous_comment(self):
        actual = Comment(text)
        assert actual.commenter_name == ANONYMOUS_COMMENTER_NAME
        assert actual.commenter_id is None

    def test_new_comment_with_name(self):
        actual = Comment(text, commenter_name=commenter_name)
        assert actual.commenter_name == commenter_name
        assert actual.commenter_id is None

    def test_new_author_comment(self):
        with self.app as context:
            context.post('/register', data=self.author_data)
            actual = Comment(text, commenter_id=1)
            assert actual.commenter_name is None
            assert actual.commenter_id == 1

    def test_get_commenter_anonymous(self):
        actual = Comment(text)
        assert actual.get_commenter() == ANONYMOUS_COMMENTER_NAME

    def test_get_commenter_explicitly_set(self):
        actual = Comment(text, commenter_name=commenter_name)
        assert actual.get_commenter() == commenter_name

    def test_get_commenter_author(self):
        with self.app as context:
            context.post('/register', data=self.author_data)
            actual = Comment(text, commenter_id=1)
            db.session.add(actual)
            db.session.commit()
            assert actual.get_commenter() == self.author_data['full_name']
