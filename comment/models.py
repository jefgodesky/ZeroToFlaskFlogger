from application import db
from settings import ANONYMOUS_COMMENTER_NAME


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commenter_name = db.Column(db.String(255))
    commenter_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    body = db.Column(db.Text)

    def __init__(self, body, commenter_name=None, commenter_id=None):
        self.body = body
        if commenter_id:
            self.commenter_id = commenter_id
        else:
            self.commenter_name = commenter_name if commenter_name is not None else ANONYMOUS_COMMENTER_NAME

    def __repr__(self):
        return f'<Comment #{self.id}>'
