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
