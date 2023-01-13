import os
import requests
import itertools

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps

db = SQL("sqlite:///crimson.db")

# From Pset 9: Finance
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

# From Pset 9: Finance
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Validates that user has created a profile
def profile_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        rows = db.execute("SELECT * FROM profile WHERE user_id = ?", session.get("user_id"))
        if len(rows) != 1:
            return redirect("/create")
        return f(*args, **kwargs)
    return decorated_function

# Validates a show/movie title from API
def search_tv(title):

    url = "https://movie-database-imdb-alternative.p.rapidapi.com/"

    querystring = {"s":title,"page":"1","r":"json"}

    headers = {
        'x-rapidapi-key': "0c2d9afbd6msh793c0bf619f85f6p12caa3jsn31fb3b989463",
        'x-rapidapi-host': "movie-database-imdb-alternative.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    if response.text != '{"Response":"False","Error":"Movie not found!"}':
        return True

# Returns user information to be displayed on profile page
def load_profile(user_id):

    user = db.execute("SELECT * FROM profile INNER JOIN contact ON profile.user_id=contact.user_id INNER JOIN academia ON contact.user_id=academia.user_id INNER JOIN entertainment ON academia.user_id=entertainment.user_id JOIN interests ON entertainment.user_id=interests.user_id WHERE profile.user_id=?", user_id)
    return user

# Iterates through each table and counts number of shared items
def count_matches(logged_user, db_user):
    match = 0
    user_profile = db.execute("SELECT birthday, hometown, state FROM profile WHERE user_id=?", logged_user)
    other_profile = db.execute("SELECT birthday, hometown, state FROM profile WHERE user_id=?", db_user)
    for u_profile, o_profile in zip(user_profile, other_profile):
        for i, j in zip(u_profile.values(), o_profile.values()):
            if i == j:
                match += 1
    user_academia = db.execute("SELECT class, house, major, minor FROM academia WHERE user_id=?", logged_user)
    other_academia = db.execute("SELECT class, house, major, minor FROM academia WHERE user_id=?", db_user)
    for u_academia, o_academia in zip(user_academia, other_academia):
        for i, j in zip(u_academia.values(), o_academia.values()):
            if i == j:
                match += 1
    user_books = db.execute("SELECT book0, book1, book2 FROM entertainment WHERE user_id=?", logged_user)
    other_books = db.execute("SELECT book0, book1, book2 FROM entertainment WHERE user_id=?", db_user)
    for book, other_book in zip(user_books, other_books):
        for bk in book.values():
            for o_bk in other_book.values():
                if o_bk == bk:
                    match += 1
    user_shows = db.execute("SELECT show0, show1, show2 FROM entertainment WHERE user_id=?", logged_user)
    other_shows = db.execute("SELECT show0, show1, show2 FROM entertainment WHERE user_id=?", db_user)
    for shows, other_show in zip(user_shows, other_shows):
        for show in shows.values():
            for o_show in other_show.values():
                if o_show == show:
                    match += 1
    user_movies = db.execute("SELECT movie0, movie1, movie2 FROM entertainment WHERE user_id=?", logged_user)
    other_movies = db.execute("SELECT movie0, movie1, movie2 FROM entertainment WHERE user_id=?", db_user)
    for movies, other_movie in zip(user_movies, other_movies):
        for movie in movies.values():
            for o_movie in other_movie.values():
                if o_movie == movie:
                    match +=1
    user_music = db.execute("SELECT artist0, artist1, artist2 FROM entertainment WHERE user_id=?", logged_user)
    other_music = db.execute("SELECT artist0, artist1, artist2 FROM entertainment WHERE user_id=?", db_user)
    for music, o_music in zip(user_music, other_music):
        for mus in music.values():
            for o_mus in o_music.values():
                if o_mus == mus:
                    match +=1
    user_extracurriculars = db.execute("SELECT extracurricular0, extracurricular1, extracurricular2 FROM interests WHERE user_id=?", logged_user)
    other_extracurriculars = db.execute("SELECT extracurricular0, extracurricular1, extracurricular2 FROM interests WHERE user_id=?", db_user)
    status = False
    for extra, o_extra in zip(user_extracurriculars, other_extracurriculars):
        for ext in extra.values():
            for o_ext in o_extra.values():
                if o_ext == ext:
                    match +=1
                    status = True
                    break
            if status == True:
                status = False
                break
    user_hobbies = db.execute("SELECT hobby0, hobby1, other_hobby FROM interests WHERE user_id=?", logged_user)
    other_hobbies = db.execute("SELECT hobby0, hobby1, other_hobby FROM interests WHERE user_id=?", db_user)
    for hobbies, o_hobbies in zip(user_hobbies, other_hobbies):
        for hobby in hobbies.values():
            for o_hobby in o_hobbies.values():
                if o_hobby == hobby:
                    match +=1
    return match






