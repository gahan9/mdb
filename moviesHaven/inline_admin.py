from django.contrib import admin
from django.utils.html import format_html
from nested_inline.admin import NestedStackedInline, NestedModelAdmin

from .models import *


class MediaInfoInline(NestedStackedInline):
    fields = ['get_reference_id', 'get_playable_stream',
              'frame_width', 'frame_height', 'video_codec', 'audio_codec', 'runtime']
    readonly_fields = ['get_reference_id', 'get_playable_stream', 'frame_width', 'frame_height', 'video_codec', 'audio_codec', 'runtime']
    model = MediaInfo

    def get_reference_id(self, obj):
        return format_html(obj.get_reference_id())

    def has_add_permission(self, request):
        return False

    def get_playable_stream(self, obj):
        # file_path = os.path.join(obj.file.path, obj.file.name)
        # return file_path
        return format_html(obj.get_stream_link())


class EpisodeDetailInline(NestedStackedInline):
    model = EpisodeDetail
    inlines = [MediaInfoInline]
    fk_name = 'season'
    fields = ['get_reference_id', 'tmdb_id', 'season_name',
              'episode_title', 'episode_number', 'air_date',
              'still_path', 'meta_stat', 'scan_stat'
              ]
    readonly_fields = ['get_reference_id', 'tmdb_id', 'season_name',
                       'episode_title', 'episode_number', 'air_date',
                       'still_path', 'meta_stat', 'scan_stat'
                       ]

    def get_reference_id(self, obj):
        return format_html(obj.get_reference_id())

    def season_name(self, obj):
        name = obj.season.series.name if obj.season.series.name else obj.season.series.title
        return "{}- {}".format(obj.season.series.id, name)


class SeasonDetailInline(NestedStackedInline):
    model = SeasonDetail
    inlines = [EpisodeDetailInline]
    fields = ['get_reference_id', 'tmdb_id', 'air_date', 'season_number']
    readonly_fields = ['get_reference_id', 'tmdb_id', 'air_date', 'season_number']
    fk_name = 'series'

    def get_reference_id(self, obj):
        return format_html(obj.get_reference_id())


class PersonRoleInline(admin.TabularInline):
    list_display = ['get_reference_id', 'character', 'role', 'person', 'movie', 'tv', 'tmdb_id', 'order']
    readonly_fields = ['get_reference_id', 'role', 'person', 'movie', 'tv', 'tmdb_id', 'cast_id']
    model = PersonRole
    extra = 0

    def get_reference_id(self, obj):
        return format_html(obj.get_reference_id())
