from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import datetime, requests, json, xml.etree.ElementTree, urllib
from helpers import *
from API import *

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

@app.route("/layout")
@login_required
def layout():
    return render_template("layout.html", lengte = lengte_vv(), tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

@app.route("/index")
@login_required
def index():
    return render_template("index.html", popular=popular_films()["results"], new=new_films()["results"], lengte = lengte_vv(),
    tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

@app.route("/")
def homepage():
    return render_template("homepage.html", popular=popular_films()["results"], new=new_films()["results"])

@app.route("/wachtwoord")
def wachtwoord():
    return render_template("wachtwoord.html")

@app.route("/overons")
@login_required
def overons():
    return render_template("overons.html", lengte = lengte_vv(), tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

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
        result = db.execute("INSERT INTO gebruikers (gebruikersnaam, wachtwoord, email, veiligheidsvraag) VALUES \
                            (:gebruikersnaam, :wachtwoord, :email, :veiligheidsvraag)",
                            gebruikersnaam=request.form.get("gebruikersnaam"), wachtwoord=wachtwoord,
                            veiligheidsvraag=request.form.get("veiligheidsvraag"), email="niet meer nodig")

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

        loginform()

        rows = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                          gebruikersnaam=request.form.get("gebruiker-inloggen"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("wachtwoord-inloggen"), rows[0]["wachtwoord"]):
            return apologynon("Ongeldige gebruikersnaam en/of wachtwoord")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

        toetevoegenvriend = ophalen("vriend")
        gebruikersnaam = gebruiker()
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

        aluitgenodigdvriend = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND uitgenodigd=:uitgenodigd \
                                          AND geaccepteerd=:geaccepteerd AND afgewezen=:afgewezen",
                                          van=toetevoegenvriend, naar = gebruikersnaam, uitgenodigd="ja",
                                          geaccepteerd="nee", afgewezen="nee")

        aluitgenodigdjij = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND uitgenodigd=:uitgenodigd \
                                       AND geaccepteerd=:geaccepteerd AND afgewezen=:afgewezen",
                                       van=gebruikersnaam, naar=toetevoegenvriend, uitgenodigd="ja",
                                       geaccepteerd="nee", afgewezen="nee")

        if aluitgenodigdvriend or aluitgenodigdjij:
            return apology("Deze gebruiker heeft je al uitgenodigd of andersom")

        else:
            now = datetime.datetime.now()
            date = now.strftime("%d-%m-%Y")
            db.execute("INSERT INTO verzoeken (van, naar, geaccepteerd, uitgenodigd, afgewezen, datum) VALUES \
                        (:van, :naar, :geaccepteerd, :uitgenodigd, :afgewezen, :datum)",
                        van=gebruikersnaam, naar=toetevoegenvriend, geaccepteerd="nee",
                        uitgenodigd="ja", afgewezen="nee", datum=date)

            return render_template("/message/toegevoegd.html", toetevoegenvriend = toetevoegenvriend, lengte = lengte_vv(),
                                    tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

    return render_template("vriendtoevoegen.html", lengte = lengte_vv(), tipslengte = tipslength(),
                            totaal = (lengte_vv()+ tipslength()))

@app.route("/toegevoegd", methods=["GET", "POST"])
@login_required
def toegevoegd():
    return render_template("/message/toegevoegd.html", lengte = lengte_vv(), tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

@app.route("/vriendenlijst")
@login_required
def vriendenlijst():
    return render_template("vriendenlijst.html", vrienden=vrienden1(), vrienden1=vrienden2(), lengte = lengte_vv(),
                            tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

@app.route("/verzoeken", methods=["GET", "POST"])
@login_required
def verzoeken():
    if request.method == "POST":
        gebruikersnaam = gebruiker()
        accepteren = request.form.get("accepteren")
        weigerenn = request.form.get("weigeren")

        if not accepteren:
            weigeren = weigerenn[1:]
            now = datetime.datetime.now()
            date = now.strftime("%d-%m-%Y")

            db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar", naar = gebruikersnaam, van=weigeren)
            db.execute("INSERT INTO verzoeken (van, naar, geaccepteerd, uitgenodigd, afgewezen, datum) VALUES (:van, :naar, :geaccepteerd, :uitgenodigd, :afgewezen, :datum)",
                        van=weigeren, naar = gebruikersnaam, geaccepteerd="nee", uitgenodigd="ja", afgewezen="ja", datum=date)

            return render_template("/message/geweigerd.html", verzoeken=verzoek(), lengte = lengte_vv(), tipslengte = tipslength(),
                                    totaal = (lengte_vv()+ tipslength()), weigeren=weigeren)

        elif accepteren:
            now = datetime.datetime.now()
            date = now.strftime("%d-%m-%Y")
            db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar", naar = gebruikersnaam, van=accepteren)
            db.execute("INSERT INTO verzoeken (van, naar, geaccepteerd, datum) VALUES (:van, :naar, :geaccepteerd, :datum)",
                        van=accepteren, naar = gebruikersnaam, geaccepteerd="ja", datum=date)

            return render_template("/message/geaccepteerd.html", verzoeken=verzoek(), lengte = lengte_vv(), tipslengte = tipslength(),
                                    totaal = (lengte_vv()+ tipslength()), accepteren=accepteren)

    return render_template("verzoeken.html", verzoeken=verzoek(), lengte = lengte_vv(), tipslengte = tipslength(),
                            totaal = (lengte_vv()+ tipslength()))

@app.route("/zoeken", methods=["GET", "POST"])
@login_required
def zoekresultaat():
    if request.method == "POST":
        searchterm = request.form.get("zoekterm")

        if not searchterm:
            return apology("Geen zoekterm")
        elif results_per_page(searchterm, pagenr=1) == False:
            return apology("Geen resultaten")
        else:
            return render_template("zoekresultaten.html", zoekresultaten=total_results(searchterm), lengte = lengte_vv(),
                                    tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

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
        tmdb_response = rfi_TMDb(tmdb_id)
        addtohistory(tmdb_id, tmdb_response)
        omdb_response = rfi_OMDb(tmdb_response)

        favorieten = favorietenn()
        alfavo = any([favoriet['film_id'] == tmdb_id for favoriet in favorieten])

        checkins = checkinss()
        alcheckin = any([checkin['film_id'] == tmdb_id for checkin in checkins])

        return render_template("filminformatie.html", tmdb = tmdb_response, omdb=omdb_response, alfavo=alfavo,
                                lengte = lengte_vv(), tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()),
                                vrienden=vrienden1(), vrienden1=vrienden2(), lijsten=lijsten1(), lijsten2=lijsten2(),
                                lijsten3=lijsten3(), alcheckin=alcheckin)

@app.route("/filminfo_non", methods=["GET", "POST"])
def filminformatie_non():
    if request.method == "POST":
        tmdb_id = request.form.get("tmdb_id")
        tmdb_response = rfi_TMDb(tmdb_id)
        omdb_response = rfi_OMDb(tmdb_response)

        return render_template("filminformatie_non.html", tmdb = tmdb_response, omdb=omdb_response)

@app.route("/mijnprofiel")
@login_required
def mijnprofiel():
    "Pas je profiel aan"

    return render_template("mijnprofiel.html", lengte = lengte_vv(), tipslengte = tipslength(), totaal= (lengte_vv()+ tipslength()),
    vrienden=vrienden1(), vrienden1=vrienden2(), favorieten=favorietenn(), historie=geschiedenis(),
    lijsten=lijsten1(), lijsten2=lijsten2(), lijsten3=lijsten3(), aanbevelingen=aanbevelingenn(), checkins=checkinss(),
    aanbevelingenvan=aanbevelingenvann())

@app.route("/wachtwoordvergeten", methods=["GET", "POST"])
def wachtwoordvergeten():
    if request.method == "POST":
        return render_template("wachtwoordveranderen.html")

@app.route("/wachtwoordveranderen", methods=["GET", "POST"])
def wachtwoordveranderen():
    """Verander wachtwoord"""

    if request.method == 'POST':

        # pak id uit database
        account = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                              gebruikersnaam=request.form.get('gebruikersnaam'))

        passwordformnon()

        # bevestig of het antwoord op de beveiligheidsvraag klopt
        if len(account) != 1 or request.form.get('veiligheidsvraag') != account[0]['veiligheidsvraag']:
            return apologynon("Het antwoord op de veiligheidsvraag klopt niet!")

        # check of nieuwe wachtwoord gelijk is aan oude wachtwoord
        wachtwoordcheck = db.execute("SELECT wachtwoord FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                                      gebruikersnaam=account[0]["gebruikersnaam"])

        if pwd_context.verify(request.form.get("nieuw_wachtwoord"), wachtwoordcheck[0]["wachtwoord"]):
            return apologynon("Niet mogelijk om je huidige wachtwoord te kiezen")

        # maak een hash van het wachtwoord
        new_hash = pwd_context.hash(request.form.get("nieuw_wachtwoord"))

        # update de gebruiker
        resultaat = db.execute("UPDATE gebruikers SET wachtwoord=:wachtwoord WHERE gebruikersnaam=:gebruikersnaam",
                                gebruikersnaam=request.form.get('gebruikersnaam'), wachtwoord=new_hash)

        return render_template("/message/wachtwoordveranderd.html")

@app.route("/wachtwoordgebruikers", methods=["GET", "POST"])
@login_required
def wachtwoordgebruikers():
    """Verander wachtwoord"""

    if request.method == 'POST':

        passwordformgeb()

        # pak id uit database
        account = db.execute("SELECT * FROM gebruikers WHERE id = :id", id=session['user_id'])

        # bevestig of het wachtwoord klopt
        if len(account) != 1 or not pwd_context.verify(request.form.get('wachtwoord'), account[0]['wachtwoord']):
            return apology("Het wachtwoord klopt niet!")


        # controleer of beide wachtwoorden overeenkomen
        if request.form.get("nieuw_wachtwoord") != request.form.get("wachtwoord_herhaling"):
            return apology("De wachtwoorden komen niet overeen")

        wachtwoordcheck = db.execute("SELECT wachtwoord FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                                      gebruikersnaam=account[0]["gebruikersnaam"])

        if pwd_context.verify(request.form.get("nieuw_wachtwoord"), wachtwoordcheck[0]["wachtwoord"]):
            return apology("Niet mogelijk om je huidige wachtwoord te kiezen")

        # maak een hash van het wachtwoord
        new_hash = pwd_context.hash(request.form.get("nieuw_wachtwoord"))

        # update de gebruiker
        resultaat = db.execute("UPDATE gebruikers SET wachtwoord=:wachtwoord WHERE id=:id",
                                id=session["user_id"], wachtwoord=new_hash)

        return render_template("/message/wachtwoordveranderdgeb.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                totaal= (lengte_vv()+ tipslength()))

    else:
        return render_template("wachtwoordgebruikers.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                totaal= (lengte_vv()+ tipslength()))

@app.route("/accountverwijderen", methods=["GET", "POST"])
@login_required
def accountverwijderen():

    if request.method == "POST":

        gebruikersnaam = gebruiker()
        wachtwoord = request.form.get("wachtwoord")
        accountverwijderenform()


        wachtwoordcheck = db.execute("SELECT wachtwoord FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                                      gebruikersnaam=gebruikersnaam)

        if len(wachtwoordcheck) != 1 or not pwd_context.verify(request.form.get("wachtwoord"), wachtwoordcheck[0]["wachtwoord"]):
            return apology("Het opgegeven wachtwoord klopt niet")

        else:
            #logt gene uit
            session.clear()

            db.execute("DELETE FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam", gebruikersnaam=gebruikersnaam)
            db.execute("DELETE FROM verzoeken WHERE naar=:naar OR van=:van", naar = gebruikersnaam, van=gebruikersnaam)

            return render_template("/message/verwijderd.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                    totaal= (lengte_vv()+ tipslength()))

    return render_template("accountverwijderen.html", lengte = lengte_vv(), tipslengte = tipslength(),
                            totaal= (lengte_vv()+ tipslength()))

@app.route("/favorieten", methods=["GET", "POST"])
@login_required
def favorieten():
    return render_template("favorieten.html", favorieten=favorietenn(), lengte = lengte_vv(), tipslengte = tipslength(),
                            totaal= (lengte_vv()+ tipslength()))

@app.route("/addfavorite", methods=["POST"])
@login_required
def addfavorite():
    if request.method == "POST":

        gebruikersnaam = gebruiker()
        tmdb_id = request.form.get("favorieten")
        tmdb_response = rfi_TMDb(tmdb_id)
        omdb_response = rfi_OMDb(tmdb_response)

        db.execute("INSERT INTO favorieten (gebruiker, film_id, titel, afbeelding) VALUES (:gebruiker, :film_id, :titel, :afbeelding)",
                    gebruiker = gebruikersnaam, film_id = tmdb_id, titel = tmdb_response["original_title"], afbeelding = tmdb_response["poster_path"])

        return render_template("/message/addfavorite.html", tmdb = tmdb_response, omdb=omdb_response, favorieten=favorietenn(),
                                lengte = lengte_vv(), tipslengte = tipslength(), totaal= (lengte_vv()+ tipslength()))

@app.route("/removefavorite", methods=["POST"])
@login_required
def removefavorite():
    if request.method == "POST":

        gebruikersnaam = gebruiker()
        tmdb_id = request.form.get("geenfavo")
        tmdb_response = rfi_TMDb(tmdb_id)
        omdb_response = rfi_OMDb(tmdb_response)

        db.execute("DELETE FROM favorieten WHERE gebruiker=:gebruiker AND film_id=:film_id",
                    gebruiker = gebruikersnaam, film_id = tmdb_id)

        return render_template("/message/removefavorite.html", tmdb = tmdb_response, omdb=omdb_response, lengte = lengte_vv(),
                                tipslengte = tipslength(), totaal= (lengte_vv()+ tipslength()))

@app.route("/historie", methods=["GET", "POST"])
@login_required
def historie():
    if request.method == "POST":

        if len(geschiedenis()) > 0:
            db.execute("DELETE FROM historie WHERE gebruiker=:gebruiker", gebruiker = gebruiker())

            return render_template("/message/legehistorie.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                    totaal= (lengte_vv()+ tipslength()))

        else:
            return apology("Je hebt geen kijkgeschiedenis")

    return render_template("historie.html", historie=geschiedenis(), lengte = lengte_vv(), tipslengte = tipslength(),
                            totaal= (lengte_vv()+ tipslength()))

@app.route("/legehistorie", methods=["GET", "POST"])
@login_required
def legehistorie():
    return render_template("/message/legehistorie.html", lengte = lengte_vv(), tipslengte =tipslength(), totaal=(lengte_vv()+ tipslength()))

@app.route("/mijnlijsten", methods=["GET", "POST"])
@login_required
def mijnlijsten():
    return render_template("mijnlijsten.html", lengte = lengte_vv(), tipslengte =tipslength(), totaal=(lengte_vv()+ tipslength()),
                            vrienden=vrienden1(), vrienden1=vrienden2(), lijsten=lijsten1(), lijsten2=lijsten2(), lijsten3=lijsten3())

@app.route("/checkins", methods=["GET", "POST"])
@login_required
def checkins():
    return render_template("checkins.html", lengte = lengte_vv(), tipslengte =tipslength(), totaal=(lengte_vv()+ tipslength()),
                            checkins=checkinss())

@app.route("/tipvriend", methods=["POST"])
@login_required
def tipvriend():
    if request.method == "POST":

        tmdb_id = ophalen("buttonvriend")

        check = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            van=gebruiker(), naar=ophalen("tipvriend"), geaccepteerd="ja")

        check2 = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            naar = gebruiker(), van=ophalen("tipvriend"), geaccepteerd="ja")

        if check or check2:
            tipcheck = db.execute("SELECT * FROM aanbevelingen WHERE van=:van AND naar=:naar AND film_id=:film_id",
                                   van=gebruiker(), naar=ophalen("tipvriend"), film_id = ophalen("buttonvriend"))

            if tipcheck:
                return apology("Je hebt deze gebruiker deze film al aanbevolen")

            tips = db.execute("INSERT INTO aanbevelingen (van, naar, film_id, titel, afbeelding) VALUES \
                             (:van, :naar, :film_id, :titel, :afbeelding)", van=gebruiker(), naar=ophalen("tipvriend"),
                             film_id = ophalen("buttonvriend"), titel = rfi_TMDb(tmdb_id)["original_title"],
                             afbeelding = rfi_TMDb(tmdb_id)["poster_path"])

            return render_template("index.html", popular=(popular_films())["results"], new=(new_films())["results"],
                                    tmdb = rfi_TMDb(tmdb_id), omdb=rfi_OMDb(rfi_TMDb(tmdb_id)), favorieten=favorieten,
                                    lengte = lengte_vv(), tipslengte =tipslength(), totaal=(lengte_vv()+ tipslength()),
                                    aanbevelingen=aanbevelingenn())

        else:
            return apology("Deze gebruiker is geen vriend van je")

@app.route("/tips", methods=["GET", "POST"])
@login_required
def tips():
    return render_template("tips.html", lengte = lengte_vv(), tipslengte =tipslength(), totaal=(lengte_vv()+ tipslength()),
                            aanbevelingen=aanbevelingenn(), vrienden=vrienden1(), vrienden1=vrienden2())

@app.route("/vriendinfo", methods=["POST"])
@login_required
def vriendinfo():
    if request.method == "POST":
        profiel = profielvriend()
        return render_template("vriendinfo.html", favorieten=favorietenvriend(), lengte = lengte_vv(), tipslengte =tipslength(),
                                totaal=(lengte_vv()+ tipslength()), profiel=profiel, checkins=checkinsvriend(),
                                historie=geschiedenisvriend(), vrienden=vriendenvriend1(), vrienden1=vriendenvriend2(),
                                aanbevelingen=aanbevelingenvriend(), aanbevelingenvan=aanbevelingenvanvriend())

@app.route("/verwijdervriendredirect", methods=["POST"])
@login_required
def verwijdervriendredirect():
    if request.method == "POST":

        vriend = request.form.get("verwijder")
        if not vriend:
            vriend = request.form.get("verwijder1")

    return render_template("/message/verwijdervriendredirect.html", vriend=vriend, lengte = lengte_vv(), tipslengte =tipslength(),
                            totaal=(lengte_vv()+ tipslength()))

@app.route("/verwijdervriend", methods=["POST"])
@login_required
def verwijdervriend():
    if request.method == "POST":

        if request.form.get("verwijder"):
            vriendcheck = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                     naar = gebruiker(), van=request.form.get("verwijder"), geaccepteerd="ja")

            vriendcheckk = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                      van=gebruiker(), naar=request.form.get("verwijder"), geaccepteerd="ja")

            if vriendcheck:
                db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            naar = gebruiker(), van=request.form.get("verwijder"), geaccepteerd="ja")

            elif vriendcheckk:
                db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            van=gebruiker(), naar=request.form.get("verwijder"), geaccepteerd="ja")

        elif request.form.get("verwijder1"):
            vriendcheck = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                      naar = gebruiker(), van=request.form.get("verwijder1"), geaccepteerd="ja")

            vriendcheckk = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                      van=gebruiker(), naar=request.form.get("verwijder1"), geaccepteerd="ja")

            if vriendcheck:
                db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            naar = gebruiker(), van=request.form.get("verwijder1"), geaccepteerd="ja")

            elif vriendcheckk:
                db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            van=gebruiker(), naar=request.form.get("verwijder1"), geaccepteerd="ja")

        return render_template("/message/verwijderdvriend.html", lengte = lengte_vv(), tipslengte =tipslength(),
                                totaal=(lengte_vv() + tipslength()))

@app.route("/lijstgemaakt", methods=["POST"])
@login_required
def lijstgemaakt():
    if request.method == "POST":

        check = db.execute("SELECT * FROM lijsten WHERE lijstnaam=:lijstnaam AND gebruiker=:gebruiker AND gebruiker2 IS NULL",
                            lijstnaam = request.form.get("lijstnaam"), gebruiker = gebruiker())

        if check:
            tekst = "Je hebt al een lijst die " + request.form.get("lijstnaam") + " heet"
            return apology(tekst)

        else:
            db.execute("INSERT INTO lijsten (gebruiker, lijstnaam, nieuwe_lijst) VALUES (:gebruiker, :lijstnaam, :nieuwe_lijst)",
                    gebruiker = gebruiker(), lijstnaam = request.form.get("lijstnaam"), nieuwe_lijst="ja")

        return render_template("/message/lijstgemaakt.html", lengte = lengte_vv(), tipslengte =tipslength(),
                                lijstnaam = request.form.get("lijstnaam"), totaal=(lengte_vv() + tipslength()))

@app.route("/gezamenlijkelijstgemaakt", methods=["POST"])
@login_required
def gezamenlijkelijstgemaakt():
    if request.method == "POST":

        user = gebruiker()
        lijstnaam = request.form.get("gez_lijstnaam")
        friend_request_FROM = request.form.get("vriendvan")
        friend_request_TO = request.form.get("vriendnaar")

        # Als vriend de gebruiker heeft toegevoegd.
        if friend_request_FROM:
            sql_gezamenlijke_lijst_gemaakt(user, friend_request_FROM, lijstnaam)
        # Als gebruiker de vriend heeft toegevoegd.
        if friend_request_TO:
            sql_gezamenlijke_lijst_gemaakt(user, friend_request_TO, lijstnaam)

        return render_template("/message/gezamenlijkelijstgemaakt.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                lijstnaam = lijstnaam, totaal = tipslength() + lengte_vv())

@app.route("/lijst", methods=["POST"])
@login_required
def lijst():
    if request.method == "POST":
        lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND nieuwe_lijst IS NULL",
                                gebruiker = gebruiker(), lijstnaam = request.form.get("button"))

        return render_template("lijst.html", lengte = lengte_vv(), tipslengte = tipslength(), lijst=request.form.get("button"),
                                lijstinfo=lijstinfo, totaal = tipslength() + lengte_vv())

@app.route("/gezlijst", methods=["POST"])
@login_required
def gezlijst():
    if request.method == "POST":
        vriend = request.form.get("vriend")

        lijsten1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 \
                               AND lijstnaam=:lijstnaam AND nieuwe_lijst IS NULL",
                               gebruiker = gebruiker(), gebruiker2 = vriend, lijstnaam = request.form.get("button"))

        lijsten2 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam AND nieuwe_lijst IS NULL",
                                gebruiker2 = gebruiker(), gebruiker = vriend, lijstnaam = request.form.get("button"))

        return render_template("gezlijst.html", lengte = lengte_vv(), tipslengte = tipslength(), totaal = tipslength() +lengte_vv(),
                                lijstnaam = request.form.get("button"),  vriend = vriend, lijsten1=lijsten1, lijsten2=lijsten2)

@app.route("/addcheckins", methods=["POST"])
@login_required
def addcheckins():

    if request.method == "POST":

        tmdb_id = request.form.get("favorieten")
        tmdb_response = rfi_TMDb(tmdb_id)
        omdb_response = rfi_OMDb(tmdb_response)

        db.execute("INSERT INTO checkins (gebruiker, film_id, titel, afbeelding) VALUES \
                  (:gebruiker, :film_id, :titel, :afbeelding)",
                  gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                  afbeelding = tmdb_response["poster_path"])

        return render_template("/message/addcheckins.html", tmdb = tmdb_response, omdb=omdb_response, checkins=checkinss(),
                                lengte = lengte_vv(), tipslengte = tipslength(), totaal = tipslength() +lengte_vv())

@app.route("/removecheckins", methods=["POST"])
@login_required
def removecheckins():

    if request.method == "POST":

        tmdb_response = rfi_TMDb(request.form.get("geencheckin"))
        omdb_response = rfi_OMDb(tmdb_response)

        db.execute("DELETE FROM checkins WHERE gebruiker=:gebruiker AND film_id=:film_id",
                    gebruiker = gebruiker(), film_id = request.form.get("geencheckin"))

        return render_template("/message/removecheckins.html", tmdb = tmdb_response, omdb = rfi_OMDb(tmdb_response), lengte = lengte_vv(),
                                tipslengte = tipslength(), totaal = tipslength() +lengte_vv())

@app.route("/addtolist", methods=["POST"])
@login_required
def addtolist():

    if request.method == "POST":

        tmdb_id = request.form.get("buttonfilm")
        lijst = request.form.get("lijst")

        tmdb_response = rfi_TMDb(tmdb_id)
        omdb_response = rfi_OMDb(tmdb_response)

        lijstnaam = lijst.split('|')[0]

        if len(lijst) == len(lijstnaam):
            lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND film_id=:film_id AND titel=:titel AND \
                                    afbeelding=:afbeelding AND lijstnaam=:lijstnaam AND gez_lijst IS NULL AND nieuwe_lijst IS NULL",
                                    gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                                    afbeelding = tmdb_response["poster_path"], lijstnaam = lijstnaam)

            if lijstinfo:
                tekst = "Deze film staat al in je lijst: " + lijstnaam
                return apology(tekst)

            db.execute("INSERT INTO lijsten (gebruiker, film_id, titel, afbeelding, lijstnaam) VALUES \
                        (:gebruiker, :film_id, :titel, :afbeelding, :lijstnaam)",
                        gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                        afbeelding = tmdb_response["poster_path"], lijstnaam = lijstnaam)

            return render_template("/message/addtolist.html", tmdb = tmdb_response, omdb=omdb_response, lengte = lengte_vv(),
                                    tipslengte = tipslength(), totaal = tipslength() +lengte_vv(), lijstnaam = lijstnaam)

        else:
            vriend = lijst.split('|')[1]
            lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND film_id=:film_id AND titel=:titel AND \
                                    afbeelding=:afbeelding AND lijstnaam=:lijstnaam AND gez_lijst IS NULL AND \
                                    nieuwe_lijst IS NULL AND gebruiker2=:gebruiker2",
                                    gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                                    afbeelding = tmdb_response["poster_path"], lijstnaam = lijstnaam, gebruiker2=vriend)

            if lijstinfo:

                tekst = "Deze film staat al in je gezamenlijke lijst: " + lijstnaam + "met:" + vriend
                return apology(tekst)

            if not lijstinfo:

                lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND film_id=:film_id AND titel=:titel AND \
                                        afbeelding=:afbeelding AND lijstnaam=:lijstnaam AND gez_lijst IS NULL AND \
                                        nieuwe_lijst IS NULL AND gebruiker2=:gebruiker2",
                                        gebruiker=vriend, film_id = tmdb_id, titel = tmdb_response["original_title"],
                                        afbeelding=tmdb_response["poster_path"], lijstnaam=lijstnaam, gebruiker2 = gebruiker())

                if lijstinfo:
                    tekst = "Deze film staat al in je gezamenlijke lijst: " + lijstnaam + "met:" + vriend
                    return apology(tekst)

                else:
                    db.execute("INSERT INTO lijsten (gebruiker, film_id, gebruiker2, titel, afbeelding, lijstnaam) VALUES (:gebruiker, :film_id, :gebruiker2, :titel, :afbeelding, :lijstnaam)",
                    gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                    afbeelding = tmdb_response["poster_path"], lijstnaam = lijstnaam, gebruiker2=vriend)

                    return render_template("/message/addtolist.html", tmdb = tmdb_response, omdb=omdb_response, lengte = lengte_vv(),
                    tipslengte = tipslength(), totaal = tipslength() +lengte_vv(), lijstnaam = lijstnaam, vriend=vriend)

@app.route("/removelist", methods=["POST"])
@login_required
def removelist():

    if request.method == "POST":

        vriend = request.form.get("vriend")

        if not vriend:
            db.execute("DELETE FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND gez_lijst IS NULL",
                        gebruiker = gebruiker(), lijstnaam = request.form.get("lijstnaam"))

            return render_template("/message/removelist.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                    totaal = tipslength()+lengte_vv(), lijstnaam = request.form.get("lijstnaam"))

        else:
            check1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND gebruiker2=:gebruiker2",
                                gebruiker = gebruiker(), lijstnaam = request.form.get("lijstnaam"), gebruiker2=vriend)

            if check1:
                db.execute("DELETE FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
                            gebruiker = gebruiker(), gebruiker2=vriend, lijstnaam = request.form.get("lijstnaam"))

                return render_template("/message/removelist.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                        totaal = tipslength()+lengte_vv(), lijstnaam=request.form.get("lijstnaam"), vriend=vriend)

            if not check1:
                check1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND gebruiker2=:gebruiker2",
                                    gebruiker2 = gebruiker(), lijstnaam=request.form.get("lijstnaam"), gebruiker=vriend)

                db.execute("DELETE FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
                            gebruiker2=gebruiker(), gebruiker=vriend, lijstnaam = request.form.get("lijstnaam"))

                return render_template("/message/removelist.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                        totaal = tipslength()+lengte_vv(), lijstnaam = request.form.get("lijstnaam"), vriend=vriend)