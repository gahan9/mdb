# coding=utf-8
import re
import time

import requests
import os

from mysite.regex import MOVIE_TV_FILTER
from mysite.settings import TEMP_FOLDER_NAME, SUPPORTED_EXTENSIONS
from mysite.tmdb_settings import *


class DataFilter(object):
    def __init__(self, *args, **kwargs):
        pass

    def filter_film(self, title):
        if title:
            season_episode = re.search(r"[s]\d+[e]\d+", title.lower())
            if season_episode:
                season_episode = season_episode.group(0)
                season = season_episode[0:round(len(season_episode) / 2)].lower()
                episode = season_episode[round(len(season_episode) / 2):].lower()
                return season, episode
            else:
                print("season episode couldn't fetched for : {}".format(title))
                return False
        else:
            print("title not found : {}".format(title))
            return False

    @staticmethod
    def get_name(filename):
        value = ' '.join(
            list(filter(
                lambda x: x not in re.findall(MOVIE_TV_FILTER, filename, re.IGNORECASE),
                filename.split('.'))))
        return value

    @staticmethod
    def name_fetcher(name):
        try:
            regex = r"([s]\d{2})+([e]\d{2})|([s]\dx\d{2})|(\d{2}x\d{2})"
            x = re.search(regex, name.lower()).group(0)
            if not x.startswith('s'):
                return 's' + x.replace("x", "e")
            else:
                return x.replace("x", "e")
        except Exception as e:
            print("Exception in name_fetcher() for : {}\nException Cause: {}".format(name, e))
            return name

    def organize_tv_data(self, model_instance):
        """

        :param model_instance: model instance of raw data
        :return:
        """
        if not model_instance:
            return False
        try:
            season_number = self.name_fetcher(model_instance.name)[1:3]
        except Exception as e:
            print("organize_tv_data: Exception fetching season_number for : {}\nException Cause: {}".format(
                model_instance.name, e))
            return False
        try:
            episode_number = self.name_fetcher(model_instance.name)[4:6]
        except Exception as e:
            print("organize_tv_data: Exception fetching episode_number for : {}\nException Cause: {}".format(
                model_instance.name, e))
            return False
        try:
            title = self.get_name(model_instance.name)
            # FIXME: This behaviour won't be tolerated.. it will break for exception i.e. *__* or *_2018_*
            if len(title.split('_')) > 1:
                title = title.split('_')[1]
            print(title, season_number, episode_number)
            return {"title": title, 'season_number': season_number, 'episode_number': episode_number}
        except Exception as e:
            print("organize_tv_data: Exception for : {}\nException Cause: {}".format(model_instance.name, e))
            return False


class MetaFetcher(object):
    def __init__(self, *args, **kwargs):
        self.default_movie_id = 1726  # Iron Man TMDB ID
        self.movie_url = TMDB_MOVIE_URL.format(id=self.default_movie_id)
        self.movie_credits_url = self.movie_url + "/credits"
        self.default_trailer_url = TMDB_TRAILER_URL.format(id=self.default_movie_id)
        self.default_tv_id = 71728  # Young Sheldon TMDB ID
        self.default_season = 1
        self.default_episode = 1
        self.tv_url = TMDB_TV_URL.format(id=self.default_tv_id)
        self.season_url = TMDB_SEASON_URL.format(id=self.default_tv_id, season_number=self.default_season)
        self.episode_url = TMDB_EPISODE_URL.format(id=self.default_tv_id, season_number=self.default_season,
                                                   episode_number=self.default_episode)
        self.episode_credits_url = self.episode_url + "/credits"
        self.params = DEFAULT_PARAMS
        self.backdrop_path = TMDB_BACKDROP_PATH
        self.poster_path = TMDB_POSTER_PATH
        self.default_person_id = 3223  # Robert Downey Jr.
        self.person_url = TMDB_PERSON_URL.format(id=self.default_person_id)

    def get_movie_url(self, movie_id=None):
        if movie_id:
            return TMDB_MOVIE_URL.format(id=movie_id)
        else:
            return False

    def get_movie_trailer_url(self, movie_id=None):
        if movie_id:
            return TMDB_TRAILER_URL.format(id=movie_id)
        else:
            return False

    def get_credits_url(self, movie_id=None):
        if movie_id:
            return TMDB_MOVIE_CREDITS_URL.format(id=movie_id)
        else:
            return False

    def get_tv_url(self, tv_id=None):
        if tv_id:
            return TMDB_TV_URL.format(id=tv_id)
        else:
            return False

    def get_season_url(self, tv_id=None, season_number=None):
        if tv_id and season_number is not None:
            return TMDB_SEASON_URL.format(id=tv_id, season_number=season_number)
        else:
            return False

    def get_episode_url(self, tv_id=None, season_number=None, episode_number=None):
        if tv_id and season_number is not None and episode_number is not None:
            return TMDB_EPISODE_URL.format(id=tv_id, season_number=season_number, episode_number=episode_number)
        else:
            return False

    def get_episode_credits_url (self, tv_id=None, season_number=None, episode_number=None):
        if tv_id and season_number is not None and episode_number is not None:
            return TMDB_EPISODE_CREDITS_URL.format(id=tv_id, season_number=season_number, episode_number=episode_number)
        else:
            return False

    def get_person_url(self, person_id=None):
        if person_id:
            return TMDB_PERSON_URL.format(id=person_id)
        else:
            return False

    def get_person_detail(self, person_id=None):
        _url = self.get_person_url(person_id)
        if _url:
            try:
                _response = get_json_response(_url)
                if _response:
                    cast_data = {
                        'popularity'    : _response.get('popularity', None),
                        'place_of_birth': _response.get('place_of_birth', None),
                        'biography'     : _response.get('biography', None),
                        'birthday'      : _response.get('birthday', None),
                        'deathday'      : _response.get('deathday', None),
                        'homepage'      : _response.get('homepage', None),
                        'imdb_id'       : _response.get('imdb_id', None),
                    }
                    _profile_path = _response.get('profile_path', None)
                    if _profile_path:
                        cast_data['profile_path'] = "{}{}".format(self.poster_path, _profile_path)
                    return cast_data
            except Exception as e:
                return False

    def get_movie_trailer(self, movie_id=None):
        if movie_id:
            _response = get_json_response(self.get_movie_trailer_url(movie_id))
            if _response:
                _result = _response.get('results', None)
                if _result:
                    try:
                        return _result[0].get("key", None)
                    except Exception as e:
                        print(
                            "Caught Exception: {}\n while performing get_movie_trailer() for id {}".format(e, movie_id))
                        return False
        else:
            return False

    def get_credits(self, movie_id=None, url=None):
        if not url:
            url = self.get_credits_url(movie_id)
        _cast_list = []
        _crew_list = []
        if movie_id:
            _response = get_json_response(url, params=self.params)
            if _response:
                cast = _response.get('cast', None)
                crew = _response.get('crew', None)
                if cast:
                    for person in cast:
                        try:
                            _cast_list.append({
                                'cast_id'  : person.get('cast_id', None),
                                'tmdb_id'  : person.get('id', None),
                                'role'     : 'cast',
                                'name'     : person.get('name', None),
                                'gender'   : person.get('gender', None),
                                'character': person.get('character', None)
                            })
                        except:
                            pass
                if crew:
                    for person in crew:
                        try:
                            _crew_list.append({
                                'tmdb_id'  : person.get('id', None),
                                'role'     : person.get('job', None),
                                'name'     : person.get('name', None),
                                'gender'   : person.get('gender', None),
                                'character': person.get('department', None)
                            })
                        except:
                            pass
        return _cast_list, _crew_list

    def get_tv_detail(self, tv_id=None):
        _url = self.get_tv_url(tv_id)
        if _url:
            _response = get_json_response(_url)
            if _response:
                tv_data = {
                    'tmdb_id'          : _response.get('id', None),
                    'name'             : _response.get('name', None),
                    'original_name'    : _response.get('original_name', None),
                    'first_air_date'   : _response.get('first_air_date', None),
                    'vote_average'     : _response.get('vote_average', None),
                    'overview'         : _response.get('overview', None),
                    'season_status'    : _response.get('season_status', None),
                    'origin_country'   : _response.get('origin_country', None),
                    'original_language': _response.get('original_language', None),
                }
                _backdrop_path = _response.get('backdrop_path', None)
                _poster_path = _response.get('poster_path', None)
                if _backdrop_path:
                    tv_data['backdrop_path'] = "{}{}".format(self.backdrop_path, _backdrop_path)
                if _poster_path:
                    tv_data['poster_path'] = "{}{}".format(self.poster_path, _poster_path)
                return tv_data
        else:
            return False

    def get_season_detail(self, tv_id=None, season_number=None):
        _url = self.get_season_url(tv_id, season_number)
        if _url:
            _response = get_json_response(_url)
            if _response:
                season_data = {
                    'tmdb_id'       : _response.get('id', None),
                    'name'          : _response.get('name', None),
                    'episode_number': _response.get('episode_number', None),
                    'air_date'      : _response.get('air_date', None),
                    'vote_average'  : _response.get('vote_average', None),
                    'vote_count'    : _response.get('vote_count', None),
                    'overview'      : _response.get('overview', None),
                }
                _backdrop_path = _response.get('backdrop_path', None)
                _poster_path = _response.get('poster_path', None)
                if _backdrop_path:
                    season_data['backdrop_path'] = "{}{}".format(self.backdrop_path, _backdrop_path)
                if _poster_path:
                    season_data['poster_path'] = "{}{}".format(self.poster_path, _poster_path)
                return season_data
        else:
            return False

    def get_episode_detail(self, tv_id=None, season_number=None, episode_number=None):
        _url = self.get_episode_url(tv_id, season_number, episode_number)
        if _url:
            _response = get_json_response(_url)
            if _response:
                episode_data = {
                    'tmdb_id'       : _response.get('id', None),
                    'name'          : _response.get('name', None),
                    'episode_number': _response.get('episode_number', None),
                    'air_date'      : _response.get('air_date', None),
                    'vote_average'  : _response.get('vote_average', None),
                    'vote_count'    : _response.get('vote_count', None),
                    'overview'      : _response.get('overview', None),
                }
                _poster_path = _response.get('still_path', None)
                if _poster_path:
                    episode_data['poster_path'] = "{}{}".format(self.poster_path, _poster_path)
                print("Episode data found: {}".format(episode_data.get('tmdb_id')))
                return episode_data
        else:
            return False


def file_category_finder(name):
    if re.search(r'XXX|sexual', name.lower(), re.IGNORECASE):
        return "adult"
    elif re.search(r" - ", name.lower(), re.IGNORECASE):
        return "songs"


def get_json_response(url, params=DEFAULT_PARAMS):
    try:
        response = requests.get(url, params=params).json()
        status_code = response.get('status_code', None)
        if status_code:
            while status_code == 25:
                time.sleep(10)
                return get_json_response(url, params)
        else:
            return response
    except Exception as e:
        # print(url, params)
        return {"request_error": "Couldn't get any response", "detail": str(e)}


def get_genre(flag):
    url = TMDB_BASE_URL
    if flag == "tv":
        url += "genre/tv/list?"
    elif flag == "movie":
        url += "genre/movie/list?"
    response = requests.get(url, params=DEFAULT_PARAMS)
    return response.json()


def set_image(instance, source_json):
    print(">>> In set_image()")
    if source_json.get('backdrop_path', None):
        fanart_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, 780, source_json.get('backdrop_path'))
        if requests.get(fanart_image_url).status_code == 200:
            instance.fanart_hq = fanart_image_url
    if source_json.get('poster_path', None):
        thumbnail_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, 300, source_json.get('poster_path'))
        if requests.get(thumbnail_image_url).status_code == 200:
            instance.thumbnail_hq = thumbnail_image_url
    if instance.thumbnail_hq and not instance.thumbnail_lq:
        instance.thumbnail_lq = instance.thumbnail_hq
    if instance.fanart_hq and not instance.fanart_lq:
        instance.fanart_lq = instance.fanart_hq
    instance.save()
    return instance


def person_fetcher(p_id):
    person_url = str(TMDB_BASE_URL) + 'person/' + str(p_id)
    cast_params = {"api_key": TMDB_API_KEY, "language": "fr"}
    person_result = requests.get(person_url, params=cast_params).json()
    return person_result


def fetch_cast_data(cast_json):
    print(">>> In fetch_cast_data()")
    if 'name' in cast_json:
        person_id = cast_json.get("id")
        person_result = person_fetcher(person_id)
        person_data = {}
        if person_result:
            try:
                for key, value in person_result.items():
                    if key in ["name", "birthday", "profile_path", "biography", "place_of_birth"]:
                        if key == "profile_path":
                            if value:
                                person_data[key] = "{}w300{}".format(TMDB_IMAGE_URL, value)
                        else:
                            if value:
                                person_data[key] = value
            except Exception as e:
                # print("*" * 10)
                print(person_result, sep="\n")
                # print("*" * 10)
                # raise Exception
        return person_data


def content_fetcher(directory_path):
    data_set = []
    if os.path.exists(directory_path):
        for root, directory, files in os.walk(directory_path, topdown=True):
            if TEMP_FOLDER_NAME in root:
                continue
            else:
                for name in files:
                    if name.split('.')[-1] in SUPPORTED_EXTENSIONS:
                        d = {"name": name, "path": root, "extension": name.split('.')[-1]}
                        data_set.append(d)
        return data_set
    else:
        print("content_fetcher: path does not exist : {}".format(directory_path))
        return False
