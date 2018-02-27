from django.contrib import admin
from .models import *


class RawDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'path', 'extension']
    list_filter = ['extension', 'movie__status']
    search_fields = ['name', 'path']


class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_short_overview', 'vote_average', 'vote_count',
                    'duration', 'movie_genre', 'release_date', 'status',
                    'thumbnail_hq', 'thumbnail_lq', 'fanart_hq', 'fanart_lq']
    search_fields = ['name']

    def movie_genre(self, obj):
        return "\n".join([p.genre_name for p in obj.genre_name.all()])


class TVSeriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'season_number', 'episode_number', 'get_short_overview', 'thumbnail_hq',
                    'thumbnail_lq',
                    'fanart_hq', 'fanart_lq',
                    'tv_genre', 'duration', 'status',
                    'vote_average', 'vote_count', 'release_date']

    def tv_genre(self, obj):
        return "\n".join([p.genre_name for p in obj.genre_name.all()])


class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'genre_id', 'genre_name']


class PersonRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'person', 'movie', 'tv']


class PersonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'birthday', 'profile_path', 'get_short_biography', 'place_of_birth']


class StreamAuthLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'stream_key', 'sym_link_path', 'response_status', 'date_created', 'date_updated']


class MainMenuContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_en', 'poster_path', 'backdrop_path', 'addon_id', 'addon_cmd']


class SubMenuContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_en', 'overview', 'overview_en',
                    'poster_path', 'backdrop_path', 'addon_id', 'addon_cmd']


admin.site.register(RawData, RawDataAdmin)
# admin.site.register(Movie, MovieAdmin)
# admin.site.register(TVSeries, TVSeriesAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(PersonRole, PersonRoleAdmin)
admin.site.register(Genres, GenreAdmin)
admin.site.register(StreamAuthLog, StreamAuthLogAdmin)
# admin.site.register(MainMenuContent, MainMenuContentAdmin)
# admin.site.register(SubMenuContent, SubMenuContentAdmin)

admin.site.site_header = 'Planet Vision'
admin.site.site_title = 'Planet Vision'
admin.site.index_title = 'Planet Vision'
