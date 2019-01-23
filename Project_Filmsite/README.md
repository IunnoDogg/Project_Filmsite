# nederlandsefilm
## Isa-Ali Kirca &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 12014672
## Gerard Noordhuis &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 11919582
## Patrick Smit &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 11433604

### [Schetsen](https://docs.google.com/presentation/d/1Dk9pYlrxR6hi45ncdenz7bOs3y8t3Wdz3CnpoxP1xaI/edit?usp=sharing)
Bekijk de concepten/schetsen op Google Slides^.

### Samenvatting:

  * Met NederlandseFilms.nl willen wij een site maken die gebruikers de optie geeft om hun favoriete Nederlandse films op te zoeken. Verder kunnen gebruikers kijklijsten creëren en vrienden maken met andere gebruikers, om vervolgens lijsten met elkaar te delen. Gebruikers kunnen ook likes geven aan films en comments achterlaten. 

### Features

Voor ingelogde gebruikers
  * 1.1 Gebruikersinteractie/ Vrienden op het platform
    * Anderen toevoegen a.d.h.v. gebruikersnaam (accepteren, weigeren)
    * Vrienden berichten sturen
    * Filmtitel delen met een vriend (in de eerder genoemde chat?)
    * Films toevoegen aan een gezamenlijke lijst (update 2 lijsten)  
    * Lijst met top gebruikers bekijken 
    * Mensen volgen
    * Kijken welke films je met vrienden ‘in common’ hebt


* 1.2 Eigen account
  * 1.2.1 Account informatie
   * Vul account details in (wachtwoord, e-mail, gebruikersnaam, geslacht)
   * Valideer account
   * Koppel Social Media accounts met NLfilms account
   * Profiel bewerken (wachtwoord, e-mail, gebruikersnaam? geslacht? verander koppeling met social media)
  * 1.2.2 Films opslaan etc.
   * Films toevoegen aan een lijst met favorieten
   * Film toevoegen aan een kijklijst
   * Film toevoegen aan ‘check-in’ of historie
   * Een rating toevoegen aan TMDb

* 1.3 Pagina van film:
  * voeg film toe aan kijklijst
  * Samenvatting / Omschrijving
  * Weergeef de rating vanuit de API
  * Bekijk comments van gebruikers
  * (wanneer ingelogd:)
    * Schrijf een comment (over de film)
    * Geef een rating (wordt dorgestuurd naar TMDb)


* 1.4 Homepage:
  * 1.4.1 Homepagina: Layout
    * Item
    * Omschrijving
    * Zoekbalk
  * 1.4.2 Homepagina: Zoeken:
    * film → pagina met informatie (zie Minimum viable product)
    * acteur → pagina met de best beoordeelde films van de desbetreffende acteur
    * jaar → pagina met de best beoordeelde films van dat jaar

* 1.5 Account:
  * maak een account aan
  * (wanneer ingelogd:)
    * Likes
    * Friend request (om naar elkaars accounts te kijken)
    
* Mogelijke extra’s
  * Delen via Whatsapp, Facebook, enz.

Wat we niet doen: 
  * Eigen ratings, beoordelingen et cetera, omdat IMDb en TMDb hierin niet te overtreffen zijn in het aantal relevante beoordelingen.
  
  
### Minimum viable product:
  * Er moet gezocht kunnen worden naar een specifieke film. Wanneer de film gevonden wordt, omvat de getoonde pagina in ieder geval:
    * titel van de film
    * jaar van uitkomst in theaters
    * speelduur
    * regisseur(s)
    * genre
    * acteurs
    * Eventueel wordt er ook een poster/afbeelding/omzet en een beoordeling bijgevoegd.

  * Het zou mooi zijn als het ook mogelijk is om per categorie de beste films te tonen. Het kan zijn dat  dit niet real-time mogelijk is, omdat veel film-API’s de beperking hebben dat er een maximum aantal data-aanvragen per tijdseenheid wordt gehanteerd. 

### Afhankelijkheden
#### Eventueel te gebruiken API’s:

The Movie Database(TMDb):
https://www.themoviedb.org/documentation/api 

Filmtotaal:
http://api.filmtotaal.nl/ 

IMDb Scraper (Third party):
http://imdbpy.sourceforge.net/

TMDb Wrapper (Third party):
https://pypi.org/project/tmdbsimple/ 
https://github.com/celiao/tmdbsimple

#### Verdere sites en plug-ins:

Bootstrap: 
https://getbootstrap.com/docs/4.2/getting-started/introduction/

Bootsnipp: 
https://bootsnipp.com/

#### Concurerende sites:

https://www.imdb.com:
 * Niet gelimiteerd tot Nederlandse films, maar heeft ze wel.
 * Bindingen met bedrijven als Amazon
 * Heeft pagina's met nieuws over de filmindustrie.
 * Behandelt ook Video Games
 
https://www.tmdb.com:
 * Heeft links naar de films die momenteel in de bioscoop draaaien.
 * Internetfora over films

 https://www.filmvandaag.nl:
  * Heeft links naar de films die momenteel in de bioscoop draaaien.
  * Heeft links naar de series/films die te zien zijn op Netfilx
  * Geeft releases op dvd/bluray aan.
  
 
#### Moeilijke delen:
Veel code zal het werk complexer maken. De zaken waarvan we momenteel verwachten dat ze lastig zullen worden:
* Andere gebruikers toevoegen a.d.h.v. gebruikersnaam
* Vrienden berichten sturen
* Filmtitels delen met een vriend
* Films toevoegen aan een gezamenlijke lijst (update 2 lijsten)  
* Lijst met top gebruikers bekijken 
* Mensen volgen
