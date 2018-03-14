import datetime
import os
import uuid

import requests
from django.db.models import Q
from django.utils import timezone
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from moviesHaven.models import *
from moviesHaven.serializers import *
from rest_framework import viewsets

from mysite.directory_settings import MEDIA_MAP
from mysite.settings import STREAM_VALIDATOR_API, TEMP_FOLDER_NAME, SCRAPE_DIR


class DetailView(APIView):
    """
    :get
    type: tv/movie
    category: letter/year
    :list
    all the alphabets/year contained by tv/movie
    """
    model = Movie

    def get(self, request):
        content_type = self.request.query_params.get('type', 'movie')
        category = self.request.query_params.get('category', None)
        response = {}
        filter_for = 'release_date'
        # print(movie_name, movie_year)
        if content_type == "movie":
            self.model = Movie
        elif content_type == "tv":
            self.model = TVSeries
            filter_for = 'first_air_date'
        queryset = self.model.objects.filter(status=True)
        print(content_type, filter_for)
        if category == "year":
            try:
                year_list = [i.year for i in queryset.dates(filter_for, 'year', order='DESC')]
                response["results"] = year_list
            except ValueError:
                return Response({"detail": "Invalid search parameter"})
        elif category == "letter":
            try:
                pass
            except ValueError:
                return Response({"detail": "Invalid search parameter: {}"})
        return Response(response)


class MovieViewSet(viewsets.ModelViewSet):
    """
    list:
    Return List of all movies with meta data
    """
    queryset = Movie.objects.filter(status=True, release_date__lte=timezone.now()).distinct().order_by("name")
    serializer_class = MovieSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'release_date', 'vote_average', 'vote_count')
    model = Movie

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name', None)
        name_starts_with = self.request.query_params.get('name_starts_with', None)
        person_name = self.request.query_params.get('person_name', None)
        person_role = self.request.query_params.get('person_role', None)
        person_role = person_role if person_role else "cast"
        person_name_starts_with = self.request.query_params.get('person_name_starts_with', None)
        year = self.request.query_params.get('year', None)
        classics = self.request.query_params.get('classics', None)
        genre = self.request.query_params.get('genre', None)
        exclude = self.request.query_params.get('exclude', None)
        latest = self.request.query_params.get('latest', None)
        # print(movie_name, movie_year, genre)
        if exclude:
            for category in ['animation', 'documentaire', 'kids']:
                queryset = queryset.exclude(genre_name__genre_name__iexact=category)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if name_starts_with:
            if str(name_starts_with) == "0":
                queryset = queryset.filter(name__iregex=r'^[0-9](.*)').order_by('name')
            else:
                queryset = queryset.filter(name__istartswith=name_starts_with)
        if person_name:
            queryset = queryset.filter(personrole__role__iexact=person_role, person__name__icontains=person_name)
        if person_name_starts_with:
            queryset = queryset.filter(personrole__role__iexact=person_role, person__name__istartswith=person_name_starts_with)
        if latest:
            try:
                latest = int(latest)
            except Exception as e:
                latest = 3
            latest_condition = datetime.date.today() - datetime.timedelta(days=latest)
            temp_query = queryset.filter(date_updated__gte=latest_condition)
            if not temp_query:
                temp_query = queryset.order_by('-release_date')[:50]
            queryset = temp_query
        if year:
            try:
                queryset = queryset.filter(release_date__year=year)
            except ValueError:
                return Response({"detail": "Invalid Year"})
        if classics:
            try:
                queryset = queryset.filter(release_date__lte=datetime.date(1970, 1, 1))
            except ValueError:
                return Response({"detail": "Invalid search parameter: {}".format(classics)})
        if genre:
            try:
                if genre.lower() == "animation":
                    queryset = queryset.filter(Q(genre_name__genre_name__iexact='Kids') | Q(genre_name__genre_name__iexact=genre)).order_by("name")
                else:
                    queryset = queryset.filter(genre_name__genre_name__iexact=genre).order_by("name")
            except ValueError:
                return Response({"detail": "Invalid Genre"})
        # TODO: remove duplicates values of tmdb_id from queryset using extra() or distinct ON
        return queryset

    def get_serializer_class(self):
        if self.kwargs:
            return self.serializer_class
        else:
            return self.serializer_class


class TVSeriesViewSet(viewsets.ModelViewSet):
    queryset = TVSeries.objects.filter(status=True).order_by("name")
    serializer_class = TVSeriesSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'first_air_date', 'vote_average', 'vote_count')
    model = TVSeries

    def get_queryset(self):
        """
        filtering against a `name` query parameter in the URL. for tv name
        """
        queryset = self.model.objects.filter(status=True).order_by("name")
        name = self.request.query_params.get('name', None)
        name_starts_with = self.request.query_params.get('name_starts_with', None)
        year = self.request.query_params.get('year', None)
        latest = self.request.query_params.get('latest', None)
        classics = self.request.query_params.get('classics', None)
        genre = self.request.query_params.get('genre', None)
        person_name = self.request.query_params.get('person_name', None)
        person_role = self.request.query_params.get('person_role', None)
        person_role = person_role if person_role else "cast"
        person_name_starts_with = self.request.query_params.get('person_name_starts_with', None)
        # print(movie_name, movie_year, genre)
        if name:
            queryset = queryset.filter(name__icontains=name).order_by('name')
        if name_starts_with:
            if str(name_starts_with) == "0":
                queryset = queryset.filter(name__iregex=r'^[0-9](.*)').order_by('name')
            else:
                queryset = queryset.filter(name__istartswith=name_starts_with).order_by('name')
        if person_name:
            queryset = queryset.filter(personrole__role__iexact=person_role, person__name__icontains=person_name)
        if person_name_starts_with:
            queryset = queryset.filter(personrole__role__iexact=person_role, person__name__istartswith=person_name_starts_with)
        if latest:
            try:
                latest = int(latest)
            except Exception as e:
                latest = 3
            latest_condition = datetime.date.today() - datetime.timedelta(days=latest)
            # queryset = queryset.filter(date_updated__gte=latest_condition)
            temp_query = queryset.filter(date_updated__gte=latest_condition)
            if not temp_query:
                temp_query = queryset.order_by('-date_updated')[:50]
            queryset = temp_query
        if year:
            try:
                queryset = queryset.filter(first_air_date__year=year).order_by("name")
            except ValueError:
                return Response({"detail": "Invalid Year"})
        if classics:
            try:
                queryset = queryset.filter(first_air_date__range=(datetime.date(1700, 1, 1), datetime.date(1970, 1, 1)))
            except ValueError:
                return Response({"detail": "Invalid search parameter: {}".format(classics)})
        if genre:
            try:
                if genre.lower() == "animation":
                    queryset = queryset.filter(Q(genre_name__genre_name__iexact='Kids') | Q(genre_name__genre_name__iexact=genre)).order_by("name")
                else:
                    queryset = queryset.filter(genre_name__genre_name__iexact=genre).order_by("name")
            except ValueError:
                return Response({"detail": "Invalid Genre"})
        return queryset

    def get_serializer_class(self):
        if self.kwargs:
            return self.serializer_class
        else:
            return self.serializer_class


class MovieByGenreViewSet(viewsets.ModelViewSet):
    # TODO: combine movie -tv genre
    queryset = Genres.objects.filter(movie__genre_name__isnull=False).exclude(Q(genre_name='Kids') | Q(genre_name='Animation') | Q(genre_id=10770) | Q(genre_name='Documentaire') | Q(genre_name='Comédie')).distinct()
    serializer_class = MovieByGenreSerializer
    model = Genres
    filter_backends = (OrderingFilter,)
    ordering_fields = ('genre_name',)

    def get_queryset(self):
        """
        filtering against a `name` query parameter in the URL. for tv name
        """
        queryset = self.model.objects.filter(movie__genre_name__isnull=False).exclude(Q(genre_name='Kids') | Q(genre_name='Animation') | Q(genre_id=10770) | Q(genre_name='Documentaire') | Q(genre_name='Comédie')).distinct()
        genre = self.request.query_params.get('genre', None)
        genre_year = self.request.query_params.get('year', None)
        # print("genre_name: {}".format(genre))
        # print("genre_year: {}".format(genre_year))
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


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.filter(personrole__role__iexact="cast").distinct()
    serializer_class = PersonSerializer
    model = Person

    def get_queryset(self):
        content_type = self.request.query_params.get('type', None)
        queryset = self.model.objects.filter(personrole__role__iexact="cast").distinct()
        if content_type == "movie":
            queryset = queryset.filter(personrole__movie__isnull=False).distinct()
        elif content_type == "tv":
            queryset = queryset.filter(personrole__tv__isnull=False).distinct()
        else:
            return queryset
        name = self.request.query_params.get('name', None)
        name_starts_with = self.request.query_params.get('name_starts_with', None)
        # print(self.request.query_params)
        if name_starts_with:
            try:
                queryset = queryset.filter(name__istartswith=name_starts_with).order_by("name")
            except ValueError:
                return queryset
        if name:
            queryset = queryset.filter(name__icontains=name).order_by("name")
        return queryset


class MovieByPersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.filter(movie__personrole__person__isnull=False).distinct().order_by('name')
    serializer_class = MovieByPersonSerializer

    def get_serializer_class(self):
        if not self.kwargs:
            return PersonSerializer
        else:
            return self.serializer_class


# class TVSeriesByPersonViewSet(viewsets.ModelViewSet):
#     queryset = Person.objects.filter(episodedetail__personrole__person__isnull=False).distinct().order_by('name')
#     serializer_class = TVSeriesByPersonSerializer
#
#     def get_serializer_class(self):
#         if not self.kwargs:
#             return PersonSerializer
#         else:
#             return self.serializer_class


class StreamGenerator(APIView):
    model = MediaInfo

    def post(self, request):
        post_data = request.data
        media_id = post_data.get('id', None)
        stream_key = post_data.get('stream_key', None)
        if media_id and stream_key:
            response = requests.get(STREAM_VALIDATOR_API, params={'key': stream_key}, verify=False)
            log_entry = StreamAuthLog.objects.create(
                stream_key=stream_key,
                request_data=str(post_data))
            if response.status_code == 200:
                log_entry.response_status = "ok"
                try:
                    instance = self.model.objects.get(id=media_id)
                    file_path = os.path.join(instance.file.path, instance.file.name)
                    if os.path.exists(MEDIA_MAP):
                        symlink_path = os.path.join(MEDIA_MAP, TEMP_FOLDER_NAME)
                    else:
                        symlink_path = os.path.join(SCRAPE_DIR, TEMP_FOLDER_NAME)
                    # print(symlink_path, SCRAPE_DIR)
                    if not os.path.exists(symlink_path):
                        try:
                            os.mkdir(symlink_path)
                        except PermissionError:
                            return Response({"detail": "Unable to generate streaming link"})
                    unique = "{}{}".format(uuid.uuid1(), 'c')
                    s_path = os.path.join(symlink_path, unique)
                    # print(s_path.split(TEMP_FOLDER_NAME)[-1])
                    if not os.path.exists(s_path):
                        try:
                            os.symlink(file_path, s_path)
                        except PermissionError:
                            return Response({"detail": "Unable to generate streaming link"})
                    host = '/'.join(request.build_absolute_uri().split('/')[:3])
                    # NOTE: stream URL configured to work only with apache hosted server
                    stream_url = "{0}/media/{1}/{2}".format(host, TEMP_FOLDER_NAME, unique)
                    log_entry.response_status = stream_url
                    log_entry.sym_link_path = s_path
                    log_entry.save()
                    return Response({'stream_link': stream_url})
                except self.model.DoesNotExist:
                    err_msg = "provided id does not exist"
                    log_entry.response_status = err_msg
                    log_entry.save()
                    return Response({"detail": err_msg})
            else:
                try:
                    log_entry.response_status = {"status": response.status_code, "content": response.json()}
                    log_entry.save()
                except Exception as e:
                    log_entry.response_status = {"status": response.status_code}
                    log_entry.save()
                return Response({'detail': "Invalid Stream Key"})
        else:
            return Response({'detail': 'Missing id or key'})


class SubMenuStructureViewSet(viewsets.ModelViewSet):
    serializer_class = SubMenuContentSerializer
    queryset = SubMenuContent.objects.all().order_by("priority")
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'priority')
    model = TVSeries


class SeasonDetailViewSet(viewsets.ModelViewSet):
    serializer_class = SeasonDetailSerializer
    queryset = SeasonDetail.objects.all()
    filter_backends = (OrderingFilter,)
    ordering_fields = ('season_number',)
    model = SeasonDetail


class EpisodeDetailViewSet(viewsets.ModelViewSet):
    serializer_class = EpisodeDetailSerializer
    queryset = EpisodeDetail.objects.all()
    filter_backends = (OrderingFilter,)
    ordering_fields = ('episode_number', 'air_date')
    model = EpisodeDetail

    def get_queryset(self):
        queryset = self.model.objects.filter(meta_stat=True).order_by('-air_date')
        latest = self.request.query_params.get('latest', None)
        if latest:
            try:
                latest = int(latest)
            except Exception as e:
                latest = 3
            latest_condition = datetime.date.today() - datetime.timedelta(days=latest)
            # queryset = queryset.filter(date_updated__gte=latest_condition)
            queryset = queryset.filter(air_date__gte=latest_condition).order_by('-air_date')
        return queryset
