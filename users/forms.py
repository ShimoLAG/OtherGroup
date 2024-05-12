from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, validators, SubmitField, DateTimeField, TextAreaField, FileField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed
import app.models as models
import flask

class UserForm(FlaskForm):
    idnum = StringField('ID Number', [validators.InputRequired(), validators.Regexp('^\d{4}-\d{4}$')])
    college = SelectField('College', choices=["CCS", "COET", "CSM", "CON", "CEBA", "CASS", "CED"], validators=[validators.InputRequired()], validate_choice=False)
    course = SelectField('Course', choices=[""], validators=[validators.InputRequired()], validate_choice=False)
    year_level = SelectField('Year Level', choices=['1st Year','2nd Year','3rd Year','4th Year','5th Year','Irregular'], validators=[validators.InputRequired()], validate_choice=False)

class LoginForm(FlaskForm):
    login_username = StringField('Username', [validators.InputRequired(), validators.Length(min=3, max=20)])
    login_pw = PasswordField('Password', [validators.InputRequired()])

class EventForm(FlaskForm):
    image = FileField('Choose an Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!'),])
    eventname = StringField(' Event Name: ', validators = [validators.InputRequired()])
    description = TextAreaField(' About the event: ', validators = [validators.InputRequired()])
    location = StringField(' Where: ', validators = [validators.InputRequired()])
    DateTimeStart = DateTimeField(' From: ', format = "%Y-%m-%d %H:%M" , validators = [validators.DataRequired()])
    DateTimeEnd = DateTimeField('To:', format = "%Y-%m-%d %H:%M", validators = [validators.DataRequired()])
    participant_limit = IntegerField('No. of Participants:', validators = [validators.InputRequired(), validators.NumberRange(min=0)])
    hashtags = StringField('Event Tags: ', validators = [validators.InputRequired()])