from django.contrib import admin
from .models import *


class RawDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'path', 'extension']
    list_filter = ['extension']
    search_fields = ['name', 'path']


class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'get_short_overview', 'vote_average', 'vote_count',
                    'duration', 'movie_genre', 'release_date', 'status',
                    'thumbnail_hq', 'thumbnail_lq', 'fanart_hq', 'fanart_lq']
    search_fields = ['title']

    def movie_genre(self, obj):
        return "\n".join([p.genre_name for p in obj.genre_name.all()])


class TVSeriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'season_number', 'episode_number', 'get_short_overview', 'thumbnail_hq',
                    'thumbnail_lq',
                    'fanart_hq', 'fanart_lq',
                    'tv_genre', 'duration', 'status',
                    'vote_average', 'vote_count', 'release_date']

    def tv_genre(self, obj):
        return "\n".join([p.genre_name for p in obj.genre_name.all()])


class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'genre_id', 'genre_name']


class PersonRoleAdmin(admin.ModelAdmin):
    list_display = ['role', 'person', 'movie', 'tv']


class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'birthday', 'profile_path', 'get_short_biography', 'place_of_birth']


admin.site.register(Movie, MovieAdmin)
admin.site.register(TVSeries, TVSeriesAdmin)
admin.site.register(RawData, RawDataAdmin)
admin.site.register(PersonRole, PersonRoleAdmin)
admin.site.register(Genres, GenreAdmin)
admin.site.register(Person, PersonAdmin)

admin.site.site_header = 'Planet Vision'
