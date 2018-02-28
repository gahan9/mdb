from threading import Thread
import copy
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from moviesHaven.media_info import FetchMediaInfo
from mysite.tmdb_settings import TMDB_TRAILER_URL
from .utils import *
from mysite.settings import TMDB_SEARCH_URL, TMDB_BASE_URL, DEFAULT_PARAMS, SCRAPE_DIR
from .models import *


class HomePageView(TemplateView):
    """ Home page view """
    template_name = "index.html"
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['movies'] = Movie.objects.all()
        return context


#
# class FilterPageView(TemplateView):
#     """ Filter page view """
#     template_name = "index.html"
#     success_url = reverse_lazy('index')
#
#     def get_context_data(self, **kwargs):
#         context = super(FilterPageView, self).get_context_data(**kwargs)
#         context['entry'] = RawData.objects.all()
#         return context
#
#     def get(self,request):
#         filter_thread = Thread(target=filter_raw_data)
#         filter_thread.start()
#
#         genres = get_genre("tv")
#         genres.update(get_genre("movie"))
#         genre_thread = Thread(target=genre_maker, args=(genres))
#         genre_thread.start()
#         return HttpResponseRedirect(reverse_lazy('index'))

def structure_maker():
    contents = content_fetcher(directory_path=SCRAPE_DIR)
    for video in contents:
        try:
            if not RawData.objects.filter(**video):
                try:
                    raw_object = RawData.objects.create(**video)
                    media_info_obj = FetchMediaInfo()
                    media_data = media_info_obj.get_all_info(os.path.join(video["path"], video["name"]))
                    if media_data:
                        MediaInfo.objects.create(file=raw_object, **media_data)
                except Exception as e:
                    print("Structure Maker exception : {}".format(e))
        except Exception as e:
            print("Structure Maker exception : {}".format(e))


def insert_raw_data(request):
    success_url = reverse_lazy('index')
    fetcher_thread = Thread(target=structure_maker)
    fetcher_thread.start()
    return HttpResponseRedirect(success_url)


def filter_raw_data():
    fetcher = MetaFetcher()
    for entry in MediaInfo.objects.all():
        filter1 = filter_film(entry.file.name)
        if filter1:
            if all(filter1):
                try:
                    structure = fetcher.organize_tv_data(model_instance=entry.file)
                    if structure:
                        title = structure.get('title', None)
                        if title:
                            # XXX: need to check test case if two TV season with same name exist???
                            tv_instance = TVSeries.objects.get_or_create(name=title)[0]
                            season_number = structure.get('season_number', None)
                            if season_number:
                                season_instance = SeasonDetail.objects.get_or_create(series=tv_instance, season_number=season_number)[0]
                                print("---------", season_number)
                                episode_number = structure.get('episode_number', None)
                                if episode_number:
                                    episode_instance = EpisodeDetail.objects.get_or_create(season=season_instance, episode_number=episode_number)[0]
                                    entry.meta_episode = episode_instance
                                    entry.save()
                except Exception as e:
                    print("filter_raw_data: Exception during creating TVSeries object: {}\nfor object- {}".format(e, entry))
                    raise Exception(e)
        else:
            title = fetcher.get_name(entry.file.name)
            # FIXME: handle name match with multiple occurrence of special character
            if '_' in title:
                x = title.split('_')
                title = x[1] if len(x) > 1 else title
            try:
                if title:
                    movie_instance = Movie.objects.get_or_create(title=title)[0]
                    entry.meta_movie = movie_instance
                    entry.save()
            except Exception as e:
                print("Exception during creating Movie object: {}".format(e))


def genre_maker(genres):
    for genre in genres['genres']:
        genre_dict = {"genre_id"  : genre.get('id'),
                      "genre_name": genre.get('name'),
                      }
        if not Genres.objects.filter(**genre_dict):
            try:
                Genres.objects.create(**genre_dict)
            except Exception as e:
                print(e)


def file_filter(request):
    filter_thread = Thread(target=filter_raw_data)
    filter_thread.start()
    genres = get_genre("tv")
    genres.update(get_genre("movie"))
    genre_thread = Thread(target=genre_maker, args=(genres,))
    genre_thread.start()
    return HttpResponseRedirect(reverse_lazy('index'))


def fetch_movie_metadata():
    print("fetching movie data...")
    for movie_instance in Movie.objects.filter(status=False):
        try:
            params = copy.deepcopy(DEFAULT_PARAMS)
            params.update({"query": movie_instance.title})
            movie_result = get_json_response("{}movie/".format(TMDB_SEARCH_URL), params=params)
            if movie_result:
                print(">>>Response of movie data... for {}".format(movie_instance.title))
                movies_data = movie_result.get('results', None)
                if movies_data:
                    movie = movies_data[0]
                    print(">>> Found movie data...")
                    print(">>> {}".format(movies_data.get('id', None)))
                    genre_id = movie.get('genre_ids', None)
                    # for movie in movies_data:
                    if movie:
                        movie_instance.name = movie.get('title', None)
                        movie_instance.tmdb_id = movie.get('id', None)
                        movie_instance.overview = movie.get('overview', None)
                        movie_instance.release_date = movie.get('release_date', None)
                        movie_instance.vote_count = movie.get('vote_count', None)
                        movie_instance.vote_average = movie.get('vote_average', None)
                        # TODO: INCLUDE ME IN CLASS!!! GET TRAILER
                        if movie_instance.tmdb_id:
                            trailer_url = TMDB_TRAILER_URL.format(movie_instance.tmdb_id)
                            trailer_response = get_json_response(trailer_url, DEFAULT_PARAMS)
                            trailer_response = trailer_response.get("results", None)
                            if trailer_response:
                                movie_instance.trailer_id = trailer_response[0].get("key", None)
                        if genre_id:
                            [movie_instance.genre_name.add(Genres.objects.get(genre_id=i)) for i in genre_id]
                        try:
                            movie_instance.save()
                        except Exception as e:
                            print("Movie... saving meta data exception : {}".format(e))
                        image_set_thread = Thread(target=set_image, args=(movie_instance, movie))
                        image_set_thread.start()
                        # movie_instance = set_image(movie_instance, movie)

                        # TODO: INCLUDE ME IN CLASS!!! GET CAST/CREW DATA!
                        cast_movie_url = "{}movie/{}/credits".format(TMDB_BASE_URL, movies_data[0]['id'])
                        cast_list = get_json_response(cast_movie_url, DEFAULT_PARAMS)['cast']
                        for cast in cast_list:
                            person_data = fetch_cast_data(cast)
                            if person_data:
                                if not Person.objects.filter(**person_data):
                                    try:
                                        person_instance = Person.objects.create(**person_data)
                                        try:
                                            PersonRole.objects.create(role="Cast", person=person_instance,
                                                                      movie=movie_instance)
                                        except Exception as e:
                                            print("Exception occurred during creating person role-- {}\n for {}".format(e,
                                                                                                                        person_instance))
                                    except Exception as e:
                                        print("Exception occurred during creating person-- {}".format(e))
                        movie_instance.status = True
                        movie_instance.save()
        except Exception as e:
            print("Exception in movie creation for object :  {}\n Exception: {}".format(movie_instance, e))


def fetch_tv_metadata():
    # LARGE CHANGE to Do
    print("fetching tv data...")
    for tv_instance in TVSeries.objects.filter(status=False):
        params = copy.deepcopy(DEFAULT_PARAMS)
        params.update({"query": tv_instance.title})
        tv_result = get_json_response("{}tv/".format(TMDB_SEARCH_URL), params=params)
        results = tv_result.get('results', None)
        results0 = results[0] if results else None
        tv_id = results[0].get('id', None) if results else None
        genre_ids = results0.get('genre_ids', None) if results0 else None
        url = str(TMDB_BASE_URL) + 'tv/' + str(tv_id) + '/season/' + str(tv_instance.season_number)
        episode_result = get_json_response(url, params=DEFAULT_PARAMS)
        episodes = episode_result.get('episodes', None)
        if episodes:
            for episode in episodes:
                if episode['episode_number'] == tv_instance.episode_number:
                    tv_instance.tmdb_id = episode.get('id')
                    tv_instance.episode_number = episode.get('episode_number')
                    tv_instance.season_number = episode.get('season_number')
                    tv_instance.episode_title = episode.get('name')
                    tv_instance.release_date = episode.get('air_date')
                    tv_instance.overview = episode.get('overview')
                    tv_instance.vote_count = episode.get('vote_count')
                    tv_instance.vote_average = episode.get('vote_average')
                    try:
                        if genre_ids:
                            [tv_instance.genre_name.add(Genres.objects.get(genre_id=i)) for i in genre_ids]
                    except Exception as e:
                        print("Genre adding exception : {}".format(e))
                        # print(e , "second error")
                        tv_instance.save()
                    image_set_thread = Thread(target=set_image, args=(tv_instance, tv_result['results'][0]))
                    image_set_thread.start()

        # FIXME: Use this url for crew+cast : cast_tv_url = "{}tv/{}/season/{}/episode/{}/".format(TMDB_BASE_URL, tv_id)
        cast_tv_url = "{}tv/{}/credits".format(TMDB_BASE_URL, tv_id)
        cast_list = get_json_response(cast_tv_url, DEFAULT_PARAMS)
        cast_list = cast_list.get('cast', None)
        if cast_list:
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
        if cast_list and episodes:
            tv_instance.status = True
            tv_instance.save()


def update_meta_data(request):
    movie_thread = Thread(target=fetch_movie_metadata)
    movie_thread.start()
    # tv_thread = Thread(target=fetch_tv_metadata)
    # tv_thread.start()
    return HttpResponseRedirect(reverse_lazy('index'))
