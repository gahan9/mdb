from moviesHaven.models import *
from moviesHaven.serializers import *
from rest_framework import viewsets


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class MovieByGenreViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.filter(movie__genre_name__isnull=False).distinct()
    serializer_class = MovieByGenreSerializer

    def get_serializer_class(self):
        if not self.kwargs:
            return GenreSerializer
        else:
            return self.serializer_class


class TVSeriesByGenreViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = TVSeriesByGenreSerializer


class MovieByPersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.filter(movie__personrole__person__isnull=False).distinct()
    serializer_class = MovieByPersonSerializer
