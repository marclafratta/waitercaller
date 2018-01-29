from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.fields.html5 import EmailField
from wtforms import validators
from wtforms import StringField
from wtforms import HiddenField


class RegistrationForm(FlaskForm):
    password_length_message = "Please choose a password of at least 8 characters"
    email = EmailField('email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('password', validators=[validators.DataRequired(),
                                                     validators.Length(min=8, message=password_length_message)])
    password2 = PasswordField('password2', validators=[validators.DataRequired(),
                                                       validators.EqualTo('password', message='Passwords must match')])
    submit = SubmitField('submit', [validators.DataRequired()])


class LoginForm(FlaskForm):
    loginemail = EmailField('email', validators=[validators.DataRequired(), validators.Email()])
    loginpassword = PasswordField('password', validators=[validators.DataRequired(
        message="Password field is required")])
    submit = SubmitField('submit', [validators.DataRequired()])


class CreateTableForm(FlaskForm):
    tablenumber = StringField('tablenumber', validators=[validators.DataRequired()])
    submit = SubmitField('createtablesubmit', validators=[validators.DataRequired()])


class DeleteTableForm(FlaskForm):
    tablenumber = StringField('tablenumber', validators=[validators.DataRequired()])
    submit = SubmitField('createtablesubmit', validators=[validators.DataRequired()])