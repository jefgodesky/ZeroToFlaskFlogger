import unittest
from datetime import datetime

from comment.models import Comment
from author.tests import AuthorTest
from blog.tests import PostTest
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
        self.post_data = PostTest.post_dict()
        with self.app_factory.app_context():
            db.create_all()
            self.post_standard()

    def post_standard(self, context=None):
        context = context if context is not None else self.app
        context.post('/register', data=self.author_data)
        context.post('/login', data=self.author_data)
        return context.post('/post', data=self.post_data, follow_redirects=True)

    def tearDown(self):
        with self.app_factory.app_context():
            self.test_db.drop_db()

    def test_new_comment_default_timestamp(self):
        actual = Comment(1,text)
        after = datetime.utcnow()
        assert actual.timestamp <= after

    def test_new_comment_set_timestamp(self):
        timestamp = datetime(1979, 1, 1)
        actual = Comment(1, text, timestamp=timestamp)
        assert actual.timestamp == timestamp

    def test_new_anonymous_comment(self):
        actual = Comment(1, text)
        assert actual.commenter_name == ANONYMOUS_COMMENTER_NAME
        assert actual.commenter_id is None

    def test_new_comment_with_name(self):
        actual = Comment(1, text, commenter_name=commenter_name)
        assert actual.commenter_name == commenter_name
        assert actual.commenter_id is None

    def test_new_author_comment(self):
        with self.app as context:
            context.post('/register', data=self.author_data)
            actual = Comment(1, text, commenter_id=1)
            assert actual.commenter_name is None
            assert actual.commenter_id == 1

    def test_get_commenter_anonymous(self):
        actual = Comment(1, text)
        assert actual.get_commenter() == ANONYMOUS_COMMENTER_NAME

    def test_get_commenter_explicitly_set(self):
        actual = Comment(1, text, commenter_name=commenter_name)
        assert actual.get_commenter() == commenter_name

    def test_get_commenter_blank_name(self):
        actual = Comment(1, text, commenter_name='')
        assert actual.get_commenter() == ANONYMOUS_COMMENTER_NAME

    def test_get_commenter_author(self):
        with self.app as context:
            context.post('/register', data=self.author_data)
            actual = Comment(1, text, commenter_id=1)
            db.session.add(actual)
            db.session.commit()
            assert actual.get_commenter() == self.author_data['full_name']
