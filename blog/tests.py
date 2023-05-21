import unittest

from blog.models import Post
from comment.models import Comment
from tag.models import Tag
from author.tests import AuthorTest
from application import db, create_app as create_app_base
from utils.test_db import TestDB


class PostTest(unittest.TestCase):
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

    def tearDown(self):
        with self.app_factory.app_context():
            self.test_db.drop_db()

    @staticmethod
    def post_dict():
        return dict(
            title='Test Post',
            body='This is the original text.',
            new_category='Tests',
            tags_field='testing, unit tests'
        )

    def post_standard(self, context=None):
        context = context if context is not None else self.app
        context.post('/register', data=self.author_data)
        context.post('/login', data=self.author_data)
        return context.post('/post', data=self.post_data, follow_redirects=True)

    def test_blog_post_has_no_comments(self):
        with self.app as context:
            self.post_standard(context)
            post = Post.query.first()
            assert post.comments is not None
            assert post.comments.count() == 0

    def test_blog_post_has_comment(self):
        with self.app as context:
            self.post_standard(context)
            comment = Comment(1, 'This is a comment.')
            db.session.add(comment)
            db.session.commit()
            post = Post.query.first()
            assert post.comments is not None
            assert post.comments.count() == 1

    def test_blog_post_create_not_logged_in(self):
        rv = self.app.get('/post', follow_redirects=True)
        assert 'Please log in to continue.' in str(rv.data)

    def test_blog_post_create_success_message(self):
        rv = self.post_standard()
        title = self.post_data['title']
        assert f'&#34;{title}&#34; posted.' in str(rv.data)
        assert self.post_data['new_category'] in str(rv.data)

    def test_blog_post_create_success_db_record(self):
        with self.app as context:
            self.post_standard(context)
            assert Post.query.count() == 1

    def test_blog_post_update_success_messaging(self):
        self.post_standard()
        self.post_data['title'] = 'Updated Title'
        rv = self.app.post('/posts/1/test-post/edit', data=self.post_data, follow_redirects=True)
        assert 'Your changes to &#34;Updated Title&#34; have been saved.' in str(rv.data)
        assert self.post_data['title'] in str(rv.data)

    def test_blog_post_update_success_database(self):
        with self.app as context:
            self.post_standard(context)
            self.post_data['title'] = 'Updated Title'
            context.post('/posts/1/test-post/edit', data=self.post_data, follow_redirects=True)
            actual = Post.query.first()
            assert actual.title == self.post_data['title']

    def test_blog_post_update_tags_success_messaging(self):
        self.post_standard()
        self.post_data['tags_field'] = self.post_data['tags_field'] + ', updates'
        rv = self.app.post('/posts/1/test-post/edit', data=self.post_data, follow_redirects=True)
        assert 'updates' in str(rv.data)

    def test_blog_post_update_tags_success_database(self):
        with self.app as context:
            self.post_standard(context)
            self.post_data['tags_field'] = self.post_data['tags_field'] + ', updates'
            context.post('/posts/1/test-post/edit', data=self.post_data, follow_redirects=True)
            assert Tag.query.filter_by(name='updates').count() == 1

    def test_blog_delete_success_messaging(self):
        self.post_standard()
        rv = self.app.get('/posts/1/test-post/delete', follow_redirects=True)
        assert '&#34;Test Post&#34; has been deactivated.' in str(rv.data)

    def test_blog_delete_success_database(self):
        with self.app as context:
            self.post_standard(context)
            context.get('/posts/1/test-post/delete', follow_redirects=True)
            actual = Post.query.first()
            assert actual is not None and actual.live is False
