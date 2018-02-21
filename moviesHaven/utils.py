import requests

from moviesHaven.models import Genres
from mysite.settings import TMDB_API_KEY, TMDB_BASE_URL, LANGUAGE_CODE


# def get_movie_genre():
#     url = TMDB_BASE_URL + "genre/movie/list?"
#     params = {"api_key": TMDB_API_KEY}
#     r = requests.get(url, params=params)
#     genres = r.json()
#     return genres['genres']
#
#
# def get_tv_genre():
#     url = TMDB_BASE_URL + "genre/tv/list?"
#     params = {"api_key": TMDB_API_KEY}
#     r = requests.get(url, params=params)
#     genres = r.json()
#     return genres['genres']


def get_genre(flag):
    if flag == "tv":
        url = TMDB_BASE_URL + "genre/tv/list?"
    elif flag == "movie":
        url = TMDB_BASE_URL + "genre/movie/list?"
    params = {"api_key": TMDB_API_KEY, 'language':LANGUAGE_CODE}
    r = requests.get(url, params=params)
    genres = r.json()
    for genre in genres['genres']:
        genre_dict = {"genre_id": genre.get('id'),
                      "genre_name": genre.get('name'),
                      }
        if not Genres.objects.filter(**genre_dict):
            Genres.objects.create(**genre_dict)
