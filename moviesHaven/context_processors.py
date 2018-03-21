from mysite.settings import SITE_NAME, SITE_LOGO, DEFAULT_PORT
from mysite.tmdb_settings import TMDB_IMAGE_URL
from .utils import get_host_name
try:
    _domain = get_host_name()
    if _domain:
        DOMAIN = "http://{}:{}".format(_domain, DEFAULT_PORT)
    else:
        from mysite.directory_settings import DOMAIN
except ImportError:
    DOMAIN = 'http://54.36.48.153:'.format(DEFAULT_PORT)


def site_detail(request):
    return {
        "SITE_NAME": SITE_NAME,
        "SITE_LOGO": SITE_LOGO,
        "DOMAIN": DOMAIN,
        "TMDB_IMAGE_URL": TMDB_IMAGE_URL
    }
