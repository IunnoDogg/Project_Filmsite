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
    verzoeken = db.execute("SELECT van FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd AND uitgenodigd=:uitgenodigd AND afgewezen=:afgewezen",
                            naar=gebruikersnaam, geaccepteerd="nee", uitgenodigd="ja", afgewezen="nee")

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

def tipslength():
    gebruikersnaam = gebruiker()

    tips = db.execute("SELECT van FROM aanbevelingen WHERE naar=:naar", naar=gebruikersnaam)

    if tips:
        tipslengte = len(tips)
        return tipslengte

    else:
        tipslengte = 0
        return tipslengte

def apology(message, code=400):
    """Renders message as an apology to user."""
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte


    return render_template("apology.html", top=code, bottom=message, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

def apologynon(message, code=400):
    """Renders message as an apology to user."""

    return render_template("apologynon.html", top=code, bottom=message)

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
        return apologynon("Geef een gebruikersnaam op.")

    # # ensure password was submitted
    # elif not request.form.get("email"):
    #     return apologynon("Geef een e-mailadres op.")

    # ensure password was submitted
    elif not request.form.get("wachtwoord"):
        return apologynon("Geef een wachtwoord op.")

    # ensure password-confirmation was submitted
    elif not request.form.get("wachtwoord-confirmatie"):
        return apologynon("Geef het wachtwoord nogmaals op.")

    # ensure password equals password confirmation
    if request.form.get("wachtwoord") != request.form.get("wachtwoord-confirmatie"):
        return apologynon("De bevestiging komt niet overeen met het wachtwoord.")

    # ensure the security question has been answered
    elif not request.form.get("veiligheidsvraag"):
        return apologynon("Beantwoord de veiligheidsvraag.")


@app.route("/layout")
@login_required
def layout():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    return render_template("layout.html", verzoeken=verzoeken, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/index")
@login_required
def index():
    from urllib.request import urlopen
    popular = json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl&sort_by=popularity.desc&page=1&with_original_language=nl").content).decode('UTF-8')))
    new = json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&year=" + str(datetime.date.today().year) + "&with_original_language=nl").content).decode('UTF-8')))

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    return render_template("index.html", popular=popular["results"], new=new["results"], lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/")
def homepage():
    # Haal populaire films op
    from urllib.request import urlopen
    popular = json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&language=nl&sort_by=popularity.desc&page=1&with_original_language=nl").content).decode('UTF-8')))
    new = json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&year=" + str(datetime.date.today().year) + "&with_original_language=nl").content).decode('UTF-8')))

    return render_template("homepage.html", popular=popular["results"], new=new["results"])

@app.route("/wachtwoord")
def wachtwoord():
    return render_template("wachtwoord.html")

@app.route("/overons")
@login_required
def overons():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte = tipslength()
    totaal = tipslengte + lengte
    return render_template("overons.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/overonsz")
def overonsz():
    return render_template("overonsz.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":

        registerform()

        # hash the password
        wachtwoord = pwd_context.hash(request.form.get("wachtwoord"))

        # insert the user into the database
        result = db.execute("INSERT INTO gebruikers (gebruikersnaam, wachtwoord, veiligheidsvraag) VALUES \
                            (:gebruikersnaam, :wachtwoord, :veiligheidsvraag)",
                            gebruikersnaam=request.form.get("gebruikersnaam"), wachtwoord=wachtwoord,
                            veiligheidsvraag=request.form.get("veiligheidsvraag"))

        if not result:
            return apologynon("username already exists")

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

        if not request.form.get("gebruiker-inloggen"):
            return apologynon("Geef een gebruikersnaam op")

        if not request.form.get("wachtwoord-inloggen"):
            return apologynon("Geef een wachtwoord op")

        rows = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                          gebruikersnaam=request.form.get("gebruiker-inloggen"))

        # rows1 = db.execute("SELECT * FROM gebruikers WHERE email = :email",
        #                   email=request.form.get("gebruiker-inloggen"))

        # if len(rows) == 0:
        #     if len(rows1) != 1 or not pwd_context.verify(request.form.get("wachtwoord-inloggen"), rows1[0]["wachtwoord"]):
        #         return apologynon("Ongeldige email en/of wachtwoord")

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("wachtwoord-inloggen"), rows[0]["wachtwoord"]):
            return apologynon("Ongeldige gebruikersnaam en/of wachtwoord")

        # remember which user has logged in
        if len(rows) > 0:
            session["user_id"] = rows[0]["id"]

        # elif len(rows1) > 0:
        #     session["user_id"] = rows1[0]["id"]

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
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    if request.method == "POST":

        toetevoegenvriend = ophalen("vriend")

        vriend = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                          gebruikersnaam=toetevoegenvriend)

        if not vriend:
            return apology("Deze gebruikersnaam bestaat niet.")

        if toetevoegenvriend == gebruikersnaam:
            return apology("Je kan jezelf niet toevoegen")

        alvrienden = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                van=toetevoegenvriend, naar=gebruikersnaam, geaccepteerd="ja")

        alvriendenn = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                naar=toetevoegenvriend, van=gebruikersnaam, geaccepteerd="ja")

        tekstt = "Je bent al vrienden met " + toetevoegenvriend

        if alvrienden or alvriendenn:
            return apology(tekstt)

        aluitgenodigdvriend = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND uitgenodigd=:uitgenodigd AND geaccepteerd=:geaccepteerd AND afgewezen=:afgewezen",
                                          van=toetevoegenvriend, naar=gebruikersnaam, uitgenodigd="ja", geaccepteerd="nee", afgewezen="nee")

        aluitgenodigdjij = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND uitgenodigd=:uitgenodigd AND geaccepteerd=:geaccepteerd AND afgewezen=:afgewezen",
                                      van=gebruikersnaam, naar=toetevoegenvriend, uitgenodigd="ja", geaccepteerd="nee", afgewezen="nee")

        if aluitgenodigdvriend or aluitgenodigdjij:
            return apology("Deze gebruiker heeft je al uitgenodigd of andersom")

        else:
            now = datetime.datetime.now()
            date = now.strftime("%d-%m-%Y")
            db.execute("INSERT INTO verzoeken (van, naar, geaccepteerd, uitgenodigd, afgewezen, datum) VALUES (:van, :naar, :geaccepteerd, :uitgenodigd, :afgewezen, :datum)",
                        van=gebruikersnaam, naar=toetevoegenvriend, geaccepteerd="nee", uitgenodigd="ja", afgewezen="nee", datum=date)

            return render_template("toegevoegd.html", toetevoegenvriend=toetevoegenvriend, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

    return render_template("vriendtoevoegen.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/toegevoegd", methods=["GET", "POST"])
@login_required
def toegevoegd():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    return render_template("toegevoegd.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/vriendenlijst")
@login_required
def vriendenlijst():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    vrienden = db.execute("SELECT * FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                           naar=gebruikersnaam, geaccepteerd="ja")

    vrienden1 = db.execute("SELECT * FROM verzoeken WHERE van=:van AND geaccepteerd=:geaccepteerd",
                           van=gebruikersnaam, geaccepteerd="ja")

    if vrienden:
        a = len(vrienden)

    else:
        a = 0

    if vrienden1:
        b = len(vrienden1)

    else:
        b = 0


    return render_template("vriendenlijst.html", vrienden=vrienden, vrienden1=vrienden1, lengte=lengte, tipslengte=tipslengte, totaal=totaal, a=a, b=b)



@app.route("/verzoeken", methods=["GET", "POST"])
@login_required
def verzoeken():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    if request.method == "POST":
        accepteren = request.form.get("accepteren")
        weigerenn = request.form.get("weigeren")

        if not accepteren:
            weigeren = weigerenn[1:]
            now = datetime.datetime.now()
            date = now.strftime("%d-%m-%Y")

            db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar", naar=gebruikersnaam, van=weigeren)
            db.execute("INSERT INTO verzoeken (van, naar, geaccepteerd, uitgenodigd, afgewezen, datum) VALUES (:van, :naar, :geaccepteerd, :uitgenodigd, :afgewezen, :datum)",
                        van=weigeren, naar=gebruikersnaam, geaccepteerd="nee", uitgenodigd="ja", afgewezen="ja", datum=date)

            return render_template("geweigerd.html", verzoeken=verzoeken, lengte=lengte, tipslengte=tipslengte, totaal=totaal, weigeren=weigeren)

        elif accepteren:
            now = datetime.datetime.now()
            date = now.strftime("%d-%m-%Y")
            # db.execute("UPDATE verzoeken SET geaccepteerd=:geaccepteerd AND datum=:datum WHERE van=:van AND naar=:naar",
            #             geaccepteerd="piemel", datum=date, van=accepteren, naar=gebruikersnaam)
            db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar", naar=gebruikersnaam, van=accepteren)
            db.execute("INSERT INTO verzoeken (van, naar, geaccepteerd, datum) VALUES (:van, :naar, :geaccepteerd, :datum)",
                        van=accepteren, naar=gebruikersnaam, geaccepteerd="ja", datum=date)

            return render_template("geaccepteerd.html", verzoeken=verzoeken, lengte=lengte, tipslengte=tipslengte, totaal=totaal, accepteren=accepteren)

    return render_template("verzoeken.html", verzoeken=verzoeken, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/zoeken", methods=["GET", "POST"])
@login_required
def zoekresultaat():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    if request.method == "POST":
        searchterm = request.form.get("zoekterm")

        if not searchterm:
            return apology("Geen zoekterm")
        elif results_per_page(searchterm, pagenr=1) == False:
            return apology("Geen resultaten")
        else:
            return render_template("zoekresultaten.html", zoekresultaten=total_results(searchterm), lengte=lengte, tipslengte=tipslengte, totaal=totaal)


@app.route("/zoekennon", methods=["GET", "POST"])
def zoekresultaat_non():

    if request.method == "POST":
        searchterm = request.form.get("zoekterm")

        if not searchterm:
            return apology("Geen zoekterm")
        elif results_per_page(searchterm, pagenr=1) == False:
            return apology("Geen resultaten")
        else:
            return render_template("zoekresultaten.html", zoekresultaten=total_results(searchterm))

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
        tipslengte=tipslength()
        totaal = tipslengte + lengte

        vrienden = db.execute("SELECT * FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                           naar=gebruikersnaam, geaccepteerd="ja")

        vrienden1 = db.execute("SELECT * FROM verzoeken WHERE van=:van AND geaccepteerd=:geaccepteerd",
                               van=gebruikersnaam, geaccepteerd="ja")

        if vrienden:
            a = len(vrienden)

        else:
            a = 0

        if vrienden1:
            b = len(vrienden1)

        else:
            b = 0

        favorieten = db.execute("SELECT film_id FROM favorieten WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)
        alfavo = any([favoriet['film_id'] == tmdb_id for favoriet in favorieten])

        lijsten = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gez_lijst IS NULL AND nieuwe_lijst=:nieuwe_lijst",
                              gebruiker=gebruikersnaam, nieuwe_lijst="ja")

        lijsten2 = db.execute("SELECT * FROM lijsten WHERE gez_lijst IS NOT NULL AND gebruiker=:gebruiker AND nieuwe_lijst=:nieuwe_lijst",
                                gebruiker=gebruikersnaam, nieuwe_lijst="ja")

        lijsten3 = db.execute("SELECT * FROM lijsten WHERE gez_lijst IS NOT NULL AND gebruiker2=:gebruiker2 AND nieuwe_lijst=:nieuwe_lijst",
                                gebruiker2=gebruikersnaam, nieuwe_lijst="ja")

        checkins = db.execute("SELECT film_id FROM checkins WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)
        alcheckin = any([checkin['film_id'] == tmdb_id for checkin in checkins])

        return render_template("filminformatie.html", tmdb=tmdb_response, omdb=omdb_response, alfavo=alfavo, lengte=lengte,
        tipslengte=tipslengte, totaal=totaal, vrienden=vrienden, vrienden1=vrienden1, a=a, b=b, lijsten=lijsten,
        lijsten2=lijsten2, lijsten3=lijsten3, alcheckin=alcheckin)

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
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    vrienden = db.execute("SELECT * FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                           naar=gebruikersnaam, geaccepteerd="ja")

    vrienden1 = db.execute("SELECT * FROM verzoeken WHERE van=:van AND geaccepteerd=:geaccepteerd",
                           van=gebruikersnaam, geaccepteerd="ja")

    if vrienden:
        a = len(vrienden)

    else:
        a = 0

    if vrienden1:
        b = len(vrienden1)

    else:
        b = 0

    favorieten = db.execute("SELECT * FROM favorieten WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)
    checkins = db.execute("SELECT * FROM checkins WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)
    historie = db.execute("SELECT * FROM historie WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)
    aanbevelingen = db.execute("SELECT * FROM aanbevelingen WHERE naar=:naar", naar=gebruikersnaam)
    aanbevelingenvan = db.execute("SELECT * FROM aanbevelingen WHERE van=:van", van=gebruikersnaam)

    lijsten = db.execute("SELECT lijstnaam FROM lijsten WHERE gebruiker=:gebruiker AND gez_lijst IS NULL AND nieuwe_lijst=:nieuwe_lijst",
                        gebruiker=gebruikersnaam, nieuwe_lijst="ja")
    lijsten2 = db.execute("SELECT * FROM lijsten WHERE gez_lijst IS NOT NULL AND gebruiker=:gebruiker", gebruiker=gebruikersnaam)
    lijsten3 = db.execute("SELECT * FROM lijsten WHERE gez_lijst IS NOT NULL AND gebruiker2=:gebruiker2", gebruiker2=gebruikersnaam)

    return render_template("mijnprofiel.html", lengte=lengte, tipslengte=tipslengte,
    totaal=totaal, vrienden=vrienden, vrienden1=vrienden1, a=a, b=b, favorieten=favorieten, historie=historie,
    lijsten=lijsten, lijsten2=lijsten2, lijsten3=lijsten3, aanbevelingen=aanbevelingen, checkins=checkins,
    aanbevelingenvan=aanbevelingenvan, gebruikersnaam=gebruikersnaam)

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
            return apologynon("Vul je gebruikersnaam in")

        # pak id uit database
        account = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                              gebruikersnaam=request.form.get('gebruikersnaam'))

        # check of een nieuw wachtwoord is ingevuld
        if not request.form.get("nieuw_wachtwoord"):
            return apologynon("Vul een nieuw wachtwoord in")

        # check of het nieuwe wachtwoord is herhaald
        if not request.form.get("wachtwoord_herhaling"):
            return apologynon("Herhaal je nieuwe wachtwoord")

        # controleer of beide wachtwoorden overeenkomen
        if request.form.get("nieuw_wachtwoord") != request.form.get("wachtwoord_herhaling"):
            return apologynon("De wachtwoorden komen niet overeen")

        # beantwoord de veiligheidsvraag
        if not request.form.get('veiligheidsvraag'):
            return apologynon("Beantwoord de veiligheidsvraag.")

        # bevestig of het antwoord klopt
        if len(account) != 1 or request.form.get('veiligheidsvraag') != account[0]['veiligheidsvraag']:
            return apologynon("Het antwoord op de veiligheidsvraag klopt niet!")

        wachtwoordcheck = db.execute("SELECT wachtwoord FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                                      gebruikersnaam=account[0]["gebruikersnaam"])

        if pwd_context.verify(request.form.get("nieuw_wachtwoord"), wachtwoordcheck[0]["wachtwoord"]):
            return apologynon("Niet mogelijk om je huidige wachtwoord te kiezen")

        # maak een hash van het wachtwoord
        new_hash = pwd_context.hash(request.form.get("nieuw_wachtwoord"))
        # new_hash = CryptContext.hash(niet_hash)

        # update de gebruiker
        resultaat = db.execute("UPDATE gebruikers SET wachtwoord=:wachtwoord WHERE gebruikersnaam=:gebruikersnaam",
                                gebruikersnaam=request.form.get('gebruikersnaam'), wachtwoord=new_hash)

        if not resultaat:
            return apologynon("Iets ging fout...")

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
    tipslengte=tipslength()
    totaal = tipslengte + lengte

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

        return render_template("wachtwoordveranderd.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal)

    else:
        return render_template("wachtwoordgebruikers.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/wachtwoordveranderd")
def wachtwoordveranderd():
    if session["user_id"] > 0:
        gebruikersnaam = gebruiker()
        verzoeken = verzoek()
        lengte = lengte_vv()
        tipslengte=tipslength()
        totaal = tipslengte + lengte

        return render_template("wachtwoordveranderd.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal)

    return render_template("wachtwoordveranderd.html")


@app.route("/accountverwijderen", methods=["GET", "POST"])
@login_required
def accountverwijderen():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    if request.method == "POST":

        gebruikersnaam = gebruiker()

        wachtwoord = request.form.get("wachtwoord")
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

            return render_template("verwijderd.html", gebruikersnaam=gebruikersnaam, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

    return render_template("accountverwijderen.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/favorieten", methods=["GET", "POST"])
@login_required
def favorieten():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    favorieten = db.execute("SELECT * FROM favorieten WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)

    return render_template("favorieten.html", favorieten=favorieten, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/addfavorite", methods=["POST"])
@login_required
def addfavorite():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

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

        return render_template("addfavorite.html", tmdb=tmdb_response, omdb=omdb_response, favorieten=favorieten, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/removefavorite", methods=["POST"])
@login_required
def removefavorite():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

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

        return render_template("removefavorite.html", tmdb=tmdb_response, omdb=omdb_response, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/historie", methods=["GET", "POST"])
@login_required
def historie():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    historie = db.execute("SELECT * FROM historie WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)

    if request.method == "POST":
        if len(historie) > 0:
            db.execute("DELETE FROM historie WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)
            return render_template("legehistorie.html", historie=historie, lengte=lengte, tipslengte=tipslengte, totaal=totaal)
        else:
            return apology("Je hebt geen kijkgeschiedenis")

    return render_template("historie.html", historie=historie, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/legehistorie", methods=["GET", "POST"])
@login_required
def legehistorie():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    return render_template("legehistorie.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/mijnlijsten", methods=["GET", "POST"])
@login_required
def mijnlijsten():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    vrienden = db.execute("SELECT * FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                           naar=gebruikersnaam, geaccepteerd="ja")

    vrienden1 = db.execute("SELECT * FROM verzoeken WHERE van=:van AND geaccepteerd=:geaccepteerd",
                           van=gebruikersnaam, geaccepteerd="ja")

    if vrienden:
        a = len(vrienden)

    else:
        a = 0

    if vrienden1:
        b = len(vrienden1)

    else:
        b = 0

    lijsten = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gez_lijst IS NULL AND nieuwe_lijst=:nieuwe_lijst",
                        gebruiker=gebruikersnaam, nieuwe_lijst="ja")
    lijsten2 = db.execute("SELECT * FROM lijsten WHERE gez_lijst IS NOT NULL AND gebruiker=:gebruiker AND nieuwe_lijst=:nieuwe_lijst",
                        gebruiker=gebruikersnaam, nieuwe_lijst="ja")
    lijsten3 = db.execute("SELECT * FROM lijsten WHERE gez_lijst IS NOT NULL AND gebruiker2=:gebruiker2 AND nieuwe_lijst=:nieuwe_lijst",
                        gebruiker2=gebruikersnaam, nieuwe_lijst="ja")

    return render_template("mijnlijsten.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal, vrienden=vrienden,
                            vrienden1=vrienden1, a=a, b=b, lijsten=lijsten, lijsten2=lijsten2, lijsten3=lijsten3)

@app.route("/checkins", methods=["GET", "POST"])
@login_required
def checkins():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    checkins = db.execute("SELECT * FROM checkins WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)

    return render_template("checkins.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal, checkins=checkins)

@app.route("/tipvriend", methods=["POST"])
@login_required
def tipvriend():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    if request.method == "POST":

        vriend = ophalen("tipvriend")
        tmdb_id = ophalen("buttonvriend")

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

        check = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            van=gebruikersnaam, naar=vriend, geaccepteerd="ja")

        check2 = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            naar=gebruikersnaam, van=vriend, geaccepteerd="ja")

        if check or check2:
            tipcheck = db.execute("SELECT * FROM aanbevelingen WHERE van=:van AND naar=:naar AND film_id=:film_id",
                                   van=gebruikersnaam, naar=vriend, film_id=tmdb_id)

            if tipcheck:
                return apology("Je hebt deze gebruiker deze film al aanbevolen")

            tips = db.execute("INSERT INTO aanbevelingen (van, naar, film_id, titel, afbeelding) VALUES (:van, :naar, :film_id, :titel, :afbeelding)",
                        van=gebruikersnaam, naar=vriend, film_id=tmdb_id, titel=tmdb_response["original_title"], afbeelding=tmdb_response["poster_path"])

            aanbevelingen = db.execute("SELECT * FROM aanbevelingen WHERE van=:van", van=gebruikersnaam)

            return render_template("index.html", popular=(popular_films())["results"], new=(new_films())["results"], tmdb=tmdb_response,
            omdb=omdb_response, favorieten=favorieten, lengte=lengte, tipslengte=tipslengte, totaal=totaal, aanbevelingen=aanbevelingen)

        else:
            return apology("Deze gebruiker is geen vriend van je")

@app.route("/tips", methods=["GET", "POST"])
@login_required
def tips():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte
    aanbevelingen = db.execute("SELECT * FROM aanbevelingen WHERE naar=:naar", naar=gebruikersnaam)
    vrienden = db.execute("SELECT * FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                           naar=gebruikersnaam, geaccepteerd="ja")

    vrienden1 = db.execute("SELECT * FROM verzoeken WHERE van=:van AND geaccepteerd=:geaccepteerd",
                           van=gebruikersnaam, geaccepteerd="ja")

    if vrienden:
        a = len(vrienden)

    else:
        a = 0

    if vrienden1:
        b = len(vrienden1)

    else:
        b = 0
    return render_template("tips.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal, aanbevelingen=aanbevelingen,
                            vrienden=vrienden, vrienden1=vrienden1, a=a, b=b)

@app.route("/vriendinfo", methods=["POST"])
@login_required
def vriendinfo():
    if request.method == "POST":
        gebruikersnaam = gebruiker()
        lengte = lengte_vv()
        tipslengte=tipslength()
        totaal = tipslengte + lengte

        profiel = request.form.get("profiel")

        if profiel == None:
            profiel = request.form.get("profiel1")

        favorieten = db.execute("SELECT * FROM favorieten WHERE gebruiker=:gebruiker", gebruiker=profiel)
        checkins = db.execute("SELECT * FROM checkins WHERE gebruiker=:gebruiker", gebruiker=profiel)
        historie = db.execute("SELECT * FROM historie WHERE gebruiker=:gebruiker", gebruiker=profiel)
        vrienden = db.execute("SELECT * FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                                naar=profiel, geaccepteerd="ja")

        vrienden1 = db.execute("SELECT * FROM verzoeken WHERE van=:van AND geaccepteerd=:geaccepteerd",
                               van=profiel, geaccepteerd="ja")

        aanbevelingen = db.execute("SELECT * FROM aanbevelingen WHERE naar=:naar", naar=profiel)
        aanbevelingenvan = db.execute("SELECT * FROM aanbevelingen WHERE van=:van", van=profiel)

    return render_template("vriendinfo.html", favorieten=favorieten, lengte=lengte, tipslengte=tipslengte, totaal=totaal,
                            profiel=profiel, vriend=vriend, checkins=checkins, historie=historie, vrienden=vrienden,
                            vrienden1=vrienden1, aanbevelingen=aanbevelingen, aanbevelingenvan=aanbevelingenvan)

@app.route("/verwijdervriendredirect", methods=["POST"])
@login_required
def verwijdervriendredirect():
    if request.method == "POST":
        gebruikersnaam = gebruiker()
        verzoeken = verzoek()
        lengte = lengte_vv()
        tipslengte=tipslength()
        totaal = tipslengte + lengte

        vriend = request.form.get("verwijder")
        if not vriend:
            vriend = request.form.get("verwijder1")

    return render_template("verwijdervriendredirect.html", vriend=vriend, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/verwijdervriend", methods=["POST"])
@login_required
def verwijdervriend():
    if request.method == "POST":
        gebruikersnaam = gebruiker()
        verzoeken = verzoek()
        lengte = lengte_vv()
        tipslengte=tipslength()
        totaal = tipslengte + lengte

        vriend = request.form.get("verwijder")
        vriendd = request.form.get("verwijder1")

        if vriend:
            vriendcheck = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                     naar=gebruikersnaam, van=vriend, geaccepteerd="ja")

            vriendcheckk = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                      van=gebruikersnaam, naar=vriend, geaccepteerd="ja")

            if vriendcheck:
                db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            naar=gebruikersnaam, van=vriend, geaccepteerd="ja")

            elif vriendcheckk:
                db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            van=gebruikersnaam, naar=vriend, geaccepteerd="ja")

        elif vriendd:
            vriendcheck = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                      naar=gebruikersnaam, van=vriendd, geaccepteerd="ja")

            vriendcheckk = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                      van=gebruikersnaam, naar=vriendd, geaccepteerd="ja")

            if vriendcheck:
                db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            naar=gebruikersnaam, van=vriendd, geaccepteerd="ja")

            elif vriendcheckk:
                db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            van=gebruikersnaam, naar=vriendd, geaccepteerd="ja")

        return render_template("verwijderdvriend.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/lijstgemaakt", methods=["POST"])
@login_required
def lijstgemaakt():
    if request.method == "POST":
        gebruikersnaam = gebruiker()
        verzoeken = verzoek()
        lengte = lengte_vv()
        tipslengte=tipslength()
        totaal = tipslengte + lengte

        lijstnaam = request.form.get("lijstnaam")
        x = lijstnaam + "_" + gebruikersnaam

        check = db.execute("SELECT * FROM lijsten WHERE lijstnaam=:lijstnaam AND gebruiker=:gebruiker AND gebruiker2 IS NULL",
                            lijstnaam=lijstnaam, gebruiker=gebruikersnaam)
        if check:
            tekst = "Je hebt al een lijst die " + lijstnaam + " heet"
            return apology(tekst)

        else:
            db.execute("INSERT INTO lijsten (gebruiker, lijstnaam, nieuwe_lijst) VALUES (:gebruiker, :lijstnaam, :nieuwe_lijst)",
                    gebruiker=gebruikersnaam, lijstnaam=lijstnaam, nieuwe_lijst="ja")

        return render_template("lijstgemaakt.html", lengte=lengte, tipslengte=tipslengte, lijstnaam=lijstnaam, totaal=totaal)

@app.route("/gezamenlijkelijstgemaakt", methods=["POST"])
@login_required
def gezamenlijkelijstgemaakt():
    if request.method == "POST":
        gebruikersnaam = gebruiker()
        verzoeken = verzoek()
        lengte = lengte_vv()
        tipslengte=tipslength()
        totaal = tipslengte + lengte

        lijstnaam = request.form.get("gez_lijstnaam")
        vriend = request.form.get("vriendvan")
        vriend2 = request.form.get("vriendnaar")

        if vriend:
            check1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
                                      gebruiker=gebruikersnaam, gebruiker2=vriend, lijstnaam=lijstnaam)

            check2 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
                                      gebruiker2=gebruikersnaam, gebruiker=vriend, lijstnaam=lijstnaam)

            if check1 or check2:
                tekst = "Je hebt al een lijst die " + lijstnaam + " heet met deze vriend"
                return apology(tekst)

            else:
                db.execute("INSERT INTO lijsten (gebruiker, lijstnaam, gebruiker2, gez_lijst, nieuwe_lijst) VALUES (:gebruiker, :lijstnaam, :gebruiker2, :gez_lijst, :nieuwe_lijst)",
                            gebruiker=gebruikersnaam, lijstnaam=lijstnaam, gebruiker2=vriend, gez_lijst="ja", nieuwe_lijst="ja")


        if vriend2:
            check1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
                                      gebruiker=gebruikersnaam, gebruiker2=vriend2, lijstnaam=lijstnaam)

            check2 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
                                      gebruiker2=gebruikersnaam, gebruiker=vriend2, lijstnaam=lijstnaam)

            if check1 or check2:
                tekst = "Je hebt al een lijst die " + lijstnaam + " heet met deze vriend"
                return apology(tekst)

            else:
                db.execute("INSERT INTO lijsten (gebruiker, lijstnaam, gebruiker2, gez_lijst, nieuwe_lijst) VALUES (:gebruiker, :lijstnaam, :gebruiker2, :gez_lijst, :nieuwe_lijst)",
                            gebruiker=gebruikersnaam, lijstnaam=lijstnaam, gebruiker2=vriend2, gez_lijst="ja", nieuwe_lijst="ja")

        return render_template("gezamenlijkelijstgemaakt.html", lengte=lengte, tipslengte=tipslengte, lijstnaam=lijstnaam, totaal=totaal)

@app.route("/lijst", methods=["POST"])
@login_required
def lijst():
    if request.method == "POST":
        gebruikersnaam = gebruiker()
        verzoeken = verzoek()
        lengte = lengte_vv()
        tipslengte=tipslength()
        totaal = tipslengte + lengte

        lijst = request.form.get("button")
        lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND nieuwe_lijst IS NULL",
                                gebruiker=gebruikersnaam, lijstnaam=lijst)

        return render_template("lijst.html", lengte=lengte, tipslengte=tipslengte, lijst=lijst, lijstinfo=lijstinfo, totaal=totaal)

@app.route("/gezlijst", methods=["POST"])
@login_required
def gezlijst():
    if request.method == "POST":
        gebruikersnaam = gebruiker()
        verzoeken = verzoek()
        lengte = lengte_vv()
        tipslengte=tipslength()
        totaal = tipslengte + lengte

        lijstnaam = request.form.get("button")
        vriend = request.form.get("vriend")

        lijsten1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam AND nieuwe_lijst IS NULL",
                            gebruiker=gebruikersnaam, gebruiker2=vriend, lijstnaam=lijstnaam)

        lijsten2 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam AND nieuwe_lijst IS NULL",
                            gebruiker2=gebruikersnaam, gebruiker=vriend, lijstnaam=lijstnaam)

        return render_template("gezlijst.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal, lijsten1=lijsten1, lijsten2=lijsten2, lijstnaam=lijstnaam, vriend=vriend)

@app.route("/addcheckins", methods=["POST"])
@login_required
def addcheckins():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

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

        checkins = db.execute("SELECT film_id FROM checkins WHERE gebruiker=:gebruiker", gebruiker=gebruikersnaam)

        db.execute("INSERT INTO checkins (gebruiker, film_id, titel, afbeelding) VALUES (:gebruiker, :film_id, :titel, :afbeelding)",
                    gebruiker=gebruikersnaam, film_id=tmdb_id, titel=tmdb_response["original_title"], afbeelding=tmdb_response["poster_path"])

        return render_template("addcheckins.html", tmdb=tmdb_response, omdb=omdb_response, checkins=checkins, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/removecheckins", methods=["POST"])
@login_required
def removecheckins():

    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    if request.method == "POST":

        gebruikersnaam = gebruiker()

        tmdb_id = request.form.get("geencheckin")

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

        db.execute("DELETE FROM checkins WHERE gebruiker=:gebruiker AND film_id=:film_id",
                    gebruiker=gebruikersnaam, film_id=tmdb_id)

        return render_template("removecheckins.html", tmdb=tmdb_response, omdb=omdb_response, lengte=lengte, tipslengte=tipslengte, totaal=totaal)

@app.route("/addtolist", methods=["POST"])
@login_required
def addtolist():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    if request.method == "POST":

        tmdb_id = request.form.get("buttonfilm")
        lijst = request.form.get("lijst")

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

        lijstnaam = lijst.split('|')[0]

        if len(lijst) == len(lijstnaam):
            lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND film_id=:film_id AND titel=:titel AND afbeelding=:afbeelding AND lijstnaam=:lijstnaam AND gez_lijst IS NULL AND nieuwe_lijst IS NULL",
                                    gebruiker=gebruikersnaam, film_id=tmdb_id, titel=tmdb_response["original_title"],
                                    afbeelding=tmdb_response["poster_path"], lijstnaam=lijstnaam)

            if lijstinfo:
                tekst = "Deze film staat al in je lijst: " + lijstnaam
                return apology(tekst)

            db.execute("INSERT INTO lijsten (gebruiker, film_id, titel, afbeelding, lijstnaam) VALUES (:gebruiker, :film_id, :titel, :afbeelding, :lijstnaam)",
                        gebruiker=gebruikersnaam, film_id=tmdb_id, titel=tmdb_response["original_title"],
                        afbeelding=tmdb_response["poster_path"], lijstnaam=lijstnaam)

            return render_template("addtolist.html", tmdb=tmdb_response, omdb=omdb_response, lengte=lengte, tipslengte=tipslengte,
                                        totaal=totaal, lijstnaam=lijstnaam)

        else:
            vriend = lijst.split('|')[1]
            lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND film_id=:film_id AND titel=:titel AND afbeelding=:afbeelding AND lijstnaam=:lijstnaam AND gez_lijst IS NULL AND nieuwe_lijst IS NULL AND gebruiker2=:gebruiker2",
                                    gebruiker=gebruikersnaam, film_id=tmdb_id, titel=tmdb_response["original_title"],
                                    afbeelding=tmdb_response["poster_path"], lijstnaam=lijstnaam, gebruiker2=vriend)

            if lijstinfo:

                tekst = "Deze film staat al in je gezamenlijke lijst: " + lijstnaam + "met:" + vriend
                return apology(tekst)

            if not lijstinfo:

                lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND film_id=:film_id AND titel=:titel AND afbeelding=:afbeelding AND lijstnaam=:lijstnaam AND gez_lijst IS NULL AND nieuwe_lijst IS NULL AND gebruiker2=:gebruiker2",
                                        gebruiker=vriend, film_id=tmdb_id, titel=tmdb_response["original_title"],
                                        afbeelding=tmdb_response["poster_path"], lijstnaam=lijstnaam, gebruiker2=gebruikersnaam)

                if lijstinfo:
                    tekst = "Deze film staat al in je gezamenlijke lijst: " + lijstnaam + "met:" + vriend
                    return apology(tekst)

                else:
                    db.execute("INSERT INTO lijsten (gebruiker, film_id, gebruiker2, titel, afbeelding, lijstnaam) VALUES (:gebruiker, :film_id, :gebruiker2, :titel, :afbeelding, :lijstnaam)",
                    gebruiker=gebruikersnaam, film_id=tmdb_id, titel=tmdb_response["original_title"],
                    afbeelding=tmdb_response["poster_path"], lijstnaam=lijstnaam, gebruiker2=vriend)

                    return render_template("addtolist.html", tmdb=tmdb_response, omdb=omdb_response, lengte=lengte, tipslengte=tipslengte,
                                                totaal=totaal, lijstnaam=lijstnaam, vriend=vriend)

@app.route("/removelist", methods=["POST"])
@login_required
def removelist():

    gebruikersnaam = gebruiker()
    lengte = lengte_vv()
    tipslengte=tipslength()
    totaal = tipslengte + lengte

    if request.method == "POST":

        lijstnaam = request.form.get("lijstnaam")
        vriend = request.form.get("vriend")

        if not vriend:
            db.execute("DELETE FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND gez_lijst IS NULL",
                        gebruiker=gebruikersnaam, lijstnaam=lijstnaam)

            return render_template("removelist.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal, lijstnaam=lijstnaam)

        else:
            check1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND gebruiker2=:gebruiker2",
                                gebruiker=gebruikersnaam, lijstnaam=lijstnaam, gebruiker2=vriend)

            if check1:
                db.execute("DELETE FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
                            gebruiker=gebruikersnaam, gebruiker2=vriend, lijstnaam=lijstnaam)

                return render_template("removelist.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal, lijstnaam=lijstnaam, vriend=vriend)

            if not check1:
                check1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND gebruiker2=:gebruiker2",
                                    gebruiker2=gebruikersnaam, lijstnaam=lijstnaam, gebruiker=vriend)

                db.execute("DELETE FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
                            gebruiker2=gebruikersnaam, gebruiker=vriend, lijstnaam=lijstnaam)

                return render_template("removelist.html", lengte=lengte, tipslengte=tipslengte, totaal=totaal, lijstnaam=lijstnaam, vriend=vriend)