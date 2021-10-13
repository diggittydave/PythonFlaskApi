from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length



class LoginForm(FlaskForm):
    """cdfService.forms.forms.LoginForm
    form used on login page.

    Args:
        FlaskForm (form): Flask Web Form.
    """
    id = StringField('Username', validators=[DataRequired(), Length(min=6, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

