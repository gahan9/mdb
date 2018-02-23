from django.urls import path, include
from django.views.generic import RedirectView

from . import views, viewsets
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'movie', viewsets.MovieViewSet)
router.register(r'genre/movie', viewsets.MovieByGenreViewSet)
router.register(r'person/movie', viewsets.MovieByPersonViewSet)
# router.register(r'genre/tv', viewsets.TVSeriesByGenreViewSet)

urlpatterns = [
    path('', views.HomePageView.as_view(), name='index'),
    path('api/', include(router.urls)),
    # path('api/v1/', RedirectView.as_view(url='/api/')),
    path('create_dir/', views.insert_raw_data, name='insert_raw_data'),
    path('show_data/', views.film_splitter, name='film_splitter'),
    path('api_out/', views.update_meta_data, name='fetch_api_data'),
    path('api/movie/(?P<name>.+)', viewsets.MovieSearchView.as_view(), name='search_movie'),
    path('api/generate_stream/', viewsets.StreamGenerator.as_view(), name='generate_stream'),
    # path('genre/movie/<int:pk>', views.MovieByGenre.as_view(), name=''),
]
