import re
import requests

from mysite.settings import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_URL, OPTION_QUALITY, DEFAULT_PARAMS


name_fetcher = lambda x: ' '.join(x.split('_')[1].split('.')[:-1])


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
    #TODO: make regex in single expression
    try:
        arg = str(arg)
    except Exception as e:
        return ("Enter valid string {}".format(e),)

    regexOut = re.findall(r"[s]\d+[e]\d+", arg.lower())
    regSea = re.findall(r"[s]\d+", (str(regexOut).split(',')[0]).lower())
    regEpi = re.findall(r"[e]\d+", (str(regexOut).split(',')[0]).lower())
    tup = regSea, regEpi
    return tup


def get_genre(flag):
    url = TMDB_BASE_URL
    if flag == "tv":
        url += "genre/tv/list?"
    elif flag == "movie":
        url += "genre/movie/list?"
    response = requests.get(url, params=DEFAULT_PARAMS)
    return response.json()


def create_file_structure(file_obj, flag):
    end = re.search(r"[s]\d+[e]\d+", name_fetcher(file_obj.name)).start()
    title = name_fetcher(file_obj.name)[:end]
    season_number = filter_film(file_obj)[:1][0][0][1:]
    episode_number = filter_film(file_obj)[1:][0][0][1:]
    tv_dict = {"local_data"   : file_obj, "title": title,
               'season_number': season_number, 'episode_number': episode_number}
    return tv_dict


def set_image(movie_instance, source_json):
    print(">>> In set_image()")
    for i in OPTION_QUALITY:
        fanart_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, i, source_json.get('backdrop_path'))
        thumbnail_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, i, source_json.get('poster_path'))
        if requests.get(thumbnail_image_url).status_code == 200:
            if not movie_instance.thumbnail_hq:
                movie_instance.thumbnail_hq = thumbnail_image_url
                movie_instance.fanart_hq = fanart_image_url
                continue
            elif movie_instance.thumbnail_hq and not movie_instance.thumbnail_lq:
                movie_instance.thumbnail_lq = thumbnail_image_url
                movie_instance.fanart_lq = fanart_image_url
                break
            if movie_instance.thumbnail_hq and not movie_instance.thumbnail_lq:
                movie_instance.thumbnail_lq = movie_instance.thumbnail_hq
    movie_instance.save()
    return movie_instance


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
            for key, value in person_result:
                if key in ["name", "birthday", "profile_path", "biography", "place_of_birth"]:
                    if value:
                        person_data[key] = value
        return person_data
