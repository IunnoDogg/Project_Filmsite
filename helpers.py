import urllib.request, requests, json, urllib, datetime
from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
from urllib.request import urlopen
from API import *

db = SQL("sqlite:///nlfilms.db")

def addtohistory(tmdb_id, tmdb_response):
    gebruikersnaam = gebruiker()
    historie = db.execute("SELECT film_id FROM historie WHERE gebruiker=:gebruiker", gebruiker = gebruikersnaam)

    if len(historie) == 0 or (tmdb_id in [i["film_id"] for i in historie] and len(historie) != 0):
        db.execute("INSERT INTO historie (gebruiker, film_id, titel, afbeelding) VALUES (:gebruiker, :film_id, :titel, :afbeelding)",
                    gebruiker = gebruikersnaam, film_id = tmdb_id, titel = tmdb_response["original_title"],
                    afbeelding = tmdb_response["poster_path"])

def apology(message, code=400):
    """Renders message as an apology to user."""

    return render_template("apology.html",
        top = code,
        bottom = message,
        lengte = lengte_vv(),
        tipslengte = tipslength(),
        totaal = (tipslength() + lengte_vv()))

def apologynon(message, code=400):
    """Renders message as an apology to user."""

    return render_template("apologynon.html", top=code, bottom=message)

def lengte_vv():
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()

    if verzoeken:
        lengte = len(verzoeken)
        return lengte

    else:
        lengte = 0
        return lengte

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def ophalen(name):
    opgehaald = request.form.get(name)
    return opgehaald

def registerform():
    if not request.form.get("gebruikersnaam"):
        return apologynon("Geef een gebruikersnaam op.")

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

def passwordformnon():
    if not request.form.get('gebruikersnaam'):
            return apologynon("Vul je gebruikersnaam in")

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

def passwordformgeb():
    if not request.form.get('wachtwoord'):
        return apology("Vul je huidige wachtwoord in")

    # check of een nieuw wachtwoord is ingevuld
    if not request.form.get("nieuw_wachtwoord"):
        return apology("Vul een nieuw wachtwoord in")

    # check of het nieuwe wachtwoord is herhaald
    if not request.form.get("wachtwoord_herhaling"):
        return apology("Herhaal je nieuwe wachtwoord")

def accountverwijderenform():
    wachtwoord = request.form.get("wachtwoord")
    wachtwoord_herhaling = request.form.get("wachtwoord_herhaling")

    if not wachtwoord:
        return apology("Geef jouw wachtwoord op.")

    if not wachtwoord_herhaling:
        return apology("Geef herhaling van jouw wachtwoord op.")

    if wachtwoord != wachtwoord_herhaling:
        return apology("De bevestiging komt niet overeen met het wachtwoord.")

####### SQL ######## everything underneath has SQL in it ################
def aanbevelingenn():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM aanbevelingen WHERE naar=:naar", naar = gebruikersnaam)

def aanbevelingenvriend():
    profiel = profielvriend()
    return db.execute("SELECT * FROM aanbevelingen WHERE naar=:naar", naar=profiel)

def aanbevelingenvann():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM aanbevelingen WHERE van=:van", van=gebruikersnaam)

def aanbevelingenvanvriend():
    profiel = profielvriend()
    return db.execute("SELECT * FROM aanbevelingen WHERE van=:van", van=profiel)

def checkinss():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM checkins WHERE gebruiker=:gebruiker", gebruiker = gebruikersnaam)

def checkinsvriend():
    profiel = profielvriend()
    return db.execute("SELECT * FROM checkins WHERE gebruiker=:gebruiker", gebruiker=profiel)

def favorietenn():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM favorieten WHERE gebruiker=:gebruiker", gebruiker = gebruikersnaam)

def favorietenvriend():
    profiel = profielvriend()
    return db.execute("SELECT * FROM favorieten WHERE gebruiker=:gebruiker", gebruiker=profiel)

def gebruiker():
    a = db.execute("SELECT gebruikersnaam FROM gebruikers WHERE id=:id", id=session["user_id"])
    return(a[0]["gebruikersnaam"])

def geschiedenis():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM historie WHERE gebruiker=:gebruiker", gebruiker = gebruikersnaam)

def geschiedenisvriend():
    profiel = profielvriend()
    return db.execute("SELECT * FROM historie WHERE gebruiker=:gebruiker", gebruiker=profiel)

def lijsten1():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gez_lijst IS NULL AND nieuwe_lijst=:nieuwe_lijst",
                        gebruiker = gebruikersnaam, nieuwe_lijst="ja")

def lijsten2():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM lijsten WHERE gez_lijst IS NOT NULL AND gebruiker=:gebruiker AND nieuwe_lijst=:nieuwe_lijst",
                        gebruiker = gebruikersnaam, nieuwe_lijst="ja")

def lijsten3():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM lijsten WHERE gez_lijst IS NOT NULL AND gebruiker2=:gebruiker2 AND nieuwe_lijst=:nieuwe_lijst",
                        gebruiker2 = gebruikersnaam, nieuwe_lijst="ja")

def loginform():
    if not request.form.get("gebruiker-inloggen"):
        return apologynon("Geef een gebruikersnaam op")

    if not request.form.get("wachtwoord-inloggen"):
        return apologynon("Geef een wachtwoord op")

def profielvriend():
    profiel = request.form.get("profiel")

    if profiel == None:
        profiel = request.form.get("profiel1")
        return profiel

    else:
        return profiel

def sql_gezamenlijke_lijst_gemaakt(gebruikersnaam, direction, lijstnaam):
    '''
    Lijst aanmaken of gezamenlijke lijst aanmaken,
    mits er nog geen lijst met de desbetreffende vriend bestaat.
    '''
    check1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
        gebruiker=gebruikersnaam, gebruiker2=direction, lijstnaam=lijstnaam)

    check2 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
        gebruiker2=gebruikersnaam, gebruiker = direction, lijstnaam=lijstnaam)

    if check1 or check2:
        tekst = "Je hebt al een lijst die " + lijstnaam + " heet met deze vriend"
        return apology(tekst)

    else:
        db.execute("INSERT INTO lijsten (gebruiker, lijstnaam, gebruiker2, gez_lijst, nieuwe_lijst) VALUES (:gebruiker, :lijstnaam, :gebruiker2, :gez_lijst, :nieuwe_lijst)",
            gebruiker=gebruikersnaam, lijstnaam=lijstnaam, gebruiker2 = direction, gez_lijst="ja", nieuwe_lijst="ja")

def tipslength():
    gebruikersnaam = gebruiker()

    tips = db.execute("SELECT van FROM aanbevelingen WHERE naar=:naar", naar = gebruikersnaam)

    if tips:
        tipslengte = len(tips)
    else:
        tipslengte = 0
    return tipslengte

def verzoek():
    return(db.execute("SELECT van FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd AND uitgenodigd=:uitgenodigd AND afgewezen=:afgewezen",
                            naar = gebruiker(), geaccepteerd="nee", uitgenodigd="ja", afgewezen="nee"))

def vrienden1():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                        naar = gebruikersnaam, geaccepteerd="ja")

def vriendenvriend1():
    profiel = profielvriend()
    return db.execute("SELECT * FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                        naar=profiel, geaccepteerd="ja")

def vrienden2():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM verzoeken WHERE van=:van AND geaccepteerd=:geaccepteerd",
                        van=gebruikersnaam, geaccepteerd="ja")

def vriendenvriend2():
    profiel = profielvriend()
    return db.execute("SELECT * FROM verzoeken WHERE van=:van AND geaccepteerd=:geaccepteerd",
                       van=profiel, geaccepteerd="ja")