from django.core.serializers import serialize
from rest_framework import serializers

from moviesHaven.utils import CustomUtils
from .models import *


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ['id', 'genre_id', 'genre_name', 'backdrop_path', 'poster_path']


class PersonSerializer(serializers.ModelSerializer):
    poster_path = serializers.SerializerMethodField(required=False, read_only=True)

    @staticmethod
    def get_poster_path(obj):
        return obj.profile_path

    class Meta:
        model = Person
        fields = ['id', 'tmdb_id', 'url', 'name', 'birthday', 'biography', 'place_of_birth', 'poster_path']


class MovieSerializer(serializers.ModelSerializer):
    genre_names = serializers.SerializerMethodField(required=False, read_only=True)
    description = serializers.SerializerMethodField(required=False, read_only=True)
    backdrop_path = serializers.SerializerMethodField(required=False, read_only=True)
    poster_path = serializers.SerializerMethodField(required=False, read_only=True)
    director = serializers.SerializerMethodField(read_only=True, required=False)
    actor = serializers.SerializerMethodField(read_only=True, required=False)
    writer = serializers.SerializerMethodField(read_only=True, required=False)
    streams = serializers.SerializerMethodField(read_only=True, required=False)

    @staticmethod
    def get_streams(obj):
        result = MediaInfo.objects.filter(meta_movie__tmdb_id=obj.tmdb_id)
        return [{"media_id"  : i.id,
                 "quality"   : i.get_quality,
                 "name"      : obj.name,
                 "resolution": i.get_resolution,
                 "duration"  : i.get_duration,
                 "runtime"   : i.runtime}
                for i in result]

    def get_director(self, obj):
        result = Person.objects.filter(personrole__role__iexact='director', movie=obj)
        return [i.name for i in result]

    def get_actor(self, obj):
        result = Person.objects.filter(personrole__role__iexact='cast', movie=obj)
        return [i.name for i in result]

    def get_writer(self, obj):
        result = Person.objects.filter(personrole__role__iexact='writer', movie=obj)
        return [i.name for i in result]

    def get_genre_names(self, obj):
        # print(obj.genre_name.all())
        if obj.genre_name:
            return [i.genre_name for i in obj.genre_name.all()]
        else:
            return []

    def get_description(self, obj):
        return obj.overview

    @staticmethod
    def get_poster_path(obj):
        return obj.thumbnail_hq

    @staticmethod
    def get_backdrop_path(obj):
        return obj.fanart_hq

    class Meta:
        model = Movie
        fields = ['id', 'tmdb_id', 'url', 'name', 'genre_names', 'release_date', 'description',
                  'director', 'actor', 'writer', 'streams',
                  'thumbnail_lq', 'status', 'trailer_id',
                  'backdrop_path', 'poster_path'
                  ]


class TVSeriesSerializer(serializers.ModelSerializer):
    genre_names = serializers.SerializerMethodField(required=False, read_only=True)
    description = serializers.SerializerMethodField(required=False, read_only=True)
    seasons = serializers.SerializerMethodField(read_only=True, required=False)
    release_date = serializers.SerializerMethodField(read_only=True, required=False)

    def get_release_date(self, obj):
        return obj.first_air_date

    def get_genre_names(self, obj):
        if obj.genre_name:
            return [i.genre_name for i in obj.genre_name.all()]
        else:
            return []

    def get_seasons(self, obj):
        result = SeasonDetail.objects.filter(series__tmdb_id=obj.tmdb_id)
        _seasons = [i.get_detail for i in result]
        return CustomUtils().get_unique_result(_seasons, flag="season_number")

    # def get_name(self, obj):
    #     return "{} Season {} episode {}".format(obj.episode_title, obj.season_number, obj.episode_number)

    def get_description(self, obj):
        return obj.overview

    class Meta:
        model = TVSeries
        fields = ['id', 'tmdb_id', 'url', 'name', 'title',
                  'genre_names', 'first_air_date', 'description', 'seasons',
                  'backdrop_path', 'poster_path',
                  ]


class EpisodeDetailSerializer(serializers.ModelSerializer):
    director = serializers.SerializerMethodField(read_only=True, required=False)
    actor = serializers.SerializerMethodField(read_only=True, required=False)
    writer = serializers.SerializerMethodField(read_only=True, required=False)
    name = serializers.SerializerMethodField(read_only=True, required=False)

    def get_name(self, obj):
        return obj.episode_title

    def get_director(self, obj):
        result = Person.objects.filter(personrole__role__iexact='director',
                                       episodedetail=obj)
        return [i.name for i in result]

    def get_actor(self, obj):
        result = Person.objects.filter(personrole__role__iexact='cast',
                                       episodedetail=obj)
        return [i.name for i in result]

    def get_writer(self, obj):
        result = Person.objects.filter(personrole__role__iexact='writer', episodedetail=obj)
        return [i.name for i in result]

    class Meta:
        model = EpisodeDetail
        fields = ["id", 'tmdb_id', "url", 'name',
                  'director', 'actor', 'writer', 'trailer_id',
                  "episode_title"]


class SeasonDetailSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField(read_only=True, required=False)

    # seasons = EpisodeDetailSerializer(source="seasons")

    def get_results(self, obj):
        result = EpisodeDetail.objects.filter(season__tmdb_id=obj.tmdb_id)
        _episodes = [i.get_details for i in result]
        return CustomUtils().get_unique_result(_episodes, flag="episode_number")

    class Meta:
        model = SeasonDetail
        fields = ["id", 'tmdb_id', "url", "results", "seasons"]


class MovieByGenreSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_results(obj):
        filtered_movie_set = Movie.objects.filter(genre_name__id=obj.id)
        if filtered_movie_set:
            res = [i.get_details for i in filtered_movie_set]
            return res
        else:
            return []

    class Meta:
        model = Genres
        fields = ['id', 'genre_id', 'genre_name', 'results', 'backdrop_path', 'poster_path']


class TVSeriesByGenreSerializer(serializers.ModelSerializer):
    def get_results(self, obj):
        filtered_movie_set = TVSeries.objects.filter(genre_name__id=obj.id)
        if filtered_movie_set:
            return [i.get_details for i in filtered_movie_set]
        else:
            return []

    results = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = Genres
        fields = ['id', 'genre_id', 'genre_name', 'results']


class MovieByPersonSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField(read_only=True)
    poster_path = serializers.SerializerMethodField(required=False, read_only=True)

    @staticmethod
    def get_poster_path(obj):
        return obj.profile_path

    def get_results(self, obj):
        filtered_movie_set = Movie.objects.filter(personrole__person=obj)
        if filtered_movie_set:
            return [i.get_details for i in filtered_movie_set]
        else:
            return []

    class Meta:
        model = Person
        fields = ['id', 'name', 'birthday', 'profile_path', 'biography', 'place_of_birth', 'results', 'poster_path']


class TVSeriesByPersonSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField(read_only=True)
    poster_path = serializers.SerializerMethodField(required=False, read_only=True)

    @staticmethod
    def get_poster_path(obj):
        return obj.profile_path

    def get_results(self, obj):
        filtered_movie_set = TVSeries.objects.filter(personrole__person=obj)
        if filtered_movie_set:
            return [i.get_details for i in filtered_movie_set]
        else:
            return []

    class Meta:
        model = Person
        fields = ['id', 'name', 'birthday', 'profile_path', 'biography', 'place_of_birth', 'results', 'poster_path']


class SubMenuContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubMenuContent
        fields = ['id', 'name', 'name_en', 'overview', 'overview_en',
                  'poster_path', 'backdrop_path', 'addon_id', 'addon_cmd']
