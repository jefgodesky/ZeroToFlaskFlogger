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

    def __init__(self, post_id, body, commenter_name=None, commenter_id=None, timestamp=None):
        self.post_id = post_id
        self.body = body
        self.timestamp = timestamp if timestamp is not None else datetime.utcnow()
        self.commenter_id = commenter_id if commenter_id is not None else None
        self.commenter_name = commenter_name if commenter_name is not None and len(commenter_name) > 0 else ANONYMOUS_COMMENTER_NAME
        self.commenter_name = self.commenter_name if self.commenter_id is None else None

    def __repr__(self):
        return f'<Comment #{self.id}>'

    def get_commenter(self):
        if self.author:
            return self.author.full_name
        elif self.commenter_name is not None:
            return self.commenter_name if len(self.commenter_name) > 0 else ANONYMOUS_COMMENTER_NAME
        else:
            return ANONYMOUS_COMMENTER_NAME
