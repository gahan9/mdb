from django.conf.urls import url
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.contrib.auth.views import login as django_login, logout as django_logout

from moviesHaven.forms import LoginForm
from . import views
from . import viewsets
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'rawdata', viewsets.RawDataViewSet, 'rawdata')
router.register(r'mediainfo', viewsets.MediaInfoViewSet, 'mediainfo')
router.register(r'movie', viewsets.MovieViewSet, 'movie')
router.register(r'tv', viewsets.TVSeriesViewSet, 'tvseries')
router.register(r'season', viewsets.SeasonDetailViewSet)
router.register(r'episode', viewsets.EpisodeDetailViewSet)
router.register(r'person', viewsets.PersonViewSet, 'person')
router.register(r'genre_movie', viewsets.MovieByGenreViewSet, 'genre_movie')
router.register(r'person_movie', viewsets.MovieByPersonViewSet, 'person_movie')
router.register(r'genre_tv', viewsets.TVSeriesByGenreViewSet, 'genre_tv')
# router.register(r'person_tv', viewsets.TVSeriesByPersonViewSet)
router.register(r'menu', viewsets.SubMenuStructureViewSet, 'submenu')

urlpatterns = [
    path('login/', django_login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
    path('logout/', django_logout, {'next_page': '/'}, name='logout'),
    path('', views.HomePageView.as_view(), name='index'),
    path('task/<slug:task>/', views.HomePageView.as_view(), name='task'),
    path('api/', include(router.urls), name='api_root'),
    path('insert_raw_data/', views.insert_raw_data, name='insert_raw_data'),
    path('file_filter/', views.file_filter, name='file_filter'),
    path('update_meta_data/', views.update_meta_data, name='update_meta_data'),
    path('display_data/', views.MediaInfoView.as_view(), name='display_data'),
    path('api/generate_stream/', viewsets.StreamGenerator.as_view(), name='generate_stream'),
    path('api/filter_set/', viewsets.DetailView.as_view(), name='filter_set'),
    path('api/get_count/', viewsets.GetCount.as_view(), name='get_count'),
    path('api_example/', views.APIDOCView.as_view(), name='api_example'),
    path('api_example/<slug:q>', views.APIDOCView.as_view(), name='api_example'),
    # path('genre/movie/<int:pk>', views.MovieByGenre.as_view(), name=''),
]
try:
    urlpatterns += [path('api/', include('drf_openapi.urls'))]
except Exception as e:
    print("URL IMPORT EXCEPTION: ", e)
    pass
