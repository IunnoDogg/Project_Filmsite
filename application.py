from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import datetime

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
    return render_template("index.html")

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/homepage1")
def homepage1():
    return render_template("homepage1.html")

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

@app.route("/vriend", methods=["GET", "POST"])
@login_required
def vriend():
    if request.method == "GET":
        return render_template("vriend.html")
    else:
        # juiste naam
        naam = lookup(request.form.get("gebruikersnaam"))
        if not naam:
            return apology("We kunnen deze naam niet vinden")

        # selecteer de persoon
        vriendo = db.execute("SELECT gebruikersnaam FROM gebruikers \
                           WHERE id = :id", \
                           id=session["user_id"])

        # maak nieuwe vriend als de gebruiker deze nog niet heeft
        if not vriendo:
            db.execute("INSERT INTO vrienden (id, vriendennaam) \
                        VALUES(:id, :vriendennaam)", \
                        id=session["user_id"], vriendennaam=["naam"])

        else:
            return apology("Deze gebruiker is al je vriend")

        # return to index
        return redirect(url_for("index"))

@app.route("/profiel")
@login_required
def profiel():
    "Pas je profiel aan"
    return render_template("profiel.html")


@app.route("/wachtwoordveranderen")
@login_required
def wachtwoordveranderen():
    """Verander wachtwoord"""

    if request.method == 'POST':

        # bevestig oud wachtwoord
        if not request.form.get('wachtwoord'):
            return apology("Vul je huidige wachtwoord in")

        # pak id uit database
        account = db.execute("SELECT * FROM gebruikers WHERE id = :id", user_id=session['id'])

        # bevestig of het wachtwoord klopt
        if len(account) != 1 or not pwd_context.verify(request.form.get('wachtwoord'), account[0]['hash']):
            return apology("Het wachtwoord klopt niet!")

        # check of een nieuw wachtwoord is ingevuld
        if not request.form.get("nieuw_wachtwoord"):
            return apology("Vul een nieuw wachtwoord in")

        # check of het nieuwe wachtwoord is herhaald
        if not request.form.get("wachtwoord_herhaling"):
            return apology("Herhaal je nieuwe wachtwoord")

        # controleer of beide wachtwoorden overeenkomen
        if request.form.get("nieuw_wachtwoord") != request.form.get("wachtwoord_herhaling"):
            return apology("De wachtwoorden komen niet overeen")

        # maak een hash van het wachtwoord
        niet_hash = request.form.get("nieuw_wachtwoord")
        hash = pwd_context.encrypt(niet_hash)

        # update de gebruiker
        resultaat = db.execute("UPDATE gebruikers SET hash=:wachtwoord", hash=hash)

        if not resultaat:
            return apology("Iets ging fout...")

        return redirect(url_for("index"))

    else:
        return render_template("wachtwoordveranderen.html")


@app.route("/gebruikersnaamveranderen")
@login_required
def gebruikersnaamveranderen():
    """Verander gebruikersnaam"""

    if request.method == 'POST':

        # pak id uit database
        account = db.execute("SELECT * FROM gebruikers WHERE id = :id", user_id=session['id'])

        # check of een nieuwe gebruikersnaam is ingevuld
        if not request.form.get("new_username"):
            return apology("Vul een nieuwe gebruikersnaam in")

        # de nieuwe naam
        newname = request.form.get("new_username")

        # update de gebruiker
        resultaat = db.execute("UPDATE gebruikers SET newname=:gebruikersnaam")

        if not resultaat:
            return apology("Iets ging fout...")

        return redirect(url_for("index"))

    else:
        return render_template("gebruikersnaamveranderen.html")