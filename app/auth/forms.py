import string
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    StringField, TextAreaField, SubmitField, PasswordField,
    BooleanField, ValidationError
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                            Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[Length(1, 64)])
    last_name = StringField('Last Name', validators=[DataRequired(),
                            Length(1, 64)])
    username = StringField('Username', validators=[DataRequired(),
        Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        'Usernames may only have letters, numbers, dots, or underscores')])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                        Email()])
    password = PasswordField('Password', validators=[DataRequired(),
        EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')


    # wtform methods defined that begin with validate_<field> are invoked
    # automatically as an additional field validator
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('That email is already registered. Reset password?')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('That username is already registered, please choose another.')


class EditPasswordForm(FlaskForm):
    old_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(),
        EqualTo('new_password2', message='Passwords must match.')])
    new_password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Save Changes')


class EditUserInfo(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    username = StringField('Username')
    bio = TextAreaField()
    location = StringField('Location')
    submit = SubmitField('Save Changes')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('That username is already registered, please choose another.')
        if not is_valid_username(field.data):
            raise ValidationError('Usernames must be between 1 and 64 characters and' \
                'may only have letters, numbers, dots, or underscores')


def is_valid_username(name):
    """
    param:
        name (str)
    returns True if name is between 1 and 64 characters and contains 
    only alphanumeric characters plus '_' and '.', else False.
    """
    if len(name) < 1 or len(name) > 64:
        return False
    valid_characters = string.ascii_letters + string.digits + '.' + '_'
    for c in name:
        if c not in valid_characters:
            return False
    return True


class EditEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                        Email()])
    submit = SubmitField('Save Changes')
