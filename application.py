from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from passlib.apps import custom_app_context as CryptContext
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

        # ensure the security question has been answered
        elif not request.form.get("veiligheidsvraag"):
            return apology("Beantwoord de veiligheidsvraag.")

        # hash the password
        wachtwoord = pwd_context.hash(request.form.get("wachtwoord"))

        # insert the user into the database
        result = db.execute("INSERT INTO gebruikers (gebruikersnaam, wachtwoord, email, veiligheidsvraag) VALUES \
                            (:gebruikersnaam, :wachtwoord, :email, :veiligheidsvraag)",
                            gebruikersnaam=request.form.get("gebruikersnaam"), wachtwoord=wachtwoord,
                            email=request.form.get("email"), veiligheidsvraag=request.form.get("veiligheidsvraag"))

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
    """
    Log user in.
    """

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure form was filled
        if not request.form.get("gebruiker-inloggen"):
            return apology("Geef een gebruikersnaam op")
        elif not request.form.get("wachtwoord-inloggen"):
            return apology("Geef een wachtwoord op")

        # query database for username
        rows = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                          gebruikersnaam=request.form.get("gebruiker-inloggen"))

        rows1 = db.execute("SELECT * FROM gebruikers WHERE email = :email",
                          email=request.form.get("gebruiker-inloggen"))

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

    if request.method == "POST":

        toetevoegenvriend = request.form.get("vriend")

        vriend = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                          gebruikersnaam=toetevoegenvriend)

        if not vriend:
            return apology("Deze gebruikersnaam bestaat niet.")

        lijst = db.execute("SELECT gebruikersnaam FROM gebruikers WHERE id=:id", id=session["user_id"])
        gebruiker = lijst[0]["gebruikersnaam"]

        altoegevoegd = db.execute("SELECT naar FROM verzoeken WHERE naar =:naar AND van=:van AND geaccepteerd IS NULL",
        naar=toetevoegenvriend, van=gebruiker)
        tekst = "Je hebt " + toetevoegenvriend + " al toegevoegd"

        if altoegevoegd:
            return apology(tekst)

        if toetevoegenvriend == gebruiker:
            return apology("Je kan jezelf niet toevoegen")

        alvrienden = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                van=toetevoegenvriend, naar=gebruiker, geaccepteerd="ja")

        tekstt = "Je bent al vrienden met " + toetevoegenvriend

        if alvrienden:
            return apology("Jullie zijn al vrienden")

        aluitgenodigd = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND uitgenodigd=:uitgenodigd",
                                    van=toetevoegenvriend, naar=gebruiker, uitgenodigd="ja")

        if aluitgenodigd:
            return redirect("/verzoeken")

        nogeenkeeruitnodigen = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                           van=toetevoegenvriend, naar=gebruiker, geaccepteerd="nee")
        if nogeenkeeruitnodigen:
            db.execute("UPDATE verzoeken (van, naar, geaccepteerd) VALUES (:van, :naar, :geaccepteerd)",
                        van=gebruiker, naar=toetevoegenvriend, geaccepteerd="NULL")

        else:

            db.execute("INSERT INTO verzoeken (van, naar, uitgenodigd) VALUES (:van, :naar, :uitgenodigd)",
                        van=gebruiker, naar=toetevoegenvriend, uitgenodigd="ja")

            return render_template("toegevoegd.html", toetevoegenvriend=toetevoegenvriend)

    return render_template("vriendtoevoegen.html")

@app.route("/toegevoegd", methods=["GET", "POST"])
@login_required
def toegevoegd():
    return render_template("toegevoegd.html")

@app.route("/vriendenlijst")
@login_required
def vriendenlijst():

    lijst = db.execute("SELECT gebruikersnaam FROM gebruikers WHERE id=:id", id=session["user_id"])
    gebruiker = lijst[0]["gebruikersnaam"]

    vrienden = db.execute("SELECT van FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                           naar=gebruiker, geaccepteerd="ja")

    print(vrienden)

    return render_template("vriendenlijst.html", vrienden=vrienden)

@app.route("/geaccepteerd", methods=["GET", "POST"])
@login_required
def geaccepteerd():

    accepteren = request.form.get("accepteren")
    gebruiker = db.execute("SELECT gebruikersnaam FROM gebruikers WHERE id=:id", id=session["user_id"])
    gebruikerzelf = gebruiker[0]["gebruikersnaam"]

    db.execute("UPDATE verzoeken SET geaccepteerd=:geaccepteerd WHERE van=:van AND naar=:naar", geaccepteerd="ja",
                van=accepteren, naar=gebruikerzelf)

    return redirect("/verzoeken")

@app.route("/geweigerd", methods=["GET", "POST"])
@login_required
def geweigerd():

    weigeren = request.form.get("weigeren")
    gebruiker = db.execute("SELECT gebruikersnaam FROM gebruikers WHERE id=:id", id=session["user_id"])
    gebruikerzelf = gebruiker[0]["gebruikersnaam"]

    db.execute("UPDATE verzoeken SET geaccepteerd=:geaccepteerd WHERE van=:van AND naar=:naar", geaccepteerd="nee",
                van=weigeren, naar=gebruikerzelf)

    return redirect("/verzoeken")

@app.route("/verzoeken", methods=["GET", "POST"])
@login_required
def verzoeken():

    gebruiker = db.execute("SELECT gebruikersnaam FROM gebruikers WHERE id=:id", id=session["user_id"])
    gebruikerzelf = gebruiker[0]["gebruikersnaam"]

    verzoeken = db.execute("SELECT van FROM verzoeken WHERE naar=:naar AND geaccepteerd IS NULL",
                            naar=gebruikerzelf)

    return render_template("verzoeken.html", verzoeken=verzoeken)

# ZOEKEN
'''
    from urllib.request import urlopen
    popular = json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl&sort_by=popularity.desc&page=1&with_original_language=nl").content).decode('UTF-8')))
    popular_results = popular["results"]
'''
def zoeken(zoekterm, pagenr):

    # ophalen (per pagina)
    from urllib.request import urlopen
    url = "https://api.themoviedb.org/3/search/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl&query=" + zoekterm + "&include_adult=false&page=" + str(pagenr)
    response = json.loads(str((requests.get(url).content).decode('UTF-8')))

    '''
    # geen resultaten
    if response["total_results"] == 0:
        return False
    # als paginanummer niet voorkomt
    elif int(pagenr) > response["total_pages"]:
        return False
    else:
    '''
    return response

@app.route("/zoeken", methods=["GET", "POST"])
def zoekresultaat():

    if request.method == "POST":
        zoekterm = request.form.get("zoekterm")

        if not zoekterm: return apology("Geen zoekterm")

        # resultaten pagina 1 - 30
        elif zoeken(zoekterm, 1) != False:
            zoekresultaten = zoeken(zoekterm, 1)["results"]
            x = 2
            while x < 30:
                zoekresultaten += zoeken(zoekterm, x)["results"]
                x += 1
            return render_template("zoekresultaten.html", zoekresultaten=zoekresultaten)

        else: return apology("Iets ging mis")

# Onderstaande ding is backup voor def zoekresultaat():
'''
    if request.method == "POST":
        zoekterm = request.form.get("zoekterm")
        if not zoekterm:
            return apology("Geen zoekterm")
        elif zoeken(zoekterm, 1) != False:
            zoekresultaten = zoeken(zoekterm, 1)
            return render_template("zoekresultaten.html", zoekresultaten=zoekresultaten)
'''


        ##als het nederlands is
        #"original_language":"nl"
 #       if not stockinfo:
 #           return apology("Stock is not valid")
 #       return render_template("stockprice.html", aandeel=stockinfo)
 #   else:
 #       return render_template("quote.html")

    # zoekresultaat TMDb id naar IMDb id (als OMDb input)
   # "https://api.themoviedb.org/3/movie/569050?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl"

@app.route("/filminfo", methods=["GET", "POST"])
def filminformatie():


    tmdbid = request.form.get("tmdb_id")
    if request.method == "POST":

        # Alle informatie ophalen voor zoekresultaat (TMDb)
        from urllib.request import urlopen
        tmdb_url = str("https://api.themoviedb.org/3/movie/" + tmdbid + "?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl")
        tmdb_response = json.loads(str((requests.get(tmdb_url).content).decode('UTF-8')))

        # Als er geen IMDb id genoemd wordt
        if tmdb_response["imdb_id"] == None or "tt" not in tmdb_response["imdb_id"]:
            omdb_response = None

        # Alle informatie ophalen voor zoekresultaat (OMDb)
        else:
            omdb_url = "http://www.omdbapi.com/?i=" + tmdb_response["imdb_id"] + "&apikey=be77e5d"
            omdb_response = json.loads(str((requests.get(omdb_url).content).decode('UTF-8')))
        return render_template("filminformatie.html", tmdb=tmdb_response, omdb=omdb_response)
        print(omdb_url)

@app.route("/profiel")
@login_required
def profiel():
    "Pas je profiel aan"
    return render_template("profiel.html")


@app.route("/wachtwoordveranderen", methods=["GET", "POST"])
@login_required
def wachtwoordveranderen():
    """Verander wachtwoord"""

    if request.method == 'POST':

        # bevestig oud wachtwoord
        if not request.form.get('wachtwoord'):
            return apology("Vul je huidige wachtwoord in")

        # pak id uit database
        account = db.execute("SELECT * FROM gebruikers WHERE id = :id", id=session['user_id'])

        # bevestig of het wachtwoord klopt
        if len(account) != 1 or not pwd_context.verify(request.form.get('wachtwoord'), account[0]['wachtwoord']):
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

        # beantwoord de veiligheidsvraag
        if not request.form.get('veiligheidsvraag'):
            return apology("Beantwoord de veiligheidsvraag.")

        # bevestig of het antwoord klopt
        if len(account) != 1 or request.form.get('veiligheidsvraag') != account[0]['veiligheidsvraag']:
            return apology("Het antwoord op de veiligheidsvraag klopt niet!")

        # maak een hash van het wachtwoord
        niet_hash = request.form.get("nieuw_wachtwoord")
        new_hash = CryptContext.hash(niet_hash)

        # update de gebruiker
        resultaat = db.execute("UPDATE gebruikers SET wachtwoord=:wachtwoord WHERE id=:id", id=session["user_id"], wachtwoord=new_hash)

        if not resultaat:
            return apology("Iets ging fout...")

        return redirect(url_for("index"))

    else:
        return render_template("wachtwoordveranderen.html")