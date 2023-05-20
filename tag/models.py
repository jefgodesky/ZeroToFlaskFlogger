from application import db

tag_key = db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
post_key = db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
tag_x_post = db.Table('tag_x_post', tag_key, post_key)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name
