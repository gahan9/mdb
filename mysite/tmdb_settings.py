TMDB_API_KEY = "34142515d9d23817496eeb4ff1d223d0"
TMDB_BASE_URL = "http://api.themoviedb.org/3/"
TMDB_IMAGE_URL = "http://image.tmdb.org/t/p/"
TMDB_SEARCH_URL = TMDB_BASE_URL + "search/"
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie/{id}"
TMDB_TV_URL = "https://api.themoviedb.org/3/tv/{id}"
TMDB_SEASON_URL = TMDB_TV_URL + "/{id}/season/{season_number}"
TMDB_EPISODE_URL = TMDB_SEASON_URL + "/episode/{episode_number}"
TMDB_CREDITS_URL = TMDB_EPISODE_URL + "/credits"


DEFAULT_PARAMS = {"api_key": TMDB_API_KEY, "language": 'fr'}
STREAM_VALIDATOR_API = "https://planetvision.net/api/streaming/check"
OPTION_QUALITY = [1000, 780, 500, 300, 185]
