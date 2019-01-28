# NL Films
#### Isa-Ali Kirca &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 12014672
#### Gerard Noordhuis &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 11919582
#### Patrick Smit &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 11433604

### [Schetsen](https://docs.google.com/presentation/d/1Dk9pYlrxR6hi45ncdenz7bOs3y8t3Wdz3CnpoxP1xaI/edit?usp=sharing)
Bekijk de concepten/schetsen op Google Slides^.

## Samenvatting:

  * Met NederlandseFilms.nl willen wij een site maken die gebruikers de optie geeft om hun favoriete Nederlandse films op te zoeken. Verder kunnen gebruikers kijklijsten creëren en vrienden maken met andere gebruikers, om vervolgens lijsten met elkaar te delen. Gebruikers kunnen ook likes geven aan films en comments achterlaten.

## Features

### Voor bezoekers zonder account:
  * 1.1 Vanaf iedere pagina:
    * 🔍 Zoeken naar films
      * Zoekresultaten pagina
    * Registreren
    * Inloggen
      * Wachtwoord vergeten
        * Opnieuw instellen a.d.h.v. veiligheidsvraag
  * 1.2 🏠 Homepagina:
    * Lijst met de 12 populairste films
  * 1.3 🍿 Filminformatie:
      * Omschrijving
      * Geef de rating van de film weer
        * wordt opgehaald van IMDb en anders van TMDb
      * Jaar van de release
      * Bekijk de regisseur(s), schrijver(s) en hoofdrolspelers

### Voor ingelogde gebruikers:
  * 2.1 Vanaf iedere pagina:
    * 🔍 Zoeken naar films
      * Zoekresultaten pagina
    * ❤️ Filmlijsten bekijken:
      * Favoriete films
      * Bekeken films
      * Kijklijst
      * Check-ins
    * 👥 Interactie met vrienden:
      * Vriendschapsverzoeken sturen a.d.h.v. gebruikersnaam
      * Vriendschapsverzoeken accepteren of weigeren
      * Film tippen aan een vriend
      * Vriendenlijst bekijken
    * 👤 Account:
      * Profiel bekijken
      * Wachtwoord wijzigen
      * Account verwijderen
      * Uitloggen
  * 2.2 🏠 Homepage:
    * Lijst met de 12 populairste films  
  * 2.3 🍿 Filminformatie:
    * Voeg film toe aan Favorieten
    * Verwijder film van Favorieten
    * Voeg film toe aan Kijklijst
    * Omschrijving
    * Geef de rating van de film weer
      * wordt opgehaald van IMDb en anders van TMDb    
    * Jaar van de release
    * Bekijk de regisseur(s), schrijver(s) en hoofdrolspelers

* Eventueel in de toekomst:
  * Delen via Social Media.
  * Lijst met top gebruikers bekijken
  * Vrienden berichten sturen
  * Films toevoegen aan een gezamenlijke lijst (update 2 lijsten)
  * Per categorie: de beste films.

---
Van tevoren bepaald:
# Wat we niet doen:
  * Eigen ratings, beoordelingen et cetera, omdat IMDb en TMDb hierin niet te overtreffen zijn in het aantal relevante beoordelingen.


### Minimum viable product:
  * Er moet gezocht kunnen worden naar een specifieke film. Wanneer de film gevonden wordt, omvat de getoonde pagina in ieder geval:
    * titel van de film
    * jaar van uitkomst
    * regisseur(s)
    * acteurs
    * poster/afbeelding
    * beoordeling

--- 

### Afhankelijkheden
#### Gebruikte diensten

| Service        | Wat           | 
| ------------- |:-------------:| 
| [The Movie Database](https://www.themoviedb.org/documentation/api) (TMDb)     | film database  API  |
| [The Open Movie Database](http://www.omdbapi.com) (OMDb)      | film database API      |
| [Bootstrap](https://getbootstrap.com/docs/4.2/getting-started/introduction/) | a HTML, CSS, and JS library      | 
| [Bootsnipp](https://bootsnipp.com/) | code snippets for Bootstrap HTML/CSS/JS framework      | 


#### Concurerende sites:
|         | NL Films           | Filmvandaag           | TMDb           | IMDb           |  
| ------------- |:-------------:|:-------------:| 
| Internationale films | ☒ | ☑ | ☑ | ☒  

https://www.imdb.com:
 * Niet gelimiteerd tot Nederlandse films, maar heeft ze wel.
 * Commercieel en gebonden aan een groot, beursgenoteerd bedrijf (Amazon).
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
