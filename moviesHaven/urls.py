from django.conf.urls import url
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.contrib.auth.views import login as django_login, logout as django_logout

from moviesHaven.forms import LoginForm
from . import views
from . import viewsets
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'movie', viewsets.MovieViewSet)
router.register(r'tv', viewsets.TVSeriesViewSet)
router.register(r'season', viewsets.SeasonDetailViewSet)
router.register(r'episode', viewsets.EpisodeDetailViewSet)
router.register(r'person', viewsets.PersonViewSet)
router.register(r'genre_movie', viewsets.MovieByGenreViewSet)
router.register(r'person_movie', viewsets.MovieByPersonViewSet)
router.register(r'genre_tv', viewsets.TVSeriesByGenreViewSet)
# router.register(r'person_tv', viewsets.TVSeriesByPersonViewSet)
router.register(r'menu', viewsets.SubMenuStructureViewSet)

urlpatterns = [
    path('login/', django_login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
    path('logout/', django_logout, {'next_page': '/'}, name='logout'),
    path('', views.HomePageView.as_view(), name='index'),
    path('<slug:task>', views.HomePageView.as_view(), name='index'),
    path('api/', include(router.urls)),
    # path('api/v1/', RedirectView.as_view(url='/api/')),
    path('insert_raw_data/', views.insert_raw_data, name='insert_raw_data'),
    path('file_filter/', views.file_filter, name='file_filter'),
    path('update_meta_data/', views.update_meta_data, name='update_meta_data'),
    path('api/generate_stream/', viewsets.StreamGenerator.as_view(), name='generate_stream'),
    path('api/filter_set/', viewsets.DetailView.as_view(), name='filter_set'),
    # path('genre/movie/<int:pk>', views.MovieByGenre.as_view(), name=''),
]
try:
    urlpatterns += [path('api/', include('drf_openapi.urls'))]
except Exception as e:
    print("URL IMPORT EXCEPTION: ", e)
    pass
