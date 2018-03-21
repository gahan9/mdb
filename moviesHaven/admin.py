from mysite.settings import SITE_NAME
from .inline_admin import *
from easy_select2 import select2_modelform
from django.utils.translation import ugettext_lazy as _

MediaInfoForm = select2_modelform(MediaInfo, attrs={'width': '450px'})


class PathHashAdmin(admin.ModelAdmin):
    list_display = ['id', 'path', 'path_last_modified', 'date_updated', 'date_created']
    search_fields = ['path']


class RawDataAdmin(NestedModelAdmin):
    list_display = ['id', 'name', 'path', 'extension']
    inlines = [MediaInfoInline]
    readonly_fields = ['id', 'name', 'path', 'extension']
    list_filter = ['extension']
    search_fields = ['name', 'path']


class MediaInfoAdmin(admin.ModelAdmin):
    form = MediaInfoForm
    fieldsets = (
        (None, {'fields': ('file', 'meta_movie', 'meta_episode')}),
        (_('Media info'), {'fields': ('frame_width', 'frame_height', 'video_codec', 'audio_codec',
                                      'runtime')}),
        (_('Stream'), {'fields': ('get_playable_stream',)})
    )
    list_display = ['id', 'get_playable_stream', 'meta_movie', 'meta_episode',
                    'frame_width', 'frame_height', 'video_codec', 'audio_codec', 'runtime'
                    ]
    readonly_fields = ['get_playable_stream', 'frame_width', 'frame_height',
                       'video_codec', 'audio_codec', 'runtime']
    # list_filter = ['meta_movie', 'meta_episode']
    search_fields = ['file__name',
                     'meta_episode__season__series__name',
                     'meta_movie__name', 'meta_episode__name', 'meta_movie__tmdb_id',
                     'meta_movie__title', 'meta_episode__title', 'meta_episode__tmdb_id']

    def get_playable_stream(self, obj):
        # file_path = os.path.join(obj.file.path, obj.file.name)
        # return file_path
        return format_html(obj.get_stream_link())

    def file_short(self, obj):
        return obj.file[:10] if obj.file else obj.file


class MovieAdmin(NestedModelAdmin):
    inlines = [MediaInfoInline]
    list_display = ['id', 'title', 'name', 'tmdb_id', 'vote_average', 'vote_count', 'trailer_id',
                    'movie_genre', 'release_date', 'get_short_overview', 'status', 'scan_stat',
                    # 'thumbnail_hq', 'thumbnail_lq', 'fanart_hq', 'fanart_lq'
                    ]
    list_filter = ['status', 'scan_stat']
    search_fields = ['name', 'title', 'tmdb_id', 'overview']

    def movie_genre(self, obj):
        return "\n".join([p.genre_name for p in obj.genre_name.all()])


class TVSeriesAdmin(NestedModelAdmin):
    inlines = [SeasonDetailInline]
    list_display = ['id', 'title', 'name', 'tmdb_id',
                    'original_name', 'first_air_date', 'vote_average',
                    'origin_country', 'original_language', 'status', 'season_status',
                    'get_short_overview', 'backdrop_path', 'poster_path']
    readonly_fields = ['title']
    list_filter = ['status']
    search_fields = ['title', 'name', 'tmdb_id', 'overview']


class SeasonDetailAdmin(admin.ModelAdmin):
    inlines = [EpisodeDetailInline]
    list_display = ['id', 'series', 'tmdb_id', 'air_date', 'season_number']
    search_fields = ['season_number']
    readonly_fields = ['title', 'date_created', 'date_updated']


class EpisodeDetailAdmin(admin.ModelAdmin):
    inlines = [MediaInfoInline]
    list_display = ['id', 'tmdb_id', 'season_name', 'season_number',
                    'episode_title', 'episode_number', 'air_date', 'vote_average',
                    'get_short_overview', 'still_path', 'meta_stat', 'scan_stat'
                    ]
    list_filter = ['meta_stat', 'scan_stat']
    search_fields = ['tmdb_id', 'episode_title', 'season__series__name']
    readonly_fields = ['title', 'date_created', 'date_updated']

    def season_name(self, obj):
        name = obj.season.series.name if obj.season.series.name else obj.season.series.title
        return "{}- {}".format(obj.season.series.id, name)

    def season_number(self, obj):
        return obj.season.season_number


class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'genre_id', 'genre_name', 'backdrop_path', 'poster_path']


class PersonRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'person', 'movie', 'tv']
    readonly_fields = ['id']
    list_filter = ['role']
    search_fields = ['person__name']


class PersonAdmin(admin.ModelAdmin):
    inlines = [PersonRoleInline]
    list_display = ['id', 'tmdb_id', 'name', 'birthday', 'profile_path', 'get_short_biography', 'place_of_birth']
    search_fields = ['name']


class StreamAuthLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'stream_key', 'sym_link_path', 'response_status', 'date_created', 'date_updated']


class MainMenuContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_en', 'poster_path', 'backdrop_path', 'addon_id', 'addon_cmd']
    search_fields = ['name', 'name_en', 'addon_id', 'addon_cmd']


class SubMenuContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_en', 'overview', 'overview_en',
                    'poster_path', 'backdrop_path', 'addon_id', 'addon_cmd']
    search_fields = ['name', 'name_en', 'addon_id', 'addon_cmd']


admin.site.register(RawData, RawDataAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(TVSeries, TVSeriesAdmin)
admin.site.register(SeasonDetail, SeasonDetailAdmin)
admin.site.register(EpisodeDetail, EpisodeDetailAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(PersonRole, PersonRoleAdmin)
admin.site.register(Genres, GenreAdmin)
admin.site.register(StreamAuthLog, StreamAuthLogAdmin)
admin.site.register(MediaInfo, MediaInfoAdmin)
admin.site.register(PathHash, PathHashAdmin)
admin.site.register(Others)
# admin.site.register(MainMenuContent, MainMenuContentAdmin)
# admin.site.register(SubMenuContent, SubMenuContentAdmin)

admin.site.site_header = SITE_NAME
admin.site.site_title = SITE_NAME
admin.site.index_title = SITE_NAME
