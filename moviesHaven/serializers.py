from django.core.serializers import serialize
from rest_framework import serializers
from .models import *


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ['id', 'url', 'genre_id', 'genre_name']


class PersonSerializer(serializers.ModelSerializer):
    poster_path = serializers.SerializerMethodField(required=False, read_only=True)

    @staticmethod
    def get_poster_path(obj):
        return obj.profile_path

    class Meta:
        model = Person
        fields = ['id', 'url', 'name', 'birthday', 'profile_path', 'biography', 'place_of_birth', 'poster_path']


class MovieSerializer(serializers.ModelSerializer):
    genre_names = serializers.SerializerMethodField(required=False, read_only=True)
    description = serializers.SerializerMethodField(required=False, read_only=True)
    backdrop_path = serializers.SerializerMethodField(required=False, read_only=True)
    poster_path = serializers.SerializerMethodField(required=False, read_only=True)

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
                  'thumbnail_lq', 'status',
                  'backdrop_path', 'poster_path'
                  ]


class TVSeriesSerializer(serializers.ModelSerializer):
    genre_names = serializers.SerializerMethodField(required=False, read_only=True)
    description = serializers.SerializerMethodField(required=False, read_only=True)
    backdrop_path = serializers.SerializerMethodField(required=False, read_only=True)
    poster_path = serializers.SerializerMethodField(required=False, read_only=True)
    name = serializers.SerializerMethodField(required=False, read_only=True)

    def get_genre_names(self, obj):
        if obj.genre_name:
            return [i.genre_name for i in obj.genre_name.all()]
        else:
            return []

    def get_name(self, obj):
        return "{} Season {} episode {}".format(obj.name, obj.season_number, obj.episode_number)

    def get_description(self, obj):
        return obj.overview

    @staticmethod
    def get_poster_path(obj):
        return obj.thumbnail_hq

    @staticmethod
    def get_backdrop_path(obj):
        return obj.fanart_hq

    class Meta:
        model = TVSeries
        fields = ['id', 'url', 'name', 'genre_names', 'release_date', 'description',
                  'season_number', 'episode_number',
                  'backdrop_path', 'poster_path'
                  ]


class MovieByGenreSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_results(obj):
        filtered_movie_set = Movie.objects.filter(genre_name__id=obj.id)
        if filtered_movie_set:
            # res = serialize('json', filtered_movie_set)
            res = [i.get_details for i in filtered_movie_set]
            return res
        else:
            return []

    class Meta:
        model = Genres
        fields = ['id', 'url', 'genre_id', 'genre_name', 'results']


class TVSeriesByGenreSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField(read_only=True)

    def get_results(self, obj):
        filtered_movie_set = TVSeries.objects.filter(genre_name__id=obj.id)
        if filtered_movie_set:
            return [i.get_details for i in filtered_movie_set]
        else:
            return []

    class Meta:
        model = Genres
        fields = ['id', 'url', 'genre_id', 'genre_name', 'results']


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
        fields = ['id', 'url', 'name', 'birthday', 'profile_path', 'biography', 'place_of_birth', 'results', 'poster_path']


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
        fields = ['id', 'url', 'name', 'birthday', 'profile_path', 'biography', 'place_of_birth', 'results', 'poster_path']
