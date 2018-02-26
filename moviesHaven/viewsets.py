"""
TASK TODO:
> Documentaries and genre....
    Genre
        search by genre
            - documentaries
            - animation
        year filter (search by year)
        order by name, year
> Classics

"""
import datetime
import os
import uuid

import requests
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from moviesHaven.models import *
from moviesHaven.serializers import *
from rest_framework import viewsets

from mysite.settings import STREAM_VALIDATOR_API, TEMP_FOLDER_NAME, SCRAPE_DIR


class MovieViewSet(viewsets.ModelViewSet):
    """
    list:
    Return List of all movies with meta data
    """
    queryset = Movie.objects.filter(status=True).order_by("name")
    serializer_class = MovieSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'release_date')
    model = Movie

    def get_queryset(self):
        queryset = self.model.objects.filter(status=True).order_by("name")
        movie_name = self.request.query_params.get('name', None)
        movie_year = self.request.query_params.get('release_date', None)
        classics = self.request.query_params.get('classics', None)
        genre = self.request.query_params.get('genre', None)
        # print(movie_name, movie_year, genre)
        if movie_name:
            queryset = queryset.filter(name__icontains=movie_name)
        if movie_year:
            try:
                queryset = queryset.filter(release_date__year=movie_year)
            except ValueError:
                return Response({"detail": "Invalid Year"})
        if classics:
            try:
                queryset = queryset.filter(release_date__range=(datetime.date(1900, 1, 1), datetime.date(1970, 1, 1)))
            except ValueError:
                return Response({"detail": "Invalid search parameter: {}".format(classics)})
        if genre:
            try:
                queryset = queryset.filter(genre_name__genre_name__iexact=genre).order_by("genre_name")
            except ValueError:
                return Response({"detail": "Invalid Genre"})
        return queryset


class TVSeriesViewSet(viewsets.ModelViewSet):
    queryset = TVSeries.objects.filter(status=True).order_by("name")
    serializer_class = TVSeriesSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'release_date')
    model = TVSeries

    def get_queryset(self):
        """
        filtering against a `name` query parameter in the URL. for tv name
        """
        queryset = self.model.objects.filter(status=True).order_by("name")
        tv_name = self.request.query_params.get('name', None)
        tv_year = self.request.query_params.get('release_date', None)
        if tv_name:
            queryset = queryset.filter(name__icontains=tv_name).order_by("-release_date")
        if tv_year:
            try:
                queryset = queryset.filter(release_date__year=tv_year).order_by("name")
            except ValueError:
                return Response({"detail": "Invalid Year"})
        return queryset


class MovieSearchView(ListAPIView):
    #TODO: Delete Me
    queryset = Movie.objects.filter(status=True)
    serializer_class = MovieSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'release_date')
    model = Movie

    def get_queryset(self):
        queryset = self.model.objects.filter(status=True)
        movie_name = self.request.query_params.get('name', None)
        movie_year = self.request.query_params.get('release_date', None)
        classics = self.request.query_params.get('classics', None)
        # print(movie_name, movie_year)
        if movie_name:
            queryset = queryset.filter(name__icontains=movie_name)
        if movie_year:
            try:
                queryset = queryset.filter(release_date__year=movie_year)
            except ValueError:
                return Response({"detail": "Invalid Year"})
        if classics:
            try:
                queryset = queryset.filter(release_date__range=(datetime.date(1900, 1, 1), datetime.date(1970, 1, 1)))
            except ValueError:
                return Response({"detail": "Invalid search parameter: {}".format(classics)})
        return queryset


class TVSeriesSearchView(ListAPIView):
    # TODO: Delete Me
    serializer_class = TVSeriesSerializer
    model = TVSeries
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'release_date')

    def get_queryset(self):
        """
        filtering against a `name` query parameter in the URL. for tv name
        """
        queryset = self.model.objects.filter(status=True)
        tv_name = self.request.query_params.get('name', None)
        tv_year = self.request.query_params.get('release_date', None)
        if tv_name:
            queryset = queryset.filter(name__icontains=tv_name).order_by("-release_date")
        if tv_year:
            try:
                queryset = queryset.filter(release_date__year=tv_year).order_by("name")
            except ValueError:
                return Response({"detail": "Invalid Year"})
        return queryset


class MovieByGenreViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.filter(movie__genre_name__isnull=False).distinct()
    serializer_class = MovieByGenreSerializer
    model = Genres
    filter_backends = (OrderingFilter,)
    ordering_fields = ('genre_name',)

    def get_queryset(self):
        """
        filtering against a `name` query parameter in the URL. for tv name
        """
        queryset = self.model.objects.filter(movie__genre_name__isnull=False).distinct()
        genre = self.request.query_params.get('genre', None)
        genre_year = self.request.query_params.get('year', None)
        print("genre_name: {}".format(genre))
        print("genre_year: {}".format(genre_year))
        if genre:
            try:
                queryset = queryset.filter(genre_name=genre).order_by("genre_name")
            except ValueError:
                return Response({"detail": "Invalid Genre"})
            if genre_year:
                try:
                    queryset = queryset.filter(release_date__year=genre_year).order_by("name")
                except ValueError:
                    return Response({"detail": "Invalid Year"})
        return queryset

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


class TVSeriesByPersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.filter(tvseries__personrole__person__isnull=False).distinct().order_by('name')
    serializer_class = TVSeriesByPersonSerializer

    def get_serializer_class(self):
        if not self.kwargs:
            return PersonSerializer
        else:
            return self.serializer_class


class StreamGenerator(APIView):
    model = Movie

    def post(self, request):
        post_data = request.data
        if post_data.get('type', None):
            if post_data.get('type') == "movie":
                self.model = Movie
            elif post_data.get('type') == "tv":
                self.model = TVSeries
            else:
                return Response({'detail': 'Invalid type in post data'})
            if post_data.get('id', None) and post_data.get('stream_key', None):
                stream_key = post_data.get('stream_key')
                response = requests.get(STREAM_VALIDATOR_API, params={'key': stream_key}, verify=False)
                log_entry = StreamAuthLog.objects.create(stream_key=stream_key, request_data=str(post_data))
                if response.status_code == 200:
                    log_entry.response_status = "ok"
                    try:
                        instance = self.model.objects.get(id=post_data.get('id'))
                        file_path = os.path.join(instance.local_data.path, instance.local_data.name)
                        symlink_path = os.path.join(SCRAPE_DIR, TEMP_FOLDER_NAME)
                        if not os.path.exists(symlink_path):
                            os.mkdir(symlink_path)
                        unique = "fu{}{}k".format(uuid.uuid1(), 'c')
                        s_path = os.path.join(symlink_path, unique)
                        # print(s_path.split(TEMP_FOLDER_NAME)[-1])
                        if not os.path.exists(s_path):
                            os.symlink(file_path, s_path)
                        host = '/'.join(request.build_absolute_uri().split('/')[:3])
                        # NOTE: stream URL configured to work only with apache hosted server
                        stream_url = "{0}/media/{1}/{2}".format(host, TEMP_FOLDER_NAME, unique)
                        log_entry.response_status = stream_url
                        return Response({'stream_link': stream_url})
                    except self.model.DoesNotExist:
                        return Response({"detail": "provided id does not exist"})
                else:
                    try:
                        log_entry.response_status = {"status": response.status_code, "content": response.json()}
                    except Exception as e:
                        log_entry.response_status = {"status": response.status_code}
                    return Response({'detail': "Invalid Stream Key"})
            else:
                return Response({'detail': 'Missing id or key'})
        else:
            return Response({'detail': 'NO or Invalid post data'})
