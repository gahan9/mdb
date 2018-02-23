from django.db import models


class RawData(models.Model):
    name = models.CharField(max_length=1500, blank=True, null=True)
    path = models.CharField(max_length=1500, blank=True, null=True)
    extension = models.CharField(blank=True, null=True, max_length=10)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Raw Video Data in local"
        verbose_name_plural = "Raw Video Data in local"
        unique_together = ('name', 'path')


class Person(models.Model):
    name = models.CharField(null=True, blank=True, max_length=100)
    birthday = models.CharField(null=True, blank=True, max_length=100)
    profile_path = models.URLField(max_length=1000, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    place_of_birth = models.CharField(null=True, blank=True, max_length=200)

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
    poster_path = models.URLField(max_length=1000, verbose_name="Thumbnail",
                                  help_text="Enter image URL of resolution width 300",
                                  blank=True, null=True)
    backdrop_path = models.URLField(max_length=1000, verbose_name="Fan Art",
                                    help_text="Enter image URL of resolution width 780",
                                    blank=True, null=True)

    def __str__(self):
        return "{}".format(self.genre_name)


class Entertainment(models.Model):
    local_data = models.ForeignKey(RawData, on_delete=models.CASCADE)
    name = models.CharField(max_length=350)
    overview = models.TextField()
    vote_average = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True, verbose_name="run time",
                                   help_text="Run time duration(in minutes)")
    status = models.BooleanField(default=False, verbose_name="Meta Data fetched?",
                                 help_text="Mark if all the require possible metadata is fetched")

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        abstract = True


class Movie(Entertainment):
    person = models.ManyToManyField(Person, through="PersonRole")
    genre_name = models.ManyToManyField(Genres)
    release_date = models.DateField(null=True, blank=True)
    thumbnail_hq = models.URLField(max_length=1000, null=True, blank=True)
    thumbnail_lq = models.URLField(max_length=1000, null=True, blank=True)
    fanart_hq = models.URLField(max_length=1000, null=True, blank=True)
    fanart_lq = models.URLField(max_length=1000, null=True, blank=True)

    @property
    def get_short_overview(self):
        return self.overview[:15]

    @property
    def get_details(self):
        detail_set = {
            "id"           : self.id,
            "name"         : self.name,
            "overview"     : self.overview,
            "release_date" : self.release_date,
            "poster_path"  : self.thumbnail_lq,
            "backdrop_path": self.fanart_hq
        }
        return detail_set


class TVSeries(Entertainment):
    person = models.ManyToManyField(Person, through="PersonRole")
    genre_name = models.ManyToManyField(Genres)
    episode_title = models.CharField(max_length=350, null=True, blank=True)
    season_number = models.IntegerField(null=True, blank=True)
    episode_number = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    thumbnail_hq = models.URLField(max_length=1000, null=True, blank=True)
    thumbnail_lq = models.URLField(max_length=1000, null=True, blank=True)
    fanart_hq = models.URLField(max_length=1000, null=True, blank=True)
    fanart_lq = models.URLField(max_length=1000, null=True, blank=True)

    @property
    def get_short_overview(self):
        return self.overview[:15]

    @property
    def get_details(self):
        detail_set = {
            "id"            : self.id,
            "name"          : self.name,
            "overview"      : self.overview,
            "release_date"  : self.release_date,
            "poster_path"   : self.thumbnail_lq,
            "backdrop_path" : self.fanart_hq,
            "season_number" : self.season_number,
            "episode_number": self.episode_number
        }
        return detail_set

    def __str__(self):
        return "{} - {}".format(self.name, self.vote_average)

    class Meta:
        verbose_name = verbose_name_plural = "TV Series"


class PersonRole(models.Model):
    role = models.CharField(max_length=200)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, blank=True, null=True)
    tv = models.ForeignKey(TVSeries, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "{} as {}".format(self.person, self.role)


class StreamAuthLog(models.Model):
    stream_key = models.TextField(blank=True, null=True)
    request_data = models.TextField(blank=True, null=True)
    response_status = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.stream_key)
