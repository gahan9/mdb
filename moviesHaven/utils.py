import re
import time

import requests
import os

from mysite.regex import MOVIE_TV_FILTER
from mysite.settings import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_URL, DEFAULT_PARAMS,\
    TEMP_FOLDER_NAME, SUPPORTED_EXTENSIONS


class MetaFetcher(object):
    def __init__(self, *args, **kwargs):
        pass

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
            print("organize_tv_data: Exception fetching season_number for : {}\nException Cause: {}".format(model_instance.name, e))
            return False
        try:
            episode_number = self.name_fetcher(model_instance.name)[4:6]
        except Exception as e:
            print("organize_tv_data: Exception fetching episode_number for : {}\nException Cause: {}".format(model_instance.name, e))
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


def file_category_finder(name):
    if re.search(r'XXX|sexual', name.lower(), re.IGNORECASE):
        return "adult"
    elif re.search(r" - ", name.lower(), re.IGNORECASE):
        return "songs"


def name_fetcher(name):
    try:
        regex = "([s]\d{2})+([e]\d{2})|([s]\dx\d{2})|(\d{2}x\d{2})"
        x = re.search(regex, name.lower()).group(0)
        if not x.startswith('s'):
            return 's' + x.replace("x", "e")
        else:
            return x.replace("x", "e")
    except Exception as e:
        return name


def filter_film(arg):
    if arg:
        season_episode = re.search(r"[s]\d+[e]\d+", arg.lower())
        if season_episode:
            season_episode = season_episode.group(0)
            season, episode = season_episode[0:round(len(season_episode) / 2)].lower(), season_episode[round(len(season_episode) / 2):].lower()
            return season, episode
        else:
            return False
    else:
        return False


def validate_value_existence(key, source_dict):
    if key in source_dict:
        if source_dict[key]:
            return True
        else:
            return False
    else:
        return False


def get_json_response(url, params):
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


def name_catcher(filename):
    value = ' '.join(list(filter(lambda x: x not in re.findall(MOVIE_TV_FILTER, filename, re.IGNORECASE), filename.split('.'))))
    return value


def get_genre(flag):
    url = TMDB_BASE_URL
    if flag == "tv":
        url += "genre/tv/list?"
    elif flag == "movie":
        url += "genre/movie/list?"
    response = requests.get(url, params=DEFAULT_PARAMS)
    return response.json()


def create_file_structure(file_obj):
    try:
        title = file_obj.name  # [:end]
        season_number = name_fetcher(file_obj.name)[1:3]  # [:1][0][0][1:]
        episode_number = name_fetcher(file_obj.name)[4:6]  # [1:][0][0][1:]
        if len(name_catcher(title).split('_')) > 1:
            title = name_catcher(title).split('_')[1]
        else:
            title = name_catcher(title)
        tv_dict = {"title": title,
                   'season_number': season_number, 'episode_number': episode_number}
        return tv_dict
    except Exception as e:
        return None


def set_image(instance, source_json):
    print(">>> In set_image()")
    if validate_value_existence('backdrop_path', source_json):
        fanart_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, 780, source_json.get('backdrop_path'))
        if requests.get(fanart_image_url).status_code == 200:
            instance.fanart_hq = fanart_image_url
    if validate_value_existence('poster_path', source_json):
        thumbnail_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, 300, source_json.get('poster_path'))
        if requests.get(thumbnail_image_url).status_code == 200:
            instance.thumbnail_hq = thumbnail_image_url
    if instance.thumbnail_hq and not instance.thumbnail_lq:
        instance.thumbnail_lq = instance.thumbnail_hq
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
        return "Path Does not exist"
