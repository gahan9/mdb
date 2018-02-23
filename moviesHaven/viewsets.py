import os

from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from moviesHaven.models import *
from moviesHaven.serializers import *
from rest_framework import viewsets


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    model = Movie

    def get_queryset(self):
        """
        filtering against a `name` query parameter in the URL. for movie title
        """
        queryset = self.model.objects.all()
        movie_name = self.request.query_params.get('name', None)
        print(movie_name)
        print(self.request.query_params)
        if movie_name is not None:
            queryset = queryset.filter(title__icontains=movie_name)
        return queryset


class MovieSearchView(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    model = Movie

    def get_queryset(self):
        """
        filtering against a `name` query parameter in the URL. for movie title
        """
        queryset = self.model.objects.all()
        movie_name = self.request.query_params.get('name', None)
        if movie_name is not None:
            queryset = queryset.filter(title__icontains=movie_name)
        return queryset


class MovieByGenreViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.filter(movie__genre_name__isnull=False).distinct()
    serializer_class = MovieByGenreSerializer

    def get_serializer_class(self):
        if not self.kwargs:
            return GenreSerializer
        else:
            return self.serializer_class


class TVSeriesByGenreViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.filter(tvseries__genre_name__isnull=False).distinct()
    serializer_class = TVSeriesByGenreSerializer

    def get_serializer_class(self):
        if not self.kwargs:
            return GenreSerializer
        else:
            return self.serializer_class


class MovieByPersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.filter(movie__personrole__person__isnull=False).distinct().order_by('name')
    serializer_class = MovieByPersonSerializer

    def get_serializer_class(self):
        if not self.kwargs:
            return PersonSerializer
        else:
            return self.serializer_class


class StreamGenerator(APIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def post(self, request):
        post_data = request.data
        if post_data.get('type', None):
            if post_data.get('type') == "movie":
                if post_data.get('id', None):
                    try:
                        movie = Movie.objects.get(id=post_data.get('id'))
                        file_path = os.path.join(movie.local_data.path, movie.local_data.name)
                        symlink_path = os.path.join(movie.local_data.path, ".cache")
                        if not os.path.exists(symlink_path):
                            os.mkdir(symlink_path)
                        s_path = os.path.join(symlink_path, movie.local_data.name)
                        print(s_path)
                        if not os.path.exists(s_path):
                            os.symlink(file_path, s_path)
                        #TODO: get server url and symlink dynamically
                        SERVER_URL = "http://192.168.5.47:8000/media/" + '/'.join(s_path.split('/')[5:])
                        return Response({'id': movie.id, 'title': movie.title, 'stream_link': SERVER_URL})
                    except Exception as e:
                        return Response({"detail": str(e)})
                else:
                    return Response({'detail': 'No or Invalid id in post data'})
            else:
                return Response({'detail': 'Invalid type in post data'})
        else:
            return Response({'detail': 'NO or Invalid post data'})
