from flask_wtf import FlaskForm
from wtforms import validators, StringField, TextAreaField


class CommentForm(FlaskForm):
    commenter_name = StringField('Your Name', [validators.Length(max=255)])
    body = TextAreaField('Content', [validators.InputRequired()])
