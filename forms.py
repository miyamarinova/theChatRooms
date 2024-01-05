from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, IntegerField, StringField,SubmitField, BooleanField,PasswordField, TextAreaField, validators,SelectField
from flask_wtf import FlaskForm

class AddStoryForm(FlaskForm):
    author = StringField('Author')
    title = StringField("Story Title", [validators.DataRequired()])
    story = TextAreaField('Your Story', [validators.DataRequired()])
