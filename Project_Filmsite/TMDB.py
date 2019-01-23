import requests
key = "api_key=9c226374f10b2dcd656cf7c348ee760a"
zoekterm = "het schnitzelparadijs"
zoekterm = zoekterm.replace(" ", "%20")

url = "https://api.themoviedb.org/3/search/movie?" + key + "&language=dutch&query=" + zoekterm + "&page=1&include_adult=false&region=netherlands"
response = requests.get(url)
print(response.content)
