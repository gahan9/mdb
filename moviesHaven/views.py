from threading import Thread
import copy

import requests
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from moviesHaven.utils import get_genre, set_image, create_file_structure, get_json_response, \
    fetch_cast_data, filter_film, name_fetcher, validate_value_existence
from mysite.settings import TMDB_SEARCH_URL, TMDB_BASE_URL, SCRAPE_DIR, DEFAULT_PARAMS, TMDB_IMAGE_URL
from .models import *
from .worker import content_fetcher


class HomePageView(TemplateView):
    """ Home page view """
    template_name = "index.html"
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['movies'] = Movie.objects.all()
        return context


def insert_raw_data(request):
    success_url = reverse_lazy('index')
    contents = content_fetcher(directory_path=SCRAPE_DIR)
    for video in contents:
        if RawData.objects.filter(**video):
            pass
        else:
            RawData.objects.create(**video)
    return HttpResponseRedirect(success_url)


def filter_raw_data():
    for entry in RawData.objects.all():
        if all(filter_film(entry.name)):
            structure = create_file_structure(file_obj=entry)
            try:
                if not TVSeries.objects.filter(**structure):
                    TVSeries.objects.create(**structure)
            except Exception as e:
                print("Exception during creating TVSeries object: {}".format(e))
        else:
            movie_dict = {"local_data": entry, "name": name_fetcher(entry.name)}
            try:
                if not Movie.objects.filter(**movie_dict):
                    Movie.objects.create(**movie_dict)
            except Exception as e:
                print("Exception during creating Movie object: {}".format(e))


def film_splitter(request):
    filter_raw_data()

    genres = get_genre("tv")
    genres.update(get_genre("movie"))
    for genre in genres['genres']:
        genre_dict = {"genre_id"  : genre.get('id'),
                      "genre_name": genre.get('name'),
                      }
        if not Genres.objects.filter(**genre_dict):
            try:
                Genres.objects.create(**genre_dict)
            except Exception as e:
                print(e)
    return HttpResponseRedirect(reverse_lazy('index'))


def fetch_movie_metadata():
    print("fetching movie data...")
    for movie_instance in Movie.objects.filter(status=False):
        params = copy.deepcopy(DEFAULT_PARAMS)
        params.update({"query": movie_instance.name})
        movie_result = get_json_response("{}movie/".format(TMDB_SEARCH_URL), params=params)
        print(movie_result)
        if 'results' in movie_result:
            movies_data = movie_result['results']
            if movies_data:
                print(">>> Found movie data...")
                if 'genre_ids' in movies_data[0]:
                    if movies_data[0]['genre_ids']:
                        genre_id = movies_data[0]['genre_ids']

                for movie in movies_data:
                    movie_instance.name = movie.get('title')
                    movie_instance.overview = movie.get('overview')
                    movie_instance.release_date = movie.get('release_date')
                    movie_instance.vote_count = movie.get('vote_count')
                    movie_instance.vote_average = movie.get('vote_average')
                    [movie_instance.genre_name.add(Genres.objects.get(genre_id=i)) for i in genre_id]
                    movie_instance.save()
                    image_set_thread = Thread(target=set_image, args=(movie_instance, movie))
                    image_set_thread.start()
                    # movie_instance = set_image(movie_instance, movie)
                # GET CAST/CREW DATA!
                cast_movie_url = "{}movie/{}/credits".format(TMDB_BASE_URL, movies_data[0]['id'])
                cast_list = get_json_response(cast_movie_url, DEFAULT_PARAMS)['cast']
                for cast in cast_list:
                    person_data = fetch_cast_data(cast)
                    if person_data:
                        if not Person.objects.filter(**person_data):
                            try:
                                person_instance = Person.objects.create(**person_data)
                                try:
                                    PersonRole.objects.create(role="Cast", person=person_instance, movie=movie_instance)
                                except Exception as e:
                                    print("Exception occurred during creating person role-- {}\n for {}".format(e, person_instance))
                            except Exception as e:
                                print("Exception occurred during creating person-- {}".format(e))
                movie_instance.status = True
                movie_instance.save()


def fetch_tv_metadata():
    print("fetching tv data...")
    for tv_instance in TVSeries.objects.filter(status=False):
        params = copy.deepcopy(DEFAULT_PARAMS)
        params.update({"query": tv_instance.name})
        tv_result = get_json_response("{}tv/".format(TMDB_SEARCH_URL), params=params)

        if 'genre_ids' in tv_result['results'][0]:
            if tv_result['results'][0]['genre_ids']:
                genre_id = tv_result['results'][0]['genre_ids']
        tv_id = tv_result['results'][0]['id']
        url = str(TMDB_BASE_URL) + 'tv/' + str(tv_id) + '/season/' + str(tv_instance.season_number)
        episode_result = get_json_response(url, params=params)
        episodes = episode_result['episodes']

        for episode in episodes:
            if episode['episode_number'] == tv_instance.episode_number:
                tv_instance.episode_number = episode.get('episode_number')
                tv_instance.season_number = episode.get('season_number')
                tv_instance.episode_title = episode.get('name')
                tv_instance.release_date = episode.get('air_date')
                tv_instance.overview = episode.get('overview')
                tv_instance.vote_count = episode.get('vote_count')
                tv_instance.vote_average = episode.get('vote_average')
                try:
                    [tv_instance.genre_name.add(Genres.objects.get(genre_id=i)) for i in genre_id]
                except Exception as e:
                    pass
                    # print(e , "second error")
                    tv_instance.save()

                image_set_thread = Thread(target=set_image, args=(tv_instance, tv_result['results'][0]))
                image_set_thread.start()
        cast_tv_url = "{}tv/{}/credits".format(TMDB_BASE_URL, tv_id)
        cast_list = get_json_response(cast_tv_url, DEFAULT_PARAMS)['cast']

        for cast in cast_list:
            person_data = fetch_cast_data(cast)
            if person_data:
                if not Person.objects.filter(**person_data):
                    try:
                        person_instance = Person.objects.create(**person_data)
                        try:
                            PersonRole.objects.create(role="Cast", person=person_instance, tv=tv_instance)
                        except Exception as e:
                            print("Exception occurred during creating person role-- {}\n for {}".format(
                                e, person_instance))
                    except Exception as e:
                        print("Exception occurred during creating person-- {}".format(e))
        tv_instance.status = True
        tv_instance.save()


def update_meta_data(request):
    movie_thread = Thread(target=fetch_movie_metadata)
    movie_thread.start()
    tv_thread = Thread(target=fetch_tv_metadata)
    tv_thread.start()
    return HttpResponseRedirect(reverse_lazy('index'))
