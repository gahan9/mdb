from django.contrib import admin
from .models import *


class RawDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'path', 'extension']
    list_filter = ['extension']
    search_fields = ['name', 'path']


class MediaInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'file', 'meta_movie', 'meta_episode', 'frame_width', 'frame_height',
                    'video_codec', 'audio_codec', 'runtime']

    def file_short(self, obj):
        return obj.file[:10] if obj.file else obj.file


class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'name', 'tmdb_id', 'vote_average', 'vote_count',
                    'movie_genre', 'release_date', 'status', 'get_short_overview',
                    # 'thumbnail_hq', 'thumbnail_lq', 'fanart_hq', 'fanart_lq'
                    ]
    list_filter = ['status']
    search_fields = ['name', 'title', 'tmdb_id', 'overview']

    def movie_genre(self, obj):
        return "\n".join([p.genre_name for p in obj.genre_name.all()])


class TVSeriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'name', 'tmdb_id',
                    'original_name', 'first_air_date', 'vote_average',
                    'origin_country', 'original_language', 'status', 'season_status',
                    'get_short_overview', 'backdrop_path', 'poster_path']
    search_fields = ['title', 'name', 'tmdb_id', 'overview']


class SeasonDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'series', 'tmdb_id', 'air_date', 'season_number']
    search_fields = ['season_number', 'series__name']


class EpisodeDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'tmdb_id', 'season_name',
                    'episode_title', 'episode_number', 'air_date', 'vote_average',
                    'get_short_overview', 'still_path'
                    ]
    search_fields = ['tmdb_id', 'episode_title', 'season__series__name']

    def season_name(self, obj):
        return obj.season.series.name


class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'genre_id', 'genre_name']


class PersonRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'person', 'movie', 'tv']
    list_filter = ['role']
    search_fields = ['person__name']


class PersonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'birthday', 'profile_path', 'get_short_biography', 'place_of_birth']
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
admin.site.register(Others)
# admin.site.register(MainMenuContent, MainMenuContentAdmin)
# admin.site.register(SubMenuContent, SubMenuContentAdmin)

admin.site.site_header = 'Planet Vision'
admin.site.site_title = 'Planet Vision'
admin.site.index_title = 'Planet Vision'
