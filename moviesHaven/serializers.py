import django_filters
from rest_framework import serializers

from .models import *


class MovieSerializer(serializers.ModelSerializer):
    genre_names = serializers.SerializerMethodField(required=False, read_only=True)
    description = serializers.SerializerMethodField(required=False, read_only=True)

    def get_genre_names(self, obj):
        print(obj.genre_name.all())
        if obj.genre_name:
            return [i.genre_name for i in obj.genre_name.all()]
        else:
            return []

    def get_description(self, obj):
        return obj.overview

    class Meta:
        model = Movie
        fields = ['id', 'url', 'title', 'genre_names', 'release_date', 'description',
                  'thumbnail_lq', 'status'
                  ]


class GenreFilterField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Movie):
            serializer = MovieSerializer(value, context=self.context)
        else:
            try:
                return value.serializable_value
            except Exception as e:
                print(e)
                raise Exception("Unexpected object: {}".format(value))
        return serializer.data


class MovieByGenreSerializer(serializers.ModelSerializer):
    movie_set = serializers.SerializerMethodField(read_only=True)

    def get_movie_set(self, obj):
        filtered_movie_set = Movie.objects.filter(genre_name__id=obj.id)
        if filtered_movie_set:
            return [i.get_details for i in filtered_movie_set]
        else:
            return []

    class Meta:
        model = Genres
        fields = ['id', 'url', 'genre_id', 'genre_name', 'movie_set']


class TVSeriesByGenreSerializer(serializers.ModelSerializer):
    tv_set = serializers.SerializerMethodField(read_only=True)

    def get_tv_set(self, obj):
        filtered_movie_set = TVSeries.objects.filter(genre_name__id=obj.id)
        if filtered_movie_set:
            return [i.get_details for i in filtered_movie_set]
        else:
            return []

    class Meta:
        model = Genres
        fields = "__all__"
