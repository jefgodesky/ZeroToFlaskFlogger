from flask_wtf import FlaskForm
from wtforms import validators, StringField, PasswordField, ValidationError
from wtforms.fields import EmailField
from werkzeug.security import check_password_hash

from author.models import Author

password_len_validator = validators.length(min=4, max=256)


class LoginForm(FlaskForm):
    email = EmailField('Email Address', [validators.InputRequired(), validators.Email()])
    password = PasswordField('Password', [validators.InputRequired(), password_len_validator])

    def validate(self, extra_validators=None):
        error_message = 'Incorrect email or password.'
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        author = Author.query.filter_by(email=self.email.data).first()
        if author and check_password_hash(author.password, self.password.data):
            return True
        else:
            self.password.errors.append(error_message)
            return False


class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', [validators.InputRequired()])
    email = EmailField('Email Address', [validators.InputRequired(), validators.Email()])
    password = PasswordField('New Password', [validators.InputRequired(), password_len_validator])
    confirm_password = PasswordField('Confirm Password', [validators.EqualTo('password', message='Passwords must match.')])

    def validate_email(self, email):
        author = Author.query.filter_by(email=email.data).first()
        if author is not None:
            raise ValidationError(f'{email.data} is already in use. Please use a different email address.')
