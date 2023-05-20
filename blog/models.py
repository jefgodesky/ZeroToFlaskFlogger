from datetime import datetime

from application import db
from tag.models import tag_x_post


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    title = db.Column(db.String(255))
    body = db.Column(db.Text)
    image = db.Column(db.String(36))
    slug = db.Column(db.String(255), unique=True)
    publish_date = db.Column(db.DateTime)
    live = db.Column(db.Boolean)

    author = db.relationship('Author', backref=db.backref('posts', lazy='dynamic'))
    category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'))
    tags = db.relationship('Tag', backref=db.backref('posts', lazy='dynamic'), secondary=tag_x_post, lazy='subquery')

    def __init__(self, author, title, body, image=None, category=None, slug=None, publish_date=None, live=True):
        self.author_id = author.id
        self.title = title
        self.body = body
        self.image = image
        if category:
            self.category_id = category.id
        self.slug = slug
        if publish_date is None:
            self.publish_date = datetime.utcnow()
        self.live = live

    def __repr__(self):
        return f'<Post {self.title}>'
