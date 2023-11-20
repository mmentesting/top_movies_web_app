from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired

class RateMovieForm(FlaskForm):
    user_rating = FloatField(label="Your Rating Out of 10 e.g. 8.5", validators=[DataRequired()])
    user_review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")

class AddMovieForm(FlaskForm):
    movie_title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")
