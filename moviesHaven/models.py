import os
import urllib

from django.forms.models import model_to_dict
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from field_history.tracker import FieldHistoryTracker

from mysite.directory_settings import *


class PathHash(models.Model):
    path = models.CharField(max_length=1500)
    path_last_modified = models.FloatField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Path Hash"
        verbose_name_plural = verbose_name


class RawData(models.Model):
    name = models.CharField(max_length=1500, blank=True, null=True)
    path = models.CharField(max_length=1500, blank=True, null=True)
    extension = models.CharField(blank=True, null=True, max_length=10)

    def get_details(self):
        return model_to_dict(self)

    def get_reference_id(self):
        _id = self.id
        _app_name = os.path.basename(os.path.dirname(__file__))
        _model_name = self.__class__.__name__.lower()
        _url = reverse_lazy('admin:{}_{}_changelist'.format(_app_name, _model_name))
        _href = "<a href='{0}{1}/change/'>{1}</a>".format(_url, _id)
        return _href

    @property
    def get_full_path(self):
        return os.path.join(self.path, self.name)

    @property
    def get_file_name(self):
        return self.name

    def __str__(self):
        return "{}- {}".format(self.id, self.name)[:50]

    class Meta:
        verbose_name = _("Raw Video Data in local")
        verbose_name_plural = _("Raw Video Data in local")
        unique_together = ('name', 'path')


class Person(models.Model):
    GENDER_CHOICES = (
        (0, "Unknown"),
        (1, "Female"),
        (2, "Male"),
    )
    STATUS_CHOICE = (
        (0, "to be scan"),
        (1, "Scanned"),
        (2, "Updated")
    )
    cast_id = models.CharField(max_length=50, blank=True, null=True)
    tmdb_id = models.CharField(max_length=50, blank=True, null=True)
    imdb_id = models.CharField(max_length=50, blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, blank=True, null=True)  # can be filled in slot 1
    name = models.CharField(null=True, blank=True, max_length=100)  # filled in slot 1
    birthday = models.CharField(null=True, blank=True, max_length=100)
    deathday = models.CharField(null=True, blank=True, max_length=100)
    profile_path = models.URLField(max_length=1000, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=200, null=True, blank=True)
    popularity = models.FloatField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=0)

    def get_reference_id(self):
        _id = self.id
        _app_name = os.path.basename(os.path.dirname(__file__))
        _model_name = self.__class__.__name__.lower()
        _url = reverse_lazy('admin:{}_{}_changelist'.format(_app_name, _model_name))
        _href = "<a href='{0}{1}/change/'>{1}</a>".format(_url, _id)
        return _href

    def __str__(self):
        return "{}".format(self.name)

    @property
    def get_short_biography(self):
        if self.biography:
            return self.biography[:15]
        else:
            return self.biography


class Genres(models.Model):
    genre_id = models.IntegerField(unique=True)
    genre_name = models.CharField(max_length=256)
    poster_path = models.URLField(max_length=1000, verbose_name=_("Thumbnail"),
                                  help_text=_("Enter image URL of resolution width 300"),
                                  blank=True, null=True)
    backdrop_path = models.URLField(max_length=1000, verbose_name=_("Fan Art"),
                                    help_text=_("Enter image URL of resolution width 780"),
                                    blank=True, null=True)
    field_history = FieldHistoryTracker(['genre_id', 'genre_name', 'poster_path'])

    def get_reference_id(self):
        _id = self.id
        _app_name = os.path.basename(os.path.dirname(__file__))
        _model_name = self.__class__.__name__.lower()
        _url = reverse_lazy('admin:{}_{}_changelist'.format(_app_name, _model_name))
        _href = "<a href='{0}{1}/change/'>{1}</a>".format(_url, _id)
        return _href

    def __str__(self):
        return "{}".format(self.genre_name)

    class Meta:
        verbose_name = _("Genre")


class Entertainment(models.Model):
    title = models.CharField(max_length=350, help_text=_("title parsed from raw data"))
    name = models.CharField(max_length=350, null=True, blank=True, help_text=_("name from tmdb API"))
    tmdb_id = models.CharField(max_length=200, blank=True, null=True)
    trailer_id = models.CharField(max_length=200, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def get_reference_id(self):
        _id = self.id
        _app_name = os.path.basename(os.path.dirname(__file__))
        _model_name = self.__class__.__name__.lower()
        _url = reverse_lazy('admin:{}_{}_changelist'.format(_app_name, _model_name))
        _href = "<a href='{0}{1}/change/'>{1}</a>".format(_url, _id)
        return _href

    def __str__(self):
        _name = self.name if self.name else self.title
        return "{}- {}".format(self.id, _name)

    class Meta:
        abstract = True
        unique_together = ('title',)


class Others(Entertainment):
    category = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Other Videos"


class Movie(Entertainment):
    person = models.ManyToManyField(Person, through="PersonRole")
    overview = models.TextField(null=True, blank=True)
    genre_name = models.ManyToManyField(Genres)
    release_date = models.DateField(null=True, blank=True)
    thumbnail_hq = models.URLField(max_length=1000, null=True, blank=True)
    thumbnail_lq = models.URLField(max_length=1000, null=True, blank=True)
    fanart_hq = models.URLField(max_length=1000, null=True, blank=True)
    fanart_lq = models.URLField(max_length=1000, null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)
    status = models.BooleanField(default=False, verbose_name=_("Meta Data fetched?"),
                                 help_text=_("Mark if all the require possible metadata is fetched"))
    scan_stat = models.BooleanField(default=False, verbose_name=_("Scanned?"),
                                    help_text=_("Mark if scanned with tmdb API"))

    @property
    def get_streams(self):
        result = MediaInfo.objects.filter(meta_movie=self)
        stream_info = [{"media_id"  : i.id,
                        "quality"   : i.get_quality,
                        "name"      : self.name,
                        "resolution": i.get_resolution,
                        "duration"  : i.get_duration,
                        "runtime"   : i.runtime}
                       for i in result]
        if not stream_info:
            self.delete()
        else:
            return stream_info

    @property
    def get_short_overview(self):
        return self.overview[:15] if self.overview else self.overview

    @property
    def get_details(self):
        detail_set = {
            "id"           : self.id,
            "name"         : self.name,
            "overview"     : self.overview,
            "release_date" : self.release_date,
            "poster_path"  : self.thumbnail_hq,
            "backdrop_path": self.fanart_hq
        }
        return detail_set

    def __str__(self):
        return "{}. {}".format(self.id, self.title[:40])

    class Meta:
        verbose_name = _("Movie")


class TVSeries(Entertainment):
    """ title, name, tmdb_id, trailer_id in base class """
    original_name = models.CharField(max_length=500, blank=True, null=True)
    first_air_date = models.DateField(blank=True, null=True)
    vote_average = models.FloatField(null=True, blank=True)
    genre_name = models.ManyToManyField(Genres)
    overview = models.TextField(null=True, blank=True)
    backdrop_path = models.URLField(max_length=1000, null=True, blank=True)
    poster_path = models.URLField(max_length=1000, null=True, blank=True)
    origin_country = models.CharField(max_length=200, null=True, blank=True)
    original_language = models.CharField(max_length=20, null=True, blank=True)
    season_status = models.CharField(max_length=50, null=True, blank=True)
    status = models.BooleanField(default=False, verbose_name=_("Meta Data fetched?"),
                                 help_text=_("Mark if all the require possible metadata is fetched"))
    scan_stat = models.BooleanField(default=False, verbose_name=_("Scanned?"),
                                    help_text=_("Mark if scanned with tmdb API"))

    @property
    def get_name(self):
        return self.name if self.name else self.title

    @property
    def get_short_overview(self):
        return self.overview[:15] if self.overview else self.overview

    def __str__(self):
        _name = self.name if self.name else self.title
        return "{}- {}".format(self.id, _name)

    class Meta:
        verbose_name = _("TV Title")
        verbose_name_plural = _("TV Title")


class SeasonDetail(Entertainment):
    series = models.ForeignKey(TVSeries, on_delete=models.CASCADE)
    tmdb_id = models.CharField(max_length=50, blank=True, null=True)
    air_date = models.DateField(blank=True, null=True)
    season_number = models.IntegerField(null=True, blank=True)
    backdrop_path = models.URLField(max_length=1000, null=True, blank=True)
    poster_path = models.URLField(max_length=1000, null=True, blank=True)

    @property
    def get_detail(self):
        return {"id"           : self.id,
                "backdrop_path": self.backdrop_path if self.backdrop_path else self.series.backdrop_path,
                "poster_path"  : self.poster_path if self.poster_path else self.series.poster_path,
                "name"         : "Season {}".format(self.season_number),
                "season_number": self.season_number}

    def __str__(self):
        return "{} Season {}".format(self.series.get_name, self.season_number)

    class Meta:
        verbose_name = _("TV Season")
        verbose_name_plural = _("TV Season")


class EpisodeDetail(Entertainment):
    # related_season = models.ForeignKey(SeasonDetail)
    season = models.ForeignKey(SeasonDetail, on_delete=models.CASCADE, related_name="seasons")
    air_date = models.DateField(blank=True, null=True)
    person = models.ManyToManyField(Person, through="PersonRole")
    overview = models.TextField(null=True, blank=True)
    episode_title = models.CharField(max_length=350, null=True, blank=True)
    episode_number = models.IntegerField(null=True, blank=True)
    still_path = models.URLField(max_length=1000, null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)
    meta_stat = models.BooleanField(default=False)
    scan_stat = models.BooleanField(default=False, verbose_name=_("Scanned?"),
                                    help_text=_("Mark if scanned with tmdb API"))

    @property
    def get_full_name(self):
        _episode = "Episode {}".format(self.episode_number)
        _season = "Season {}".format(self.season.season_number)
        _season_title = self.season.series.title
        return "{} {} {}".format(_season_title, _season, _episode)

    @property
    def get_short_overview(self):
        return self.overview[:15] if self.overview else self.overview

    @property
    def get_director(self):
        result = Person.objects.filter(personrole__role__iexact='director',
                                       episodedetail=self)
        return [i.name for i in result]

    @property
    def get_actor(self):
        result = Person.objects.filter(personrole__role__iexact='cast',
                                       episodedetail=self)
        return [i.name for i in result]

    @property
    def get_writer(self):
        result = Person.objects.filter(personrole__role__iexact='writer', episodedetail=self)
        return [i.name for i in result]

    @property
    def get_episode_name(self):
        return self.episode_title if self.episode_title else "Episode {}".format(self.episode_number)

    @property
    def get_name(self):
        return self.episode_title if self.episode_title else "Episode {}".format(self.episode_number)

    @property
    def get_streams(self):
        result = MediaInfo.objects.filter(meta_episode=self)
        return [{"media_id"  : i.id,
                 "quality"   : i.get_quality,
                 "name"      : self.get_episode_name,
                 "resolution": i.get_resolution,
                 "duration"  : i.get_duration,
                 "runtime"   : i.runtime}
                for i in result]

    @property
    def get_backdrop_path(self):
        return self.season.backdrop_path if self.season.backdrop_path else self.season.series.backdrop_path

    @property
    def get_details(self):
        detail_set = {
            "id"            : self.id,
            "tmdb_id"       : self.tmdb_id,
            "name"          : self.get_name,
            "air_date"      : self.air_date,
            "release_date"  : self.air_date,
            "episode_number": self.episode_number,
            "vote_average"  : self.vote_average,
            "vote_count"    : self.vote_count,
            "backdrop_path" : self.get_backdrop_path,
            "poster_path"   : self.still_path if self.still_path else self.season.series.poster_path,
            "description"   : self.overview,
            "director"      : self.get_director,
            "actor"         : self.get_actor,
            "streams"       : self.get_streams
        }
        return detail_set

    def __str__(self):
        return "{}. {} - {}".format(self.id, self.title[:10], self.vote_average)

    class Meta:
        verbose_name = verbose_name_plural = _("TV Episodes")


class PersonRole(models.Model):
    role = models.CharField(max_length=200)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, blank=True, null=True)
    tv = models.ForeignKey(EpisodeDetail, on_delete=models.CASCADE, blank=True, null=True)
    character = models.CharField(null=True, blank=True, max_length=500)
    order = models.IntegerField(null=True, blank=True)
    cast_id = models.IntegerField(null=True, blank=True)
    tmdb_id = models.IntegerField(null=True, blank=True)

    def get_reference_id(self):
        _id = self.id
        _app_name = os.path.basename(os.path.dirname(__file__))
        _model_name = self.__class__.__name__.lower()
        _url = reverse_lazy('admin:{}_{}_changelist'.format(_app_name, _model_name))
        _href = "<a href='{0}{1}/change/'>{1}</a>".format(_url, _id)
        return _href

    def __str__(self):
        return "{} as ".format(self.person, self.character)


class MediaInfo(models.Model):
    file = models.ForeignKey(RawData, on_delete=models.CASCADE)
    meta_movie = models.ForeignKey(Movie, null=True, blank=True, on_delete=models.CASCADE,
                                   help_text=_("Related Movie of stream (if exist)"),
                                   related_name='movie_media_info')
    meta_episode = models.ForeignKey(EpisodeDetail, null=True, blank=True, on_delete=models.CASCADE,
                                     help_text=_("Related TV Episode of stream (if exist)"),
                                     related_name='episode_media_info')
    meta_other = models.ForeignKey(Others, null=True, blank=True, on_delete=models.CASCADE,
                                   help_text=_("all other contents"))
    frame_width = models.CharField(max_length=20, null=True, blank=True)
    frame_height = models.CharField(max_length=20, null=True, blank=True)
    video_codec = models.CharField(max_length=20, null=True, blank=True)
    audio_codec = models.CharField(max_length=20, null=True, blank=True)
    bit_rate = models.CharField(max_length=20, null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True,
                                  verbose_name=_("Run time in seconds"))

    @property
    def get_info_object(self):
        if self.meta_movie:
            return self.meta_movie.title
        elif self.meta_episode:
            return self.meta_episode.season.series.title
        elif self.meta_other:
            return self.meta_other.title
        else:
            return '—'

    def get_details(self):
        model_dict = model_to_dict(self)
        model_dict['file'] = model_to_dict(self.file) if model_dict.get('file', None) else self.file
        model_dict['meta_movie'] = model_to_dict(self.meta_movie) if model_dict.get('meta_movie', None) else self.meta_movie
        model_dict['meta_episode'] = model_to_dict(self.meta_episode) if model_dict.get('meta_episode', None) else self.meta_episode
        return model_dict

    @property
    def get_href(self):
        _id = self.id
        _app_name = os.path.basename(os.path.dirname(__file__))
        _model_name = self.__class__.__name__.lower()
        _url = reverse_lazy('admin:{}_{}_changelist'.format(_app_name, _model_name))
        _href = "{0}{1}/change/".format(_url, _id)
        return _href

    def get_reference_id(self):
        _href = self.get_href
        return "<a href='{}'>{}</a>".format(_href, self.id)

    @property
    def get_stream_url(self):
        file_path = os.path.join(self.file.path, self.file.name)
        # host = '/'.join(request.build_absolute_uri().split('/')[:3])
        try:
            from mysite.directory_settings import DOMAIN
            domain = DOMAIN
        except Exception as e:
            domain = "54.36.48.153:8000"
        if os.path.exists(MEDIA_MAP) and MEDIA_MAP in file_path:
            file_path = file_path.replace(MEDIA_MAP, '')
        else:
            file_path = file_path.replace(SCRAPE_DIR, '')
        file_path = urllib.parse.quote(file_path)
        stream_url = "http://{0}/media/{1}".format(domain, file_path)
        return stream_url

    def get_stream_link(self, link_name=None):
        if not link_name:
            link_name = self.file.name
        stream_url = self.get_stream_url
        # NOTE: stream URL configured to work only with apache hosted server
        return "<a href='{0}'>{1}</a>".format(stream_url, link_name)

    @property
    def has_movie(self):
        if self.meta_movie:
            return True
        else:
            return False

    @property
    def get_resolution(self):
        return "{}x{}".format(self.frame_width, self.frame_height)

    @property
    def get_duration(self):
        try:
            minutes, seconds = int(self.runtime) // 60, int(self.runtime) % 60
            hour, minutes = minutes // 60, minutes % 60
            return "{}:{}:{}".format(hour, minutes, seconds)
        except Exception as e:
            print(">>Exception in get_duration for : {}-{}\nreason:{}".format(self.id, self, e))
            return self.runtime

    @property
    def get_quality(self):
        # HD : if frame resolution greater then 896000(1280 * 700)
        try:
            quality = "HD" if int(self.frame_width) > 500 else "DVD"
            return "{}".format(quality)
        except Exception as e:
            print("EXCEPTION in get_quality for object: {}-{}\nreason:{}".format(self.id, self, e))
            # "{} x {}".format(self.frame_width, self.frame_height)
            return "DVD"

    def __str__(self):
        return "{} - {}x{} @ {}".format(self.file, self.frame_width, self.frame_height, self.bit_rate)

    class Meta:
        verbose_name = verbose_name_plural = _("Media Information")


class StreamAuthLog(models.Model):
    stream_key = models.TextField(blank=True, null=True)
    request_data = models.TextField(blank=True, null=True)
    response_status = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    sym_link_path = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.stream_key)


class MainMenuConstructor(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name in Regional Language(French)"))
    name_en = models.CharField(max_length=50, verbose_name=_("Name in English (en_US)"))
    poster_path = models.URLField(max_length=1000, verbose_name="Thumbnail",
                                  help_text=_("Enter image URL of resolution width 300"),
                                  blank=True, null=True)
    backdrop_path = models.URLField(max_length=1000, verbose_name="Fan Art",
                                    help_text=_("Enter image URL of resolution width 780"),
                                    blank=True, null=True)
    addon_id = models.CharField(max_length=100, blank=True, null=True)
    addon_cmd = models.TextField(blank=True, null=True,
                                 verbose_name=_("addon command to be execute"))
    priority = models.IntegerField(default=10, verbose_name=_("Order/Priority of item"),
                                   help_text=_("Determines in which order item should be displayed"))


class MainMenuContent(MainMenuConstructor):
    class Meta:
        verbose_name = _("Content of Main Menu")


class SubMenuContent(MainMenuConstructor):
    overview = models.TextField(blank=True, null=True, verbose_name=_("Description in regional language"))
    overview_en = models.TextField(blank=True, null=True, verbose_name=_("Description in English US"))

    class Meta:
        verbose_name = _("Sub Menu Content")


class ThreadManager(models.Model):
    THREAD_TYPE = (
        (0, "Raw Data"),
        (1, "Filtering Raw Data"),
        (2, "Fetch Movie Meta Data"),
        (3, "Fetch TV Meta Data"),
        (4, "Fetch Person Detail"),
        (5, "Structure Update")
    )
    THREAD_STATUS = (
        (0, "running"),
        (1, "stopped")
    )
    type = models.IntegerField(choices=THREAD_TYPE, verbose_name="Thread Type")
    status = models.IntegerField(choices=THREAD_STATUS, verbose_name="Thread Status")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_type_display()
