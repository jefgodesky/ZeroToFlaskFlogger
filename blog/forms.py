from flask_wtf import FlaskForm
from wtforms import validators, StringField, TextAreaField, SelectField, FileField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileAllowed

from category.models import Category


def categories():
    return Category.query


class PostForm(FlaskForm):
    image = FileField('Image', [FileAllowed(['jpg', 'png'], 'JPEG or PNG files only.')])
    title = StringField('Title', [validators.InputRequired(), validators.Length(max=255)])
    body = TextAreaField('Content', [validators.InputRequired()])
    category = QuerySelectField('Category', query_factory=categories, allow_blank=True)
    new_category = StringField('New Category')
