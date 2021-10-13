from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class FilterForm(FlaskForm):
    """cdfService.forms.forms.FilterForm
    Form used to add or remove filters.
    Args:
        FlaskForm (form): Flask Web Form.
    """
    filter = StringField('Filter', validators=[DataRequired(), Length(min=3),])
    service = StringField('Service', validators=[DataRequired(), Length(min=2),], default='NONE')
    submit_filter = SubmitField('Submit Filter')
    remove_filter = SubmitField('Remove filter')
    

class ReloadForm(FlaskForm):
    """cdfService.forms.forms.ReloadForm
    Flask web form used to log username from support person and start the flag reloads.
    All cdf's are tested against the new set of regex patterns and their flags are updated.


    Args:
        FlaskForm ([type]): [description]
    """
    id = StringField('Username', validators=[DataRequired(), Length(min=6, max=25),])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('RELOAD FLAGS')

    
class FilterSearchForm(FlaskForm):
    search = StringField('FILTER STRING TO SEARCH FOR')
    starts_with = BooleanField("Starts With")
    contains = BooleanField("Contains")
    submit = SubmitField('SEARCH!')



