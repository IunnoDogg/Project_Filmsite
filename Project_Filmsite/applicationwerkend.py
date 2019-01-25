from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import datetime, requests, json, xml.etree.ElementTree, urllib
from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///nlfilms.db")

@app.route("/index")
@login_required
def index():
    from urllib.request import urlopen
    popular = json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl&sort_by=popularity.desc&page=1&with_original_language=nl").content).decode('UTF-8')))
    popular_results = popular["results"]
    return render_template("index.html", results=popular_results)

@app.route("/")
def homepage():
    # Haal populaire films op
    from urllib.request import urlopen
    popular = json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl&sort_by=popularity.desc&page=1&with_original_language=nl").content).decode('UTF-8')))
    popular_results = popular["results"]

    # Vanavond op televisie
    return render_template("homepage.html", results=popular_results)

@app.route("/wachtwoord")
def wachtwoord():
    return render_template("wachtwoord.html")

@app.route("/overons")
def overons():
    return render_template("overons.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("gebruikersnaam"):
            return apology("Geef een gebruikersnaam op.")

        # ensure password was submitted
        elif not request.form.get("email"):
            return apology("Geef een e-mailadres op.")

        # ensure password was submitted
        elif not request.form.get("wachtwoord"):
            return apology("Geef een wachtwoord op.")

        # ensure password-confirmation was submitted
        elif not request.form.get("wachtwoord-confirmatie"):
            return apology("Geef het wachtwoord nogmaals op.")

        # ensure password equals password confirmation
        if request.form.get("wachtwoord") != request.form.get("wachtwoord-confirmatie"):
            return apology("De bevestiging komt niet overeen met het wachtwoord.")

        # hash the password
        wachtwoord = pwd_context.hash(request.form.get("wachtwoord"))

        # insert the user into the database
        result = db.execute("INSERT INTO gebruikers (gebruikersnaam, wachtwoord, email) VALUES \
                            (:gebruikersnaam, :wachtwoord, :email)",
                            gebruikersnaam=request.form.get("gebruikersnaam"), wachtwoord=wachtwoord,
                            email=request.form.get("email"))

        if not result:
            return apology("username already exists")

        # query database for username
        rows = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                          gebruikersnaam=request.form.get("gebruikersnaam"))

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("registreren.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("gebruiker-inloggen"):
            return apology("Geef een gebruikersnaam op")

        # ensure password was submitted
        elif not request.form.get("wachtwoord-inloggen"):
            return apology("Geef een wachtwoord op")

        # query database for username
        rows = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                          gebruikersnaam=request.form.get("gebruiker-inloggen"))

        rows1 = db.execute("SELECT * FROM gebruikers WHERE email = :email",
                          email=request.form.get("gebruiker-inloggen"))

        print(rows)
        print(rows1)

        if len(rows) == 0:
            if len(rows1) != 1 or not pwd_context.verify(request.form.get("wachtwoord-inloggen"), rows1[0]["wachtwoord"]):
                return apology("Ongeldige email en/of wachtwoord")

        # ensure username exists and password is correct
        elif len(rows) != 1 or not pwd_context.verify(request.form.get("wachtwoord-inloggen"), rows[0]["wachtwoord"]):
            return apology("Ongeldige gebruikersnaam en/of wachtwoord")

        # remember which user has logged in
        if len(rows) > 0:
            session["user_id"] = rows[0]["id"]

        elif len(rows1) > 0:
            session["user_id"] = rows1[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("inloggen.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/vriend")
@login_required
def vriend():
    return render_template("vriendtoevoegen.html")

@app.route("/vriendenlijst")
@login_required
def vriendenlijst():
    return render_template("vriendenlijst.html")

# ZOEKEN
'''
    from urllib.request import urlopen
    popular = json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl&sort_by=popularity.desc&page=1&with_original_language=nl").content).decode('UTF-8')))
    popular_results = popular["results"]
'''
def zoeken(zoekterm, pagenr):
    from urllib.request import urlopen
    url = "https://api.themoviedb.org/3/search/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl&query=" + zoekterm + "&include_adult=false&page=" + pagenr
    zoekresultaten = (json.loads(str((requests.get(url).content).decode('UTF-8'))))["results"]
    if not zoekresultaten:
        return False
    else: return zoekresultaten

@app.route("/zoeken", methods=["GET", "POST"])
def zoekresultaat():

    if request.method == "POST":
        zoekterm = request.form.get("zoekterm")
        if not zoekterm:
            return apology("Geen zoekterm")
        elif zoeken(zoekterm, "2") != False:
            zoekresultaten = zoeken(zoekterm, "2")
            return render_template("zoekresultaten.html", zoekresultaten=zoekresultaten)
        ##als het nederlands is
        #"original_language":"nl"


 #       if not stockinfo:
 #           return apology("Stock is not valid")
 #       return render_template("stockprice.html", aandeel=stockinfo)
 #   else:
 #       return render_template("quote.html")

    # zoekresultaat TMDb id naar IMDb id (als OMDb input)
    "https://api.themoviedb.org/3/movie/569050?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl"