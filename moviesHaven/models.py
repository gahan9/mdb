from django.db import models
from django.utils.translation import ugettext_lazy as _


class RawData(models.Model):
    name = models.CharField(max_length=1500, blank=True, null=True)
    path = models.CharField(max_length=1500, blank=True, null=True)
    extension = models.CharField(blank=True, null=True, max_length=10)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = _("Raw Video Data in local")
        verbose_name_plural = _("Raw Video Data in local")
        unique_together = ('name', 'path')


class Person(models.Model):
    CHOICES = (
        (1, "Female"),
        (2, "Male"),
    )
    tmdb_id = models.CharField(max_length=50, blank=True, null=True)
    gender = models.IntegerField(blank=True, null=True)
    name = models.CharField(null=True, blank=True, max_length=100)
    character = models.CharField(null=True, blank=True, max_length=100)
    birthday = models.CharField(null=True, blank=True, max_length=100)
    profile_path = models.URLField(max_length=1000, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=200, null=True, blank=True)

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

    def __str__(self):
        return "{}".format(self.genre_name)

    class Meta:
        verbose_name = _("Genre")


class Entertainment(models.Model):
    title = models.CharField(max_length=350, help_text=_("title parsed from raw data"))
    name = models.CharField(max_length=350, null=True, blank=True, help_text=_("name from tmdb API"))
    tmdb_id = models.CharField(max_length=200, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name if self.name else self.title

    class Meta:
        abstract = True
        unique_together = ('title', )


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
        return "{}. {} - {}".format(self.id, self.title[:10], self.vote_average)

    class Meta:
        verbose_name = _("Movie")


class TVSeries(Entertainment):
    name = models.CharField(max_length=250)
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

    @property
    def get_short_overview(self):
        return self.overview[:15] if self.overview else self.overview

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("TV Series")
        verbose_name_plural = _("TV Series")


class SeasonDetail(Entertainment):
    series = models.ForeignKey(TVSeries, on_delete=models.CASCADE)
    tmdb_id = models.CharField(max_length=50, blank=True, null=True)
    air_date = models.DateField(blank=True, null=True)
    season_number = models.IntegerField(null=True, blank=True)
    backdrop_path = models.URLField(max_length=1000, null=True, blank=True)
    poster_path = models.URLField(max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = _("TV Season")
        verbose_name_plural = _("TV Season")


class EpisodeDetail(Entertainment):
    # related_season = models.ForeignKey(SeasonDetail)
    season = models.ForeignKey(SeasonDetail, on_delete=models.CASCADE)
    air_date = models.DateField(blank=True, null=True)
    person = models.ManyToManyField(Person, through="PersonRole")
    overview = models.TextField(null=True, blank=True)
    episode_title = models.CharField(max_length=350, null=True, blank=True)
    episode_number = models.IntegerField(null=True, blank=True)
    still_path = models.URLField(max_length=1000, null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)

    @property
    def get_short_overview(self):
        return self.overview[:15] if self.overview else self.overview

    @property
    def get_episode_name(self):
        return "{} Season {} episode {}".format(
            self.season.name, self.season.season_number, self.episode_number)

    @property
    def get_details(self):
        detail_set = {
            "id"            : self.id,
            "name"          : self.get_episode_name,
            "overview"      : self.overview,
            "release_date"  : self.release_date,
            "poster_path"   : self.thumbnail_lq,
            "backdrop_path" : self.fanart_hq,
            "season_number" : self.season_number,
            "episode_number": self.episode_number
        }
        return detail_set

    def __str__(self):
        return "{}. {} - {}".format(self.id, self.title[:10], self.vote_average)

    class Meta:
        verbose_name = verbose_name_plural = _("Episodes")


class PersonRole(models.Model):
    role = models.CharField(max_length=200)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, blank=True, null=True)
    tv = models.ForeignKey(EpisodeDetail, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "{} as {}".format(self.person, self.role)


class MediaInfo(models.Model):
    file = models.ForeignKey(RawData, on_delete=models.CASCADE)
    meta_movie = models.ForeignKey(Movie, null=True, blank=True, on_delete=models.SET_NULL)
    meta_episode = models.ForeignKey(EpisodeDetail, null=True, blank=True, on_delete=models.SET_NULL)
    frame_width = models.CharField(max_length=20, null=True, blank=True)
    frame_height = models.CharField(max_length=20, null=True, blank=True)
    video_codec = models.CharField(max_length=20, null=True, blank=True)
    audio_codec = models.CharField(max_length=20, null=True, blank=True)
    bit_rate = models.CharField(max_length=20, null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True,
                                  verbose_name=_("Run time in seconds"))

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
