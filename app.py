import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required, profile_required, search_tv, load_profile, count_matches

UPLOAD_FOLDER = '/home/ubuntu/project/static/profilepics'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded (from Pset 9: Finance)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure responses aren't cached (from Pset 9: Finance)
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///crimson.db")

# Renders homepage
@app.route("/")
@login_required
@profile_required
def index():
    return render_template("index.html")


# Allows user to register for an account (from Pset 9: Finance)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        username = request.form.get("username")
        if not username:
            return apology("must provide username")
        # Ensure username exists
        elif len(rows) != 0:
            return apology("username already exists")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password")
        # Ensure password and confirmation matches
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")
        password_hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES(?,?)", username, password_hash)
        return redirect("/")
    else:
        return render_template("register.html")


# Allows user to login (from Pset 9: Finance)
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Creates profile through form inputs
@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    # Stores user inputs into corresponding SQL tables
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        bday = request.form.get("birth")
        home = request.form.get("hometown")
        state = request.form.get("state")
        email = request.form.get("email")
        cell = request.form.get("cell")
        sc = request.form.get("snapchat")
        ig = request.form.get("instagram")
        classyear = request.form.get("class")
        house = request.form.get("dorm")
        major = request.form.get("major")
        minor = request.form.get("minor")
        db.execute("INSERT INTO profile (user_id, last_name, first_name, birthday, hometown, state) VALUES(?,?,?,?,?,?)", session["user_id"], lname, fname, bday, home, state)
        db.execute("INSERT INTO contact (user_id, email, cell, snapchat, instagram) VALUES(?,?,?,?,?)", session["user_id"], email, cell, sc, ig)
        db.execute("INSERT INTO academia (user_id, class, house, major, minor) VALUES(?,?,?,?,?)", session["user_id"], classyear, house, major, minor)
        hobby=[]
        extracurricular=[]
        description=[]
        tvlist=[]
        movielist=[]
        book=[]
        music=[]
        hobby_other = request.form.get("hobby-other")
        for n in range(2):
            hobby.append(request.form.get("hobby" + str(n)))
        for i in range(3):
            extracurricular.append(request.form.get("act" + str(i)))
            description.append(request.form.get("description" + str(i)))
            book.append(request.form.get("book" + str(i)))
            music.append(request.form.get("music" + str(i)))
            show = request.form.get("tv" + str(i))
            # Validates user input is a valid show
            if search_tv(show) == True:
                tvlist.append(show)
            else:
                tvlist.append("None")
            movie = request.form.get("movie" + str(i))
            # Validates user insput is a valid movie
            if search_tv(movie) == True:
                movielist.append(movie)
            else:
                movielist.append("None")
        db.execute("INSERT INTO interests (user_id, extracurricular0, description0, extracurricular1, description1, extracurricular2, description2, hobby0, hobby1, other_hobby) VALUES(?,?,?,?,?,?,?,?,?,?)", session["user_id"], extracurricular[0], description[0], extracurricular[1], description[1], extracurricular[2], description[2], hobby[0], hobby[1], hobby_other)
        db.execute("INSERT INTO entertainment (user_id, book0, book1, book2, show0, show1, show2, movie0, movie1, movie2, artist0, artist1, artist2) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", session["user_id"], book[0], book[1], book[2], tvlist[0], tvlist[1], tvlist[2], movielist[0], movielist[1], movielist[2], music[0], music[1], music[2])
        return redirect("/")
    # Renders profile creation page
    else:
        concentration = ["African and African American Studies","History and Science","Anthropology","History of Art and Architecture",
        "Applied Mathematics","Human Developmental and Regenerative Biology",
        "Art, Film, and Visual Studies","Human Evolutionary Biology",
        "Astrophysics","Integrative Biology",
        "Biomedical Engineering","Linguistics",
        "Chemical and Physical Biology","Mathematics","Chemistry","Mechanical Engineering",
        "Chemistry and Physics","Molecular and Cellular Biology",
        "Classics","Music",
        "Comparative Literature","Near Eastern Languages and Civilizations",
        "Computer Science","Neuroscience",
        "Earth and Planetary Sciences","Philosophy",
        "East Asian Studies","Physics",
        "Economics","Psychology",
        "Electrical Engineering", "Comparative Study of Religion",
        "Engineering Sciences","Romance Languages and Literatures",
        "English","Slavic Languages and Literatures",
        "Environmental Science and Engineering","Social Studies",
        "Environmental Science and Public Policy","Sociology",
        "Folklore and Mythology","South Asian Studies"
        "Germanic Languages and Literatures","Special Concentrations",
        "Government","Statistics",
        "History","Theater, Dance, & Media",
        "History and Literature","Study of Women, Gender, and Sexuality"]
        extracurricular = ["Varsity Athletics","Academic and Pre-Professional","College Life","Creative and Performing Arts","Cultural and Racial Initiatives",
        "Gender and Sexual Identity","Government and Politics","Health and Wellness","Hobbies and Special Interest","Media and Publications",
        "Peer Counseling and Peer Education","Public Service","Women's Initiatives","Religious and Spiritual"]
        hobbies = ["Cooking","Hiking/Outdoors Activities","Traveling","Politics","Exercise","Video Gaming","Studio Arts","Dance","Writing","Singing"
        ,"Playing an Instrument","Filmmaking","Social Media"]
        hobbies.sort()
        return render_template("create.html", concentration=concentration, extracurricular=extracurricular, hobbies=hobbies)

# Retrieves user id from form
def get_id():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        return user_id


# Loads profile
@app.route("/profile", methods=["POST"])
@login_required
def profile():
    user_id = get_id()
    # Loads profile page based on user id
    if request.method == "POST":
        username = db.execute("SELECT username FROM users WHERE id=?", user_id)
        user = load_profile(user_id)
        index = ['0','1','2']
        return render_template("profile.html", username=username[0]['username'], user=user, index=index)


# Finds matches for user based on shared background/interests
@app.route("/match")
@login_required
@profile_required
def match():
    logged_user = session["user_id"]
    users = db.execute("SELECT id FROM users WHERE id != ? AND id NOT IN (SELECT saved_id FROM saved_profiles WHERE user_id=?)", logged_user, logged_user)
    users_count = db.execute("SELECT count(id) FROM users WHERE id !=? AND id NOT IN (SELECT saved_id FROM saved_profiles WHERE user_id=?)", logged_user, logged_user)
    most_matches = 0
    most_match_id = None
    second_most_matches = 0
    second_match_id = None
    third_most_matches = 0
    third_match_id = None
    # Determines top three user matches
    for i in range(users_count[0]['count(id)']):
        curr_matches = count_matches(logged_user, users[i]['id'])
        if curr_matches > most_matches:
            most_match_id = users[i]['id']
            most_matches = curr_matches
        elif curr_matches > second_most_matches and curr_matches <= most_matches:
            second_match_id = users[i]['id']
            second_most_matches = curr_matches
        elif curr_matches > third_most_matches and curr_matches <= second_most_matches:
            third_match_id = users[i]['id']
            third_most_matches = curr_matches
    firstbio = db.execute("SELECT profile.user_id, first_name, last_name, hometown, state, class FROM profile INNER JOIN academia ON profile.user_id=academia.user_id WHERE profile.user_id=?", most_match_id)
    secondbio = db.execute("SELECT profile.user_id, first_name, last_name, hometown, state, class FROM profile INNER JOIN academia ON profile.user_id=academia.user_id WHERE profile.user_id=?", second_match_id)
    thirdbio = db.execute("SELECT profile.user_id, first_name, last_name, hometown, state, class FROM profile INNER JOIN academia ON profile.user_id=academia.user_id WHERE profile.user_id=?", third_match_id)
    matched_users = [firstbio, secondbio, thirdbio]
    matches = [most_matches, second_most_matches, third_most_matches]
    # Renders match page with information loaded from top three matches
    return render_template("match.html", user=matched_users, matches=matches)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Saves user from match page into database
@app.route("/saveprofile", methods=["POST"])
@login_required
@profile_required
def saveprofile():
    if request.method == "POST":
        saved_profile = get_id()
        db.execute("INSERT INTO saved_profiles (user_id, saved_id) VALUES (?,?)", session["user_id"], saved_profile)
        return redirect("/match")


# Removes saved profile
@app.route("/unsaveprofile", methods=["POST"])
@login_required
@profile_required
def unsave_profile():
    if request.method == "POST":
        deleted_profile = get_id()
        db.execute("DELETE FROM saved_profiles WHERE user_id=? AND saved_id=?", session["user_id"], deleted_profile)
        return redirect("/saved")


# Displays saved users
@app.route("/saved")
@login_required
@profile_required
def load_saved():
    users = db.execute("SELECT profile.user_id, first_name, last_name, hometown, state, class FROM profile INNER JOIN academia ON profile.user_id=academia.user_id WHERE profile.user_id IN (SELECT saved_id FROM saved_profiles WHERE user_id=?)", session["user_id"])
    return render_template("saved.html", user=users)


# Allows user to upload a profile picture
@app.route("/settings", methods=["GET","POST"])
@login_required
@profile_required
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.execute("UPDATE profile SET imgpath=? WHERE user_id=?", filename, session["user_id"])
            return redirect("/")
    return render_template("settings.html")


# Allows user to upload/update a brief bio to profile page
@app.route("/bio", methods=["POST"])
@login_required
@profile_required
def update_bio():
    if request.method =="POST":
        bio = request.form.get("bio")
        db.execute("UPDATE profile SET bio=? WHERE user_id=?", bio, session["user_id"])
        return redirect("/settings")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)