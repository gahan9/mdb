import re
import requests

from mysite.settings import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_URL, DEFAULT_PARAMS
from mysite.tmdb_settings import EXCLUDE


def name_fetcher(name):
    try:
        regex = "([s]\d{2})+([e]\d{2})|([s]\dx\d{2})|(\d{2}x\d{2})"
        x = re.search(regex,name.lower()).group(0)
        if not x.startswith('s'):
            return 's' + x.replace("x","e")
        else:
            return x.replace("x","e")
    except Exception as e:
        return name


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
        return response
    except Exception as e:
        return {"error": "Couldn't get any response", "detail": str(e)}


def filter_film(arg):
    regex_output = name_fetcher(arg)
    regex_season = re.findall(r"[s]\d+", regex_output.lower())
    regex_episode = re.findall(r"[e]\d+", regex_output.lower())
    return regex_season, regex_episode

def name_catcher(filename):
    value = ' '.join(list(filter(lambda x: x not in re.findall(EXCLUDE, filename), filename.split('.'))))
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
        season_number = name_fetcher(file_obj.name)[1:3] # [:1][0][0][1:]
        episode_number = name_fetcher(file_obj.name)[4:6] # [1:][0][0][1:]
        if len(name_catcher(title).split('_')) > 1:
            title = name_catcher(title).split('_')[1]
        else:
            title = name_catcher(title)
        tv_dict = {"local_data": file_obj, "name": title,
                       'season_number': season_number, 'episode_number': episode_number}
        return tv_dict
    except:
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
                        if value:
                            person_data[key] = value
            except Exception as e:
                print("*" * 10)
                print(person_result, sep="\n")
                print("*" * 10)
                raise Exception
        return person_data
