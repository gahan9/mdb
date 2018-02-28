from django.core.serializers import serialize
from rest_framework import serializers
from .models import *


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ['id', 'genre_id', 'genre_name']


class PersonSerializer(serializers.ModelSerializer):
    poster_path = serializers.SerializerMethodField(required=False, read_only=True)

    @staticmethod
    def get_poster_path(obj):
        return obj.profile_path

    class Meta:
        model = Person
        fields = ['id', 'url', 'name', 'birthday', 'biography', 'place_of_birth', 'poster_path']


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
        result = MediaInfo.objects.filter(meta_movie=obj)
        return [{"media_id"  : i.id,
                 "resolution": i.get_resolution,
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
        fields = ['id', 'url', 'name', 'genre_names', 'release_date', 'description',
                  'director', 'actor', 'writer', 'streams',
                  'thumbnail_lq', 'status', 'trailer_id',
                  'backdrop_path', 'poster_path'
                  ]


class TVSeriesSerializer(serializers.ModelSerializer):
    genre_names = serializers.SerializerMethodField(required=False, read_only=True)
    description = serializers.SerializerMethodField(required=False, read_only=True)
    seasons = serializers.SerializerMethodField(read_only=True, required=False)

    def get_genre_names(self, obj):
        if obj.genre_name:
            return [i.genre_name for i in obj.genre_name.all()]
        else:
            return []

    def get_seasons(self, obj):
        result = SeasonDetail.objects.filter(series=obj)
        return [{"id": i.id, "season_number": i.season_number} for i in result]

    # def get_name(self, obj):
    #     return "{} Season {} episode {}".format(obj.episode_title, obj.season_number, obj.episode_number)

    def get_description(self, obj):
        return obj.overview

    class Meta:
        model = TVSeries
        fields = ['id', 'url', 'name', 'title',
                  'genre_names', 'first_air_date', 'description', 'seasons',
                  'backdrop_path', 'poster_path',
                  ]


class SeasonDetailSerializer(serializers.ModelSerializer):
    episodes = serializers.SerializerMethodField(read_only=True, required=False)

    def get_episodes(self, obj):
        result = EpisodeDetail.objects.filter(season=obj)
        return [{"id": i.id, "episode_number": i.episode_number} for i in result]

    class Meta:
        model = SeasonDetail
        fields = ["id", "url", "episodes"]


class EpisodeDetailSerializer(serializers.ModelSerializer):
    director = serializers.SerializerMethodField(read_only=True, required=False)
    actor = serializers.SerializerMethodField(read_only=True, required=False)
    writer = serializers.SerializerMethodField(read_only=True, required=False)

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
        fields = ["id", "url", 'director', 'actor', 'writer', 'trailer_id',
                  "episode_title"]


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
        fields = ['id', 'genre_id', 'genre_name', 'results']


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


class MovieDetail(MovieSerializer):
    cast = serializers.SerializerMethodField(required=False, read_only=True)
    crew = serializers.SerializerMethodField(required=False, read_only=True)

    def get_cast(self, obj):
        result = ""
        return result

    def get_director(self, obj):
        result = Person.objects.filter(personrole__role__iexact='director', movie=obj)
        return [i.name for i in result]

    class Meta:
        model = Movie
        fields = ['id', 'url', 'name', 'genre_names', 'release_date', 'description',
                  'thumbnail_lq', 'status', 'cast',
                  'backdrop_path', 'poster_path'
                  ]
