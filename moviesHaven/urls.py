from django.urls import path, include
from . import views, viewsets
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'movie', viewsets.MovieViewSet)
router.register(r'genre/movie', viewsets.MovieByGenreViewSet)
router.register(r'person/movie', viewsets.MovieByPersonViewSet)
# router.register(r'genre/tv', viewsets.TVSeriesByGenreViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('create_dir/', views.insert_raw_data, name='insert_raw_data'),
    path('show_data/', views.film_splitter, name='film_splitter'),
    path('api_out/', views.fetch_api_data, name='fetch_api_data'),
    # path('genre/movie/<int:pk>', views.MovieByGenre.as_view(), name=''),
]
