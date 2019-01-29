import urllib.request, requests, json, urllib, datetime
from flask import redirect, render_template, request, session
from functools import wraps
from urllib.request import urlopen

year = str(datetime.date.today().year)

# Om urls te vereenvoudigen
tmdb_info = "https://api.themoviedb.org/3/movie/"
tmdb_search = "https://api.themoviedb.org/3/search/movie?"
tmdb_key = "api_key=9c226374f10b2dcd656cf7c348ee760a"
tmdb_no_adult = "&include_adult=false"
tmdb_nl = "&language=nl"

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

def results_per_page(searchterm, pagenr):
    '''
    Return all results for an individual searchresults page.
    '''
    url = tmdb_search + tmdb_key + tmdb_nl + "&query=" + searchterm + tmdb_no_adult + "&page=" + str(pagenr)
    print(url)
    response = json.loads(str((requests.get(url).content).decode('UTF-8')))
    return response

def total_results(searchterm):
    '''
    Collect results for the first 30 (or less) searchresults pages.
    '''
    total_pages = results_per_page(searchterm, pagenr=1)["total_pages"]
    searchresults = []
    pagenr = 1

    # Blijf resultaten toevoegen tot paginalimiet (of pagina 30) is bereikt.
    while pagenr < 30 and pagenr <= total_pages:
        searchresults += results_per_page(searchterm, pagenr)["results"]
        pagenr += 1
    return([i for i in searchresults if i["original_language"] == "nl"])

def film_informatie(tmdb_id):
    '''
    Request film information for a specific TMDb film ID.
    '''
    from urllib.request import urlopen
    tmdb_url = str(tmdb_search + tmdb_id + tmdb_key + tmdb_nl)
    return(json.loads(str((requests.get(tmdb_url).content).decode('UTF-8'))))

def popular_films():
    return(json.loads(str((requests.get("https://goo.gl/1wCPmP").content).decode('UTF-8'))))

def new_films():
    return(json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key=9c226374f10b2dcd656cf7c348ee760a&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_original_language=nl&year=" + year).content).decode('UTF-8'))))
