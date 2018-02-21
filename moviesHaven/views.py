import json
import re
import requests

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.db import IntegrityError

from moviesHaven.utils import get_genre
from moviesHaven.worker import name_fetcher, filter_film
from mysite.settings import TMDB_SEARCH_URL, TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_URL, option_quality
from .models import *
from .worker import content_fetcher


def index(request):
    movies = Movie.objects.all()
    return render(request, 'index.html', {'movies': movies})


def insert_raw_data(request):
    success_url = reverse_lazy('index')
    contents = content_fetcher(directory_path=r"E:\dir")
    for video in contents:
        if RawData.objects.filter(**video):
            pass
        else:
            RawData.objects.create(**video)
    return HttpResponseRedirect(success_url)


def film_splitter(request):
    for x in RawData.objects.all():
        if all(filter_film(x)):
            try:
                end = re.search(r"[s]\d+[e]\d+", name_fetcher(x.name)).start()

                title = name_fetcher(x.name)[:end]

                season_number = filter_film(x)[:1][0][0][1:]
                episode_number = filter_film(x)[1:][0][0][1:]

                tv_dict = {"local_data": x, "title": title,
                           'season_number': season_number, 'episode_number': episode_number}

                if not TVSeries.objects.filter(**tv_dict):
                    TVSeries.objects.create(**tv_dict)
            except IntegrityError:
                pass
        else:
            try:
                movie_dict = {"local_data": x,
                              "title": name_fetcher(x.name)}
                if Movie.objects.filter(**{'title': name_fetcher(x.name)}):
                    pass
                else:
                    Movie.objects.create(**movie_dict)
            except IntegrityError:
                pass

        get_genre("tv")
        get_genre("movie")
        # genres = get_genre("tv")
        # for genre in genres:
        #     genre_dict = {"genre_id": genre.get('id'),
        #                   "genre_name": genre.get('name'),
        #                   }
        #     if not Genres.objects.filter(**genre_dict):
        #         Genres.objects.create(**genre_dict)
        # genres = get_genre("movie")
        # for genre in genres:
        #     genre_dict = {"genre_id": genre.get('id'),
        #                   "genre_name": genre.get('name'),
        #                   }
        #     if not Genres.objects.filter(**genre_dict):
        #         Genres.objects.create(**genre_dict)
    return HttpResponse("done!")


def person_fetcher():
    pass
    # params = {"api_key": TMDB_API_KEY,
    #           "language": "fr"
    #           }
    #
    # url = TMDB_BASE_URL + 'person/' +
    #
    # movie_result = requests.get(url, params=params)
    #
    # movies_data = movie_result.json()['results']
    #
    # for persons in Person.objects.all():
    #     persons.birth_date = items.get("birthday")
    #     persons.name =


def fetch_api_data(request):
    for movies in Movie.objects.filter(status=False):
        params = {"api_key": TMDB_API_KEY,
                  "query": movies.title,
                  "language": "fr"
                  }
        url = TMDB_SEARCH_URL + 'movie/'
        movie_result = requests.get(url, params=params)
        movies_data = movie_result.json()['results']

        if movies_data:
            if 'genre_ids' in movies_data[0]:
                genre_id = movies_data[0]['genre_ids']

            for movie in movies_data:
                movies.title = movie.get('title')
                movies.overview = movie.get('overview')
                movies.release_date = movie.get('release_date')
                movies.vote_count = movie.get('vote_count')
                movies.vote_average = movie.get('vote_average')

                for i in option_quality:
                    fanart_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, i, movie.get('backdrop_path'))
                    thumbnail_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, i, movie.get('poster_path'))
                    if requests.get(thumbnail_image_url).status_code == 200:
                        if not movies.thumbnail_hq:
                            movies.thumbnail_hq = thumbnail_image_url
                            movies.fanart_hq = fanart_image_url
                        elif movies.thumbnail_hq and not movies.thumbnail_lq:
                            movies.thumbnail_lq = thumbnail_image_url
                            movies.fanart_lq = fanart_image_url
                            break
                        if movies.thumbnail_hq and not movies.thumbnail_lq:
                            movies.thumbnail_lq = movies.thumbnail_hq
                movies.save()
                [movies.genre_name.add(Genres.objects.get(genre_id=i)) for i in genre_id]

            # GET CAST/CREW DATA!
            movie_id = movies_data[0]['id']
            cast_movie_url = str(TMDB_BASE_URL) + 'movie/' + str(movie_id) + '/credits'
            cast_params = {"api_key": TMDB_API_KEY, "language": "fr"}
            cast_result = requests.get(cast_movie_url, params=cast_params)
            for character in cast_result.json()['cast']:
                if 'name' in character:
                    person_id = character.get("id")
                    person_fetcher(person_id)

            # for person in person_result.json()['cast']:

            # ---------------------------------------------------
            # for persons in Person.objects.all():
            # persons.birth_date = items.get("birthday")
            # persons.name =

            # print(casts)
            # for cast in casts:
            #     person.name = cast.get("name")
            #     person.profile_image = cast.get("profile_path")
            #     person.save()

    #
    # for tv in TVSeries.objects.filter(status=False):
    #
    #     params = {"api_key": TMDB_API_KEY,
    #               "query": tv.title,
    #               "language": "fr"
    #               }
    #
    #     search_result = requests.get("{}tv/".format(TMDB_SEARCH_URL), params=params)
    #     data = search_result.json()
    #
    #     tv_id = data['results'][0]['id']
    #     genre_id = data['results'][0]['genre_ids']
    #
    #     # url = "{}".format(TMDB_BASE_URL, 'tv/', id, '/season/', tv.season_number)
    #     url = str(TMDB_BASE_URL) + 'tv/' + str(tv_id) + '/season/' + str(tv.season_number)
    #     episode_result = requests.get(url, params=params)
    #     episodes = episode_result.json()['episodes']
    #
    #     for episode in episodes:
    #         if episode['episode_number'] == tv.episode_number:
    #             tv.episode_number = episode.get('episode_number')  # title
    #             tv.season_number = episode.get('season_number')  # description
    #             tv.episode_title = episode.get('name')  # genres
    #             tv.release_date = episode.get('air_date')  # numVotes
    #             tv.overview = episode.get('overview')  # averageRating
    #             tv.vote_count = episode.get('vote_count')
    #             tv.vote_average = episode.get('vote_average')
    #
    # for i in option_quality:
    #     thumbnail_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, i, episode_result.json().get('poster_path'))
    #     fanart_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, i, data['results'][0]['backdrop_path'])
    #     if requests.get(thumbnail_image_url).status_code == 200:
    #         if not tv.thumbnail_hq:
    #             tv.thumbnail_hq = thumbnail_image_url
    #             tv.fanart_hq = fanart_image_url
    #         elif tv.thumbnail_hq and not tv.thumbnail_lq:
    #             tv.thumbnail_lq = thumbnail_image_url
    #             tv.fanart_lq = fanart_image_url
    #             break
    # if tv.thumbnail_hq and not tv.thumbnail_lq:
    #     tv.thumbnail_lq = tv.thumbnail_hq
    # tv.save()
    #             #----- TVSeries.objects.filter(id=tv.id).update(**tv_dict)
    #             [tv.genre_name.add(Genres.objects.get(genre_id=i)) for i in genre_id]
    #
    #     cast_url = str(TMDB_BASE_URL) + 'tv/' + str(tv_id) + '/credits'
    #     cast_params = {"api_key": TMDB_API_KEY,
    #                    "language": "fr"
    #                   }
    #
    #     cast_result = requests.get(cast_url, params=cast_params)
    #     casts = cast_result.json()['cast']
    #
    #     print()

    return HttpResponse("Okay!")


def person_fetcher(p_id):
    person_url = str(TMDB_BASE_URL) + 'person/' + str(p_id)
    cast_params = {"api_key": TMDB_API_KEY, "language": "fr"}
    person_result = requests.get(person_url, params=cast_params).json()
    if person_result and not Person.objects.filter(**{"name": person_result["name"]}):
        person = Person.objects.create()
        if "name" in person_result:
            person.name = person_result["name"]
        if "birthday" in person_result:
            person.birth_date = person_result["birthday"]
        if "profile_path" in person_result:
            person.profile_image = person_result["profile_path"]
        if "biography" in person_result:
            person.biography = person_result["biography"]
        if "place_of_birth" in person_result:
            person.place_of_birth = person_result["place_of_birth"]
        person.save()
