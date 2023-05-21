from application import db
from settings import ANONYMOUS_COMMENTER_NAME


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    commenter_name = db.Column(db.String(255))
    commenter_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    body = db.Column(db.Text)

    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))
    author = db.relationship('Author', backref=db.backref('comments', lazy='dynamic'))

    def __init__(self, body, commenter_name=None, commenter_id=None):
        self.body = body
        if commenter_id:
            self.commenter_id = commenter_id
        else:
            self.commenter_name = commenter_name if commenter_name is not None else ANONYMOUS_COMMENTER_NAME

    def __repr__(self):
        return f'<Comment #{self.id}>'

    def get_commenter(self):
        return self.author.full_name if self.author else self.commenter_name
