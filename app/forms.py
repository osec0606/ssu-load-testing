from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, URL, NumberRange
from wtforms.validators import DataRequired, ValidationError
import re

def validate_urls(form, field):

    urls = field.data.split('\n')
    url_pattern = re.compile(r'^(https?:\/\/)?[\w\-]+(\.[\w\-]+)+[/#?]?.*$')
    invalid_urls = [url for url in urls if not url_pattern.match(url.strip())]

    if invalid_urls:
        raise ValidationError(f'Invalid URL(s): {" ".join(invalid_urls)}. Please ensure all URLs are valid.')

class MyForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL(require_tld=True, message='Invalid URL')])
    num_requests = IntegerField('Number of Requests', default=5, validators=[DataRequired()])
    submit = SubmitField('Start Load Test')

class LoadTestForm(FlaskForm):
    urls = TextAreaField('URLs', validators=[DataRequired(), validate_urls],
                         description="Enter each URL on a new line.")
    num_requests = IntegerField('Number of Requests', default=5, validators=[DataRequired()])
    submit = SubmitField('Start Multi Load Test')


class RequestsForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL(require_tld=True, message='Invalid URL')])
    num_users = IntegerField('Number of Users', default=2, validators=[DataRequired()])
    num_requests_per_user = IntegerField('Number of Requests per User', default=5, validators=[DataRequired()])
    