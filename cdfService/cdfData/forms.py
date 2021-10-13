from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length


class CDFSearchForm(FlaskForm):
    search = StringField('CDF NAME OR STRING TO SEARCH FOR')
    starts_with = BooleanField("Starts With")
    contains = BooleanField("Contains")
    submit = SubmitField('SEARCH!')


class RebuildForm(FlaskForm):
    """cdfService.forms.forms.ReloadForm
    Flask web form used to log username from support person and start the flag reloads.
    All cdf's are tested against the new set of regex patterns and their flags are updated.


    Args:
        FlaskForm ([type]): [description]
    """
    id = StringField('Username', validators=[DataRequired(), Length(min=6, max=25),])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Rebuild CDF Data Table. This should find missing CDFs.')