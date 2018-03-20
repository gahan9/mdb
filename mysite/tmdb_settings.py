# Common tmdb Data and url
TMDB_API_KEY = "34142515d9d23817496eeb4ff1d223d0"
TMDB_BASE_URL = "http://api.themoviedb.org/3/"
TMDB_IMAGE_URL = "http://image.tmdb.org/t/p/"
TMDB_SEARCH_URL = TMDB_BASE_URL + "search/"
# Movie urls
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie/{id}"
TMDB_MOVIE_CREDITS_URL = TMDB_MOVIE_URL + "/credits"
TMDB_TRAILER_URL = TMDB_MOVIE_URL + "/videos"
MOVIE_EXTERNAL_ID = TMDB_MOVIE_URL + "/external_ids"
# TV urls
TMDB_TV_URL = "https://api.themoviedb.org/3/tv/{id}"
TMDB_SEASON_URL = TMDB_TV_URL + "/season/{season_number}"
TMDB_EPISODE_URL = TMDB_SEASON_URL + "/episode/{episode_number}"
TMDB_EPISODE_CREDITS_URL = TMDB_EPISODE_URL + "/credits"
TV_EXTERNAL_ID = TMDB_SEASON_URL + "/external_ids"
EPISODE_EXTERNAL_ID = TMDB_EPISODE_URL + "/external_ids"
# common urls
TMDB_PERSON_URL = TMDB_BASE_URL + "person/{id}"
TMDB_BACKDROP_PATH = TMDB_IMAGE_URL + "w780"
TMDB_POSTER_PATH = TMDB_IMAGE_URL + "w300"
# default params
DEFAULT_PARAMS = {"api_key": TMDB_API_KEY, "language": 'fr'}
# other constants
STREAM_VALIDATOR_API = "https://planetvision.net/api/streaming/check"
OPTION_QUALITY = [1000, 780, 500, 300, 185]
MEDIA_MAP = "/media/data"
