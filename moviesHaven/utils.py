import requests

from moviesHaven.models import Genres, Person, PersonRole
from mysite.settings import TMDB_API_KEY, TMDB_BASE_URL, LANGUAGE_CODE, API_LANGUAGE_CODE, \
    TMDB_IMAGE_URL, OPTION_QUALITY


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
    params = {"api_key": TMDB_API_KEY, 'language': API_LANGUAGE_CODE}
    r = requests.get(url, params=params)
    genres = r.json()
    for genre in genres['genres']:
        genre_dict = {"genre_id": genre.get('id'),
                      "genre_name": genre.get('name'),
                      }
        if not Genres.objects.filter(**genre_dict):
            try:
                Genres.objects.create(**genre_dict)
            except Exception as e:
                print(e)
                print(Genres.objects.filter(**genre_dict))
                print(genre_dict)


def set_image(movie_instance, source_json):
    print(">>> In set_image()")
    for i in OPTION_QUALITY:
        fanart_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, i, source_json.get('backdrop_path'))
        thumbnail_image_url = "{}w{}/{}".format(TMDB_IMAGE_URL, i, source_json.get('poster_path'))
        # if requests.get(thumbnail_image_url).status_code == 200:
        if True:
            if not movie_instance.thumbnail_hq:
                movie_instance.thumbnail_hq = thumbnail_image_url
                movie_instance.fanart_hq = fanart_image_url
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


def create_person(url, **kwargs):
    print(">>> In create_person()")
    cast_params = {"api_key": TMDB_API_KEY, "language": "fr"}
    cast_result = requests.get(url, params=cast_params)
    for character in cast_result.json()['cast']:
        if 'name' in character:
            person_id = character.get("id")
            person_result = person_fetcher(person_id)
            person_data = {}
            if person_result:
                if "name" in person_result:
                    person_data["name"] = person_result["name"]
                if "birthday" in person_result:
                    person_data["birth_date"] = person_result["birthday"]
                if "profile_path" in person_result:
                    person_data["profile_image"] = person_result["profile_path"]
                if "biography" in person_result:
                    person_data["biography"] = person_result["biography"]
                if "place_of_birth" in person_result:
                    person_data["place_of_birth"] = person_result["place_of_birth"]
                if not Person.objects.filter(**person_data):
                    person_instance = Person.objects.create(**person_data)
                    PersonRole.objects.create(role="Cast", person=person_instance, movie=kwargs['movie'])
