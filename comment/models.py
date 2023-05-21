from datetime import datetime

from application import db
from settings import ANONYMOUS_COMMENTER_NAME


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    commenter_name = db.Column(db.String(255))
    commenter_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)

    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))
    author = db.relationship('Author', backref=db.backref('comments', lazy='dynamic'))

    def __init__(self, body, commenter_name=None, commenter_id=None, timestamp=None):
        self.body = body
        self.timestamp = timestamp if timestamp is not None else datetime.utcnow()
        self.commenter_id = commenter_id if commenter_id is not None else None
        self.commenter_name = commenter_name if commenter_name is not None else ANONYMOUS_COMMENTER_NAME
        self.commenter_name = self.commenter_name if self.commenter_id is None else None

    def __repr__(self):
        return f'<Comment #{self.id}>'

    def get_commenter(self):
        return self.author.full_name if self.author else self.commenter_name
