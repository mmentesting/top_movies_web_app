from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from forms import RateMovieForm, AddMovieForm
import requests
import os

TMDB_API_KEY = os.environ["TMDB_API_KEY"]
TMDB_S_ENDPOINT = "https://api.themoviedb.org/3/search/movie"
TMDB_M_ENDPOINT = "https://api.themoviedb.org/3/movie"
TMDB_IMG_ENDPOINT = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["APP_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///my_movies.db"
Bootstrap5(app)

db = SQLAlchemy()
db.init_app(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

# with app.app_context():
#     db.create_all()

@app.route("/")
def home():
    all_movies = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars().all()
    for index in range(len(all_movies)):
        all_movies[index].ranking = len(all_movies) - index
        db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    add_form = AddMovieForm()
    if add_form.validate_on_submit():
        movie_title = add_form.data.get("movie_title")
        params = {"api_key": TMDB_API_KEY, "query": movie_title}
        response = requests.get(url=TMDB_S_ENDPOINT, params=params)
        data = response.json()["results"]
        return render_template("select.html", all_movies_title=data)
    return render_template("add.html", form=add_form)

@app.route("/find")
def find_movie():
    tm_api_id = request.args.get("tm_id")
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url=f"{TMDB_M_ENDPOINT}/{tm_api_id}", params=params)
    data = response.json()
    new_movie = Movie(
        title=data["title"],
        year=data["release_date"].split("-")[0],
        description=data["overview"],
        img_url=f"{TMDB_IMG_ENDPOINT}/{data['poster_path']}",
        )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("edit_rating", id=new_movie.id))

@app.route("/edit", methods=["GET", "POST"])
def edit_rating():
    edit_form = RateMovieForm()
    movie_id = request.args.get("id")
    movie_to_edit = db.get_or_404(Movie, movie_id)
    # movie_to_edit = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
    if edit_form.validate_on_submit():
        movie_to_edit.rating = edit_form.data.get("user_rating")
        movie_to_edit.review = edit_form.data.get("user_review")
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movie=movie_to_edit, form=edit_form)

@app.route("/delete")
def delete_record():
    movie_id = request.args.get("id")
    movie_to_delete = db.get_or_404(Movie, movie_id)
    # movie_to_delete = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
