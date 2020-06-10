from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class URLForm(FlaskForm):
    url = StringField('URL', validators = [DataRequired(), Length(min = 5, max = 250)])
    submit = SubmitField('Shorten')
    