from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
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

def zoeken_id(tmdb_id):
    # ophalen (per pagina)
    from urllib.request import urlopen
    url = "https://api.themoviedb.org/3/movie/" + tmdb_id + "?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl"
    response = json.loads(str((requests.get(url).content).decode('UTF-8')))

def gebruiker():
    a = db.execute("SELECT gebruikersnaam FROM gebruikers WHERE id=:id", id=session["user_id"])
    gebruikersnaam = a[0]["gebruikersnaam"]

    return gebruikersnaam

def verzoek():
    gebruikersnaam = gebruiker()
    verzoeken = db.execute("SELECT van FROM verzoeken WHERE naar=:naar AND geaccepteerd IS NULL",
                            naar=gebruikersnaam)

    return verzoeken

def lengte_vv():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()

    if verzoeken:
        lengte = len(verzoeken)
        return lengte

    else:
        lengte = 0
        return lengte

def apology(message, code=400):
    """Renders message as an apology to user."""
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    return render_template("apology.html", top=code, bottom=message, lengte=lengte)

def addtohistory(tmdb_id, tmdb_response):
    gebruikersnaam = gebruiker()
    historie = db.execute("SELECT film_id FROM historie WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)

    if len(historie) == 0:
        db.execute("INSERT INTO historie (gebruiker, film_id, titel, afbeelding) VALUES (:gebruiker, :film_id, :titel, :afbeelding)",
                    gebruiker=gebruikersnaam, film_id=tmdb_id, titel=tmdb_response["original_title"],
                    afbeelding=tmdb_response["poster_path"])

    if not tmdb_id in [i["film_id"] for i in historie] and len(historie) != 0:
        db.execute("INSERT INTO historie (gebruiker, film_id, titel, afbeelding) VALUES (:gebruiker, :film_id, :titel, :afbeelding)",
                    gebruiker=gebruikersnaam, film_id=tmdb_id, titel=tmdb_response["original_title"],
                    afbeelding=tmdb_response["poster_path"])


def ophalen(name):
    opgehaald = request.form.get(name)
    return opgehaald

def ophalenmislukt(name, error):
    opgehaald = request.form.get(name)

    if not opgehaald:
        return apology(error)

def select(zoekterm, tabel, gelijke_var, variabelen):

    a = "SELECT"
    b = '("{} '.format(a)
    c = '{} '.format(zoekterm)
    d = "FROM"
    e = '{} '.format(d)
    f = " WHERE"
    g = '{} '.format(f)
    h = '{}", '.format(gelijke_var)
    i= '{})'.format(variabelen)
    resultaat = (b+c+e+tabel+g+h+i)
    return resultaat


def registerform():
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


@app.route("/layout")
@login_required
def layout():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    return render_template("layout.html", verzoeken=verzoeken, lengte=lengte)

@app.route("/index")
@login_required
def index():
    from urllib.request import urlopen
    popular = json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl&sort_by=popularity.desc&page=1&with_original_language=nl").content).decode('UTF-8')))
    popular_results = popular["results"]

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    return render_template("index.html", results=popular_results, lengte=lengte)

@app.route("/")
def homepage():
    # Haal populaire films op
    from urllib.request import urlopen
    popular = json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl&sort_by=popularity.desc&page=1&with_original_language=nl").content).decode('UTF-8')))
    popular_results = popular["results"]

    return render_template("homepage.html", results=popular_results)

@app.route("/wachtwoord")
def wachtwoord():
    return render_template("wachtwoord.html")

@app.route("/overons")
def overons():
    if session["user_id"] > 0:
        gebruikersnaam = gebruiker()
        verzoeken = verzoek()
        lengte = lengte_vv()
        return render_template("overons.html", lengte=lengte)

    return render_template("overons.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":

        registerform()

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

        ophalenmislukt("gebruiker-inloggen", "Geef een gebruikersnaam op")
        ophalenmislukt("wachtwoord-inloggen", "Geef een wachtwoord op")

        # # query database for username
        # x = "gebruikersnaam=" + ophalen("gebruiker-inloggen")
        # a = select("*", "gebruikers", "gebruikersnaam=:gebruikersnaam", x)
        # print(a)
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

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    if request.method == "POST":

        toetevoegenvriend = ophalen("vriend")

        vriend = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                          gebruikersnaam=toetevoegenvriend)

        if not vriend:
            return apology("Deze gebruikersnaam bestaat niet.")

        altoegevoegd = db.execute("SELECT naar FROM verzoeken WHERE naar =:naar AND van=:van AND geaccepteerd IS NULL",
        naar=toetevoegenvriend, van=gebruikersnaam)
        tekst = "Je hebt " + toetevoegenvriend + " al toegevoegd"

        if altoegevoegd:
            return apology(tekst)

        if toetevoegenvriend == gebruikersnaam:
            return apology("Je kan jezelf niet toevoegen")

        alvrienden = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                van=toetevoegenvriend, naar=gebruikersnaam, geaccepteerd="ja")

        tekstt = "Je bent al vrienden met " + toetevoegenvriend

        if alvrienden:
            return apology("Jullie zijn al vrienden")

        aluitgenodigd = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND uitgenodigd=:uitgenodigd",
                                    van=toetevoegenvriend, naar=gebruikersnaam, uitgenodigd="ja")

        if aluitgenodigd:
            return apology("Deze gebruiker heeft je al uitgenodigd")

        nogeenkeeruitnodigen = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                           van=toetevoegenvriend, naar=gebruikersnaam, geaccepteerd="nee")
        if nogeenkeeruitnodigen:
            db.execute("UPDATE verzoeken (van, naar, geaccepteerd) VALUES (:van, :naar, :geaccepteerd)",
                        van=gebruikersnaam, naar=toetevoegenvriend, geaccepteerd="NULL")

        else:

            db.execute("INSERT INTO verzoeken (van, naar, uitgenodigd) VALUES (:van, :naar, :uitgenodigd)",
                        van=gebruikersnaam, naar=toetevoegenvriend, uitgenodigd="ja")

            return render_template("toegevoegd.html", toetevoegenvriend=toetevoegenvriend, lengte=lengte)

    return render_template("vriendtoevoegen.html", lengte=lengte)

@app.route("/toegevoegd", methods=["GET", "POST"])
@login_required
def toegevoegd():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    return render_template("toegevoegd.html", lengte=lengte)

@app.route("/vriendenlijst")
@login_required
def vriendenlijst():

    gebruikersnaam = gebruiker()
    vrienden = db.execute("SELECT van FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                           naar=gebruikersnaam, geaccepteerd="ja")
    verzoeken = verzoek()
    lengte = lengte_vv()

    return render_template("vriendenlijst.html", vrienden=vrienden, lengte=lengte)

@app.route("/verzoeken", methods=["GET", "POST"])
@login_required
def verzoeken():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    if request.method == "POST":
        accepteren = request.form.get("accepteren")
        weigerenn = request.form.get("weigeren")

        if not accepteren:
            weigeren = weigerenn[1:]
            db.execute("UPDATE verzoeken SET geaccepteerd=:geaccepteerd WHERE van=:van AND naar=:naar", geaccepteerd="nee",
                        van=weigeren, naar=gebruikersnaam)

            return redirect("/verzoeken")

        else:
            db.execute("UPDATE verzoeken SET geaccepteerd=:geaccepteerd WHERE van=:van AND naar=:naar", geaccepteerd="ja",
                        van=accepteren, naar=gebruikersnaam)

            return redirect("/verzoeken")

    return render_template("verzoeken.html", verzoeken=verzoeken, lengte=lengte)

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
@login_required
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

            if not session["user_id"]:
                return render_template("zoekresultaten.html", zoekresultaten=zoekresultaten)

            else:
                gebruikersnaam = gebruiker()
                verzoeken = verzoek()
                lengte = lengte_vv()

                return render_template("zoekresultaten.html", zoekresultaten=zoekresultaten, lengte=lengte)

        else:
            return apology("Iets ging mis")

@app.route("/zoekennon", methods=["GET", "POST"])
def zoekresultaat_non():

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

        else:
            return apology("Iets ging mis")

@app.route("/filminfo", methods=["GET", "POST"])
@login_required
def filminformatie():

    if request.method == "POST":
        tmdb_id = request.form.get("tmdb_id")

        # Alle informatie ophalen voor zoekresultaat (TMDb)
        from urllib.request import urlopen
        tmdb_url = str("https://api.themoviedb.org/3/movie/" + tmdb_id + "?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl")
        tmdb_response = json.loads(str((requests.get(tmdb_url).content).decode('UTF-8')))

        addtohistory(tmdb_id, tmdb_response)

        # Als er geen IMDb id genoemd wordt
        if tmdb_response["imdb_id"] == None or "tt" not in tmdb_response["imdb_id"]:
            omdb_response = None

        # Alle informatie ophalen voor zoekresultaat (OMDb)
        else:
            omdb_url = "http://www.omdbapi.com/?i=" + tmdb_response["imdb_id"] + "&apikey=be77e5d"
            omdb_response = json.loads(str((requests.get(omdb_url).content).decode('UTF-8')))

        gebruikersnaam = gebruiker()
        verzoeken = verzoek()
        lengte = lengte_vv()

        favorieten = db.execute("SELECT film_id FROM favorieten WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)
        alfavo = any([favoriet['film_id'] == tmdb_id for favoriet in favorieten])

        return render_template("filminformatie.html", tmdb=tmdb_response, omdb=omdb_response, alfavo=alfavo, lengte=lengte)

@app.route("/filminfo_non", methods=["GET", "POST"])
def filminformatie_non():

    if request.method == "POST":

        tmdb_id = request.form.get("tmdb_id")

        # Alle informatie ophalen voor zoekresultaat (TMDb)
        from urllib.request import urlopen
        tmdb_url = str("https://api.themoviedb.org/3/movie/" + tmdb_id + "?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl")
        tmdb_response = json.loads(str((requests.get(tmdb_url).content).decode('UTF-8')))

        # Als er geen IMDb id genoemd wordt
        if tmdb_response["imdb_id"] == None or "tt" not in tmdb_response["imdb_id"]:
            omdb_response = None

        # Alle informatie ophalen voor zoekresultaat (OMDb)
        else:
            omdb_url = "http://www.omdbapi.com/?i=" + tmdb_response["imdb_id"] + "&apikey=be77e5d"
            omdb_response = json.loads(str((requests.get(omdb_url).content).decode('UTF-8')))

        return render_template("filminformatie_non.html", tmdb=tmdb_response, omdb=omdb_response)

@app.route("/mijnprofiel")
@login_required
def mijnprofiel():
    "Pas je profiel aan"

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    return render_template("mijnprofiel.html", lengte=lengte)

@app.route("/wachtwoordvergeten", methods=["GET", "POST"])
def wachtwoordvergeten():
    if request.method == "POST":
        return render_template("wachtwoordveranderen.html")

    return render_template("wachtwoordvergeten.html")

@app.route("/wachtwoordveranderen", methods=["GET", "POST"])
def wachtwoordveranderen():
    """Verander wachtwoord"""

    if request.method == 'POST':

        if not request.form.get('gebruikersnaam'):
            return apology("Vul je gebruikersnaam in")

        # pak id uit database
        account = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                              gebruikersnaam=request.form.get('gebruikersnaam'))

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

        wachtwoordcheck = db.execute("SELECT wachtwoord FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                                      gebruikersnaam=account[0]["gebruikersnaam"])

        if pwd_context.verify(request.form.get("nieuw_wachtwoord"), wachtwoordcheck[0]["wachtwoord"]):
            return apology("Niet mogelijk om je huidige wachtwoord te kiezen")

        # maak een hash van het wachtwoord
        new_hash = pwd_context.hash(request.form.get("nieuw_wachtwoord"))
        # new_hash = CryptContext.hash(niet_hash)

        # update de gebruiker
        resultaat = db.execute("UPDATE gebruikers SET wachtwoord=:wachtwoord WHERE gebruikersnaam=:gebruikersnaam",
                                gebruikersnaam=request.form.get('gebruikersnaam'), wachtwoord=new_hash)

        if not resultaat:
            return apology("Iets ging fout...")

        return render_template("wachtwoordveranderd.html")

    else:
        return render_template("wachtwoordveranderen.html")

@app.route("/wachtwoordgebruikers", methods=["GET", "POST"])
@login_required
def wachtwoordgebruikers():
    """Verander wachtwoord"""

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    if request.method == 'POST':

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

        wachtwoordcheck = db.execute("SELECT wachtwoord FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                                      gebruikersnaam=account[0]["gebruikersnaam"])

        if pwd_context.verify(request.form.get("nieuw_wachtwoord"), wachtwoordcheck[0]["wachtwoord"]):
            return apology("Niet mogelijk om je huidige wachtwoord te kiezen")

        # maak een hash van het wachtwoord
        niet_hash = request.form.get("nieuw_wachtwoord")
        new_hash = pwd_context.hash(niet_hash)
        # new_hash = CryptContext.hash(niet_hash)

        # update de gebruiker
        resultaat = db.execute("UPDATE gebruikers SET wachtwoord=:wachtwoord WHERE id=:id",
                                id=session["user_id"], wachtwoord=new_hash)

        if not resultaat:
            return apology("Iets ging fout...")

        return render_template("wachtwoordveranderd.html", lengte=lengte)

    else:
        return render_template("wachtwoordgebruikers.html", lengte=lengte)

@app.route("/wachtwoordveranderd")
def wachtwoordveranderd():
    if session["user_id"] > 0:
        gebruikersnaam = gebruiker()
        verzoeken = verzoek()
        lengte = lengte_vv()

        return render_template("wachtwoordveranderd.html", lengte=lengte)

    return render_template("wachtwoordveranderd.html")


@app.route("/accountverwijderen", methods=["GET", "POST"])
@login_required
def accountverwijderen():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    if request.method == "POST":

        gebruikersnaam = gebruiker()

        wachtwoord = request.form.get("wachtwoord")
        print(wachtwoord)
        wachtwoord_herhaling = request.form.get("wachtwoord_herhaling")

        if not wachtwoord:
            return apology("Geef jouw wachtwoord op.")

        if not wachtwoord_herhaling:
            return apology("Geef herhaling van jouw wachtwoord op.")

        if wachtwoord != wachtwoord_herhaling:
            return apology("De bevestiging komt niet overeen met het wachtwoord.")

        wachtwoordcheck = db.execute("SELECT wachtwoord FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                                      gebruikersnaam=gebruikersnaam)

        if len(wachtwoordcheck) != 1 or not pwd_context.verify(request.form.get("wachtwoord"), wachtwoordcheck[0]["wachtwoord"]):
            return apology("Het opgegeven wachtwoord klopt niet")

        else:
            session.clear()

            db.execute("DELETE FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam", gebruikersnaam=gebruikersnaam)
            db.execute("DELETE FROM verzoeken WHERE naar=:naar OR van=:van", naar=gebruikersnaam, van=gebruikersnaam)

            return render_template("verwijderd.html", gebruikersnaam=gebruikersnaam, lengte=lengte)

    return render_template("accountverwijderen.html", lengte=lengte)

@app.route("/favorieten", methods=["GET", "POST"])
@login_required
def favorieten():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    favorieten = db.execute("SELECT * FROM favorieten WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)

    return render_template("favorieten.html", favorieten=favorieten, lengte=lengte)

@app.route("/addfavorite", methods=["POST"])
@login_required
def addfavorite():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    if request.method == "POST":

        gebruikersnaam = gebruiker()

        tmdb_id = request.form.get("favorieten")

        # Alle informatie ophalen voor zoekresultaat (TMDb)
        from urllib.request import urlopen
        tmdb_url = str( "https://api.themoviedb.org/3/movie/" + tmdb_id + "?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl")
        tmdb_response = json.loads(str((requests.get(tmdb_url).content).decode('UTF-8')))

        # Als er geen IMDb id genoemd wordt
        if tmdb_response["imdb_id"] == None or "tt" not in tmdb_response["imdb_id"]:
            omdb_response = None

        # Alle informatie ophalen voor zoekresultaat (OMDb)
        else:
            omdb_url = "http://www.omdbapi.com/?i=" + tmdb_response["imdb_id"] + "&apikey=be77e5d"
            omdb_response = json.loads(str((requests.get(omdb_url).content).decode('UTF-8')))

        favorieten = db.execute("SELECT film_id FROM favorieten WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)

        db.execute("INSERT INTO favorieten (gebruiker, film_id, titel, afbeelding) VALUES (:gebruiker, :film_id, :titel, :afbeelding)",
                    gebruiker=gebruikersnaam, film_id=tmdb_id, titel=tmdb_response["original_title"], afbeelding=tmdb_response["poster_path"])

        return render_template("addfavorite.html", tmdb=tmdb_response, omdb=omdb_response, favorieten=favorieten, lengte=lengte)

@app.route("/removefavorite", methods=["POST"])
@login_required
def removefavorite():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    if request.method == "POST":

        gebruikersnaam = gebruiker()

        tmdb_id = request.form.get("geenfavo")

        # Alle informatie ophalen voor zoekresultaat (TMDb)
        from urllib.request import urlopen
        tmdb_url = str( "https://api.themoviedb.org/3/movie/" + tmdb_id + "?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl")
        tmdb_response = json.loads(str((requests.get(tmdb_url).content).decode('UTF-8')))

        # Als er geen IMDb id genoemd wordt
        if tmdb_response["imdb_id"] == None or "tt" not in tmdb_response["imdb_id"]:
            omdb_response = None

        # Alle informatie ophalen voor zoekresultaat (OMDb)
        else:
            omdb_url = "http://www.omdbapi.com/?i=" + tmdb_response["imdb_id"] + "&apikey=be77e5d"
            omdb_response = json.loads(str((requests.get(omdb_url).content).decode('UTF-8')))

        db.execute("DELETE FROM favorieten WHERE gebruiker=:gebruiker AND film_id=:film_id",
                    gebruiker=gebruikersnaam, film_id=tmdb_id)

        return render_template("removefavorite.html", tmdb=tmdb_response, omdb=omdb_response, lengte=lengte)

@app.route("/historie", methods=["GET", "POST"])
@login_required
def historie():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    historie = db.execute("SELECT * FROM historie WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)

    if request.method == "POST":
        if len(historie) > 0:
            db.execute("DELETE FROM historie WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)
            return render_template("legehistorie.html", historie=historie, lengte=lengte)
        else:
            return apology("Je hebt geen kijkgeschiedenis")

    return render_template("historie.html", historie=historie, lengte=lengte)

@app.route("/legehistorie", methods=["GET", "POST"])
@login_required
def legehistorie():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    return render_template("legehistorie.html", lengte=lengte)

@app.route("/mijnkijklijst", methods=["GET", "POST"])
@login_required
def mijnkijklijst():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    return render_template("mijnkijklijst.html", lengte=lengte)

@app.route("/mijnlijsten", methods=["GET", "POST"])
@login_required
def mijnlijsten():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    return render_template("mijnlijsten.html", lengte=lengte)

@app.route("/checkins", methods=["GET", "POST"])
@login_required
def checkins():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()

    return render_template("checkins.html", lengte=lengte)