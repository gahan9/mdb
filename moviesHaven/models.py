from django.db import models


class RawData(models.Model):
    name = models.TextField(blank=True, null=True)
    path = models.TextField(blank=True, null=True)
    extension = models.CharField(blank=True, null=True, max_length=10)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Raw Video Data in local"
        verbose_name_plural = "Raw Video Data in local"


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
        return self.biography[:15]


class Genres(models.Model):
    genre_id = models.IntegerField(unique=True)
    genre_name = models.CharField(max_length=256)

    def __str__(self):
        return "{}".format(self.genre_name)


class Entertainment(models.Model):
    local_data = models.ForeignKey(RawData, on_delete=models.CASCADE)
    title = models.CharField(max_length=350)
    overview = models.TextField()
    vote_average = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    status = models.BooleanField(default=False, verbose_name="Meta Data fetched?")

    def __str__(self):
        return "{}".format(self.title)

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
            "title"        : self.title,
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

    def __str__(self):
        return "{} - {}".format(self.title, self.vote_average)

    class Meta:
        verbose_name = verbose_name_plural = "TV Series"


class PersonRole(models.Model):
    role = models.CharField(max_length=200)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, blank=True, null=True)
    tv = models.ForeignKey(TVSeries, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "{} as {}".format(self.person, self.role)
