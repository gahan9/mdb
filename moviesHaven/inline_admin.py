from django.contrib import admin
from django.utils.html import format_html

from .models import *


class MediaInfoInline(admin.TabularInline):
    fields = ('id', 'get_playable_stream',
              'frame_width', 'frame_height', 'video_codec', 'audio_codec', 'runtime')
    readonly_fields = ('id', 'get_playable_stream', 'frame_width', 'frame_height', 'video_codec', 'audio_codec', 'runtime')
    model = MediaInfo
    extra = 0

    def has_add_permission(self, request):
        return False

    def get_playable_stream(self, obj):
        # file_path = os.path.join(obj.file.path, obj.file.name)
        # return file_path
        return format_html(obj.get_stream_link())


class SeasonDetailInline(admin.TabularInline):
    model = SeasonDetail
    fields = ['id', 'series', 'tmdb_id', 'air_date', 'season_number']
    readonly_fields = ['id', 'series', 'tmdb_id', 'air_date', 'season_number']


class EpisodeDetailInline(admin.TabularInline):
    model = EpisodeDetail
    fields = ['id', 'tmdb_id', 'season_name',
              'episode_title', 'episode_number', 'air_date',
              'still_path', 'meta_stat', 'scan_stat'
              ]
    readonly_fields = ['id', 'tmdb_id', 'season_name',
                       'episode_title', 'episode_number', 'air_date',
                       'still_path', 'meta_stat', 'scan_stat'
                       ]

    def season_name(self, obj):
        name = obj.season.series.name if obj.season.series.name else obj.season.series.title
        return "{}- {}".format(obj.season.series.id, name)


class PersonRoleInline(admin.TabularInline):
    list_display = ['id', 'character', 'role', 'person', 'movie', 'tv', 'tmdb_id', 'order']
    readonly_fields = ['id', 'role', 'person', 'movie', 'tv', 'tmdb_id', 'cast_id']
    model = PersonRole
    extra = 0

