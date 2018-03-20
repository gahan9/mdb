"""
Evan Joaness - E viva espana (français)_476b7.mp4
"""

from threading import Thread
import copy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django_tables2 import SingleTableMixin, SingleTableView

from moviesHaven.media_info import FetchMediaInfo
from moviesHaven.tables import MediaInfoTable
from .utils import *
from mysite.settings import TMDB_SEARCH_URL, DEFAULT_PARAMS, SCRAPE_DIR
from .models import *


def print_log(line, *args, debug=True):
    print(line)
    if debug:
        if args:
            print("additional info: ")
            for i in args:
                print(i)


class HomePageView(LoginRequiredMixin, TemplateView):
    """ Home page view """
    template_name = "index.html"
    success_url = reverse_lazy('index')
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        thread_instance = ThreadManager.objects.last()
        person_query = Person.objects.filter(personrole__role="cast").distinct()
        movie_query = Movie.objects.all()
        episode_query = EpisodeDetail.objects.all()
        context['thread'] = thread_instance if thread_instance else None
        # context['actors_scanned'] = person_query.filter(status__gte=1).count()
        # context['actors_with_metadata'] = person_query.filter(status__gte=2).count()
        context['total_actors'] = person_query.count()
        context['total_movies'] = movie_query.count()
        _movie_scan_stat = movie_query.filter(scan_stat=True)
        context['movies_scanned'] = _movie_scan_stat.count()
        context['movies_with_metadata'] = _movie_scan_stat.filter(status=True).count()
        context['total_episodes'] = episode_query.count()
        _tv_scan_stat = episode_query.filter(scan_stat=True)
        context['episodes_scanned'] = _tv_scan_stat.count()
        context['episodes_with_metadata'] = _tv_scan_stat.filter(meta_stat=True).count()
        context['total_raw_data'] = RawData.objects.count()
        context['total_raw_data_with_media_info'] = MediaInfo.objects.count()
        return context

    def get(self, request, *args, **kwargs):
        task = self.kwargs.get('task', None)
        # task = self.request.GET.get('task', None)
        if task:
            print_log("got task", task)
            if task == "update_person_data":
                meta_fetcher_obj = PopulateMetaData()
                person_thread = Thread(target=meta_fetcher_obj.update_person_data, name="person_thread")
                person_thread.start()
            if task == "update_content":
                sniffer_obj = DirSniffer()
                sniffer_obj.update_structure()
                # update_thread = Thread(target=sniffer_obj.update_structure, name="update_thread")
                # update_thread.start()
        return super(HomePageView, self).get(request, *args, **kwargs)


class APIDOCView(LoginRequiredMixin, TemplateView):
    """ Home page view """
    template_name = "api-doc.html"
    success_url = reverse_lazy('api_example')
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(APIDOCView, self).get_context_data(**kwargs)
        query = self.kwargs.get('q', None)
        context['regex'] = True if query else None
        return context


class MediaInfoView(AddFormMixin, SingleTableView):
    """ Home page view """
    model = MediaInfo
    template_name = "tabular_view.html"
    table_class = MediaInfoTable
    # table_pagination = {'per_page': 100}
    paginate_by = 150
    search_fields = ['file__name', 'meta_movie__name', 'meta_episode__name']
    queryset = model.objects.exclude(Q(meta_movie__status=True) | Q(meta_episode__scan_stat=True))

    def get_context_data(self, **kwargs):
        context = super(MediaInfoView, self).get_context_data(**kwargs)
        context['total_records'] = self.queryset.count()
        return context

    def get_form_fields(self):
        """
        Enables filter for fields mentioned in list search_fields
        :return: list of fields for search
        """
        return self.search_fields

    def get_queryset(self):
        print(self.queryset.count())
        if self.queryset is None:
            self.queryset = self.model.objects.filter(meta_movie__isnull=True , meta_episode__isnull=True)
        return super(MediaInfoView, self).get_queryset()


class DirSniffer(DataFilter):
    _lookup_dir = SCRAPE_DIR
    _sniffed_paths = RawData.objects.values_list('path', flat=True).distinct()

    def update_content(self, directory_path):
        print_log("updating content", directory_path)
        files_in_dir = os.listdir(directory_path)
        files_in_db = RawData.objects.filter(path=directory_path)
        files_set = []
        for file in files_in_db:
            if file.name not in files_in_dir:
                print_log("file name change detected", file.name)
                media_instance = MediaInfo.objects.get(file=file)
                if media_instance.meta_movie:
                    try:
                        Movie.objects.get(movie_media_info=media_instance).delete()
                    except Exception as e:
                        print_log("Exception in removing Movie object while updating directory: {}".format(directory_path), e)
                elif media_instance.meta_episode:
                    try:
                        EpisodeDetail.objects.get(episode_media_info=media_instance).delete()
                    except Exception as e:
                        print_log("Exception in removing EpisodeDetail object while updating directory: {}".format(directory_path), e)
                try:
                    media_instance.delete()
                except Exception as e:
                    print_log("Exception in removing media_instance object while updating directory: {}".format(directory_path), e)
                file.delete()
                print_log("file removed")
            else:
                try:
                    files_in_dir.pop(files_in_dir.index(file.name))
                except ValueError:
                    pass
        if files_in_dir:
            for item in files_in_dir:
                _extension = item.split('.')[-1]
                if _extension in SUPPORTED_EXTENSIONS:
                    _item_info = {"name": item.encode('utf-8').decode('utf-8', 'ignore'),
                                  "path": directory_path, "extension": _extension}
                    files_set.append(_item_info)
            if files_set:
                print_log("file set exist", files_set)
                self.content_creator(files_set)

    def update_structure(self, directory_path=None):
        directory_path = self._lookup_dir if not directory_path else directory_path
        thread_instance, thread_created = ThreadManager.objects.get_or_create(type=5, status=0)
        print_log("thread created: {}; created: {}".format(thread_instance, thread_created))
        if thread_created:
            for root, directory, files in os.walk(directory_path, topdown=True):
                if root in self._sniffed_paths:
                    _last_modified = self.get_path_state(root)
                    try:
                        path_instance = PathHash.objects.get(path=root)
                        if _last_modified != path_instance.path_last_modified:
                            self.update_content(directory_path=root)
                        path_instance.path_last_modified = _last_modified
                        path_instance.save()
                    except Exception as e:
                        path_instance = PathHash.objects.create(path=root, path_last_modified=_last_modified)
                        print_log("created path: {}".format(root))
            thread_instance.delete()
            print_log("deleted thread instance")
        else:
            return False

    @staticmethod
    def content_creator(contents):
        if contents:
            for video in contents:
                try:
                    raw_object, created = RawData.objects.get_or_create(**video)
                    print_log(raw_object, created)
                    media_info_obj = FetchMediaInfo()
                    try:
                        print_log("fetching media info")
                        media_data = media_info_obj.get_all_info(os.path.join(video["path"], video["name"]))
                        # THE BLACK HOLE HERE.....
                        print_log("found media_data for entry {}".format(video),
                                  raw_object.get_details(), media_data.get_details(), debug=True)
                        if media_data:
                            try:
                                media_info_instance = MediaInfo.objects.get_or_create(file=raw_object, **media_data)
                                print_log("media_info_instance instance for {} : {}".format(video, media_info_instance.get_details()),
                                          video, raw_object.get_details(), media_data, debug=True)
                            except Exception as e:
                                print_log(
                                    "Create query for media info failed for object: {} and media data: {}\n reason: {}".format(
                                        raw_object.get_details(), media_data, e))
                        else:
                            print_log("Media data couldn't found for: {}".format(raw_object.get_details()),
                                      video, media_data, debug=True)
                    except Exception as e:
                        print_log("Could not fetch media information for : {}".format(raw_object.get_details()))
                except Exception as e:
                    print_log("RawData objects could not created for: {}\nEXCEPTION==>reason:{} ".format(video, e))
        else:
            print_log("Structure Maker: Path Does not exist")

    def structure_maker(self):
        thread_instance, created = ThreadManager.objects.get_or_create(type=0, status=0)
        print_log("thread created: {}; created: {}".format(thread_instance, created))
        if created:
            contents = self.content_fetcher(directory_path=self._lookup_dir, db_paths=self._sniffed_paths)
            # self.content_creator(contents)
            content_creator = Thread(target=self.content_creator, args=(contents,))
            content_creator.start()
            thread_instance.delete()
            print_log("deleted thread instance")
        else:
            return False


class PopulateMetaData(object):
    def __init__(self, *args, **kwargs):
        self.tv_search_url = TMDB_SEARCH_URL + "tv/"
        self.default_params = DEFAULT_PARAMS

    def search_tv_data(self):
        print_log("fetching tv data...")
        thread_instance, created = ThreadManager.objects.get_or_create(type=1, status=0)
        if not created:
            return False
        for episode_instance in EpisodeDetail.objects.filter(meta_stat=False, scan_stat=False):
            tv_instance = episode_instance.season.series
            params = copy.deepcopy(DEFAULT_PARAMS)
            params.update({"query": tv_instance.title})
            tv_result = get_json_response(self.tv_search_url, params=params)
            episode_instance.scan_stat = True
            episode_instance.season.series.scan_stat = True
            episode_instance.save()
            results = tv_result.get('results', None)
            results0 = results[0] if results else None
            tv_instance.tmdb_id = results[0].get('id', None) if results else None
            genre_ids = results0.get('genre_ids', None) if results0 else None
            try:
                if genre_ids:
                    [tv_instance.genre_name.add(Genres.objects.get_or_create(genre_id=i)[0]) for i in genre_ids]
            except Exception as e:
                print_log("Genre adding exception : {}".format(e))
            tv_instance.scan_stat = True
            tv_instance.save()
            print_log("Instance_saved: {}".format(tv_instance))
            update_thread = Thread(target=self.update_tv_data, args=(episode_instance,))
            update_thread.start()
        thread_instance.delete()

    def update_tv_data(self, episode_instance=None):
        fetcher_object = MetaFetcher()
        if not episode_instance:
            return False
        season_instance = episode_instance.season
        tv_instance = season_instance.series
        fetcher = MetaFetcher()
        # TV DATA
        tv_detail = fetcher.get_tv_detail(tv_instance.tmdb_id)
        if tv_detail:
            for key, value in tv_detail.items():
                if value is not None:  # used is not None to allow 0 as valid value
                    setattr(tv_instance, key, value)
            tv_instance.status = True
            try:
                tv_instance.save()  # saved tv_data
            except Exception as e:
                print_log("Exception in saving tv instance id: {}\n tmdb id: {} \n title: {}".format(tv_instance.id,
                                                                                                 tv_instance.tmdb_id,
                                                                                                 tv_instance.title))
        # SEASON DATA
        season_detail = fetcher.get_season_detail(tv_instance.tmdb_id, season_instance.season_number)
        if season_detail:
            for key, value in season_detail.items():
                if value is not None:  # used is not None to allow 0 as valid value
                    setattr(season_instance, key, value)
            try:
                season_instance.save()  # saved season_detail
            except Exception as e:
                print_log("Exception in saving tv instance id: {}\n tmdb id: {} \n title: {}".format(season_instance.id,
                                                                                                 season_instance.tmdb_id,
                                                                                                 season_instance.title))
        episode_detail = fetcher.get_episode_detail(tv_instance.tmdb_id, season_instance.season_number,
                                                    episode_instance.episode_number)
        if episode_detail:
            for key, value in episode_detail.items():
                if value is not None:  # used is not None to allow 0 as valid value
                    setattr(episode_instance, key, value)
            episode_instance.meta_stat = True
            try:
                episode_instance.save()  # saved episode_detail
            except Exception as e:
                print_log("Exception in saving tv instance id: {}\n tmdb id: {} \n title: {}".format(episode_instance.id,
                                                                                                 episode_instance.tmdb_id,
                                                                                                 episode_instance.title))
            credits_url = fetcher.get_episode_credits_url(tv_id=tv_instance.tmdb_id,
                                                          season_number=season_instance.season_number,
                                                          episode_number=episode_instance.episode_number)
            casts, crews = fetcher_object.get_credits(episode_instance.tmdb_id, url=credits_url)
            if crews:
                for crew in crews:
                    crew_role = crew.pop('role')
                    crew_work = crew.pop('character')
                    try:
                        person_instance = Person.objects.get_or_create(**crew)[0]
                        PersonRole.objects.create(person=person_instance,
                                                  role=crew_role, character=crew_work,
                                                  tv=episode_instance)
                    except Exception as e:
                        print_log("Exception in creating person role: {}".format(e))
            if casts:
                for cast in casts:
                    cast_role = cast.pop('role')
                    cast_work = cast.pop('character')
                    try:
                        person_instance = Person.objects.get_or_create(**cast)[0]
                        PersonRole.objects.create(person=person_instance,
                                                  role=cast_role, character=cast_work,
                                                  tv=episode_instance)
                    except Exception as e:
                        print_log("Exception in creating person role: {}".format(e))

    def update_person_data(self):
        thread_instance, created = ThreadManager.objects.get_or_create(type=4, status=0)
        if created:
            fetcher = MetaFetcher()
            for person_instance in Person.objects.filter(status=0):
                try:
                    person_data = fetcher.get_person_detail(person_instance.tmdb_id)
                    person_instance.status = 1
                    person_instance.save()
                    # print_log(person_instance)
                    if person_data:
                        for key, value in person_data.items():
                            setattr(person_instance, key, value)
                        person_instance.status = 2
                        person_instance.save()
                except Exception as e:
                    print_log("Unable to fetch person data for {}\nreason:".format(person_instance, e))
            thread_instance.delete()
        else:
            return False


def filter_raw_data():
    thread_instance, created = ThreadManager.objects.get_or_create(type=1, status=0)
    if created:
        fetcher = DataFilter()
        for entry in MediaInfo.objects.filter(meta_movie__isnull=True, meta_episode__isnull=True):
            filter1 = fetcher.filter_film(entry.file.name)
            if filter1:
                if all(filter1):
                    try:
                        structure = fetcher.organize_tv_data(model_instance=entry.file)
                        if structure:
                            title = structure.get('title', None)
                            if title:
                                # XXX: need to check test case if two TV season with same name exist???
                                tv_instance = TVSeries.objects.get_or_create(title=title)[0]
                                season_number = structure.get('season_number', None)
                                if season_number:
                                    season_instance = \
                                    SeasonDetail.objects.get_or_create(series=tv_instance, season_number=season_number)[
                                        0]
                                    print_log("---------", season_number)
                                    episode_number = structure.get('episode_number', None)
                                    if episode_number:
                                        episode_instance = EpisodeDetail.objects.get_or_create(season=season_instance,
                                                                                               episode_number=episode_number)[
                                            0]
                                        entry.meta_episode = episode_instance
                                        entry.save()
                    except Exception as e:
                        print_log("filter_raw_data: Exception during creating TVSeries object: {}\nfor object- {}".format(e,
                                                                                                                      entry))
                        # raise Exception(e)
            else:
                title = fetcher.get_name(entry.file.name)
                # FIXME: handle name match with multiple occurrence of special character
                if '_' in title:
                    x = title.split('_')
                    title = x[1] if len(x) > 1 else title
                try:
                    if title:
                        movie_instance = Movie.objects.get_or_create(title=title)[0]
                        entry.meta_movie = movie_instance
                        entry.save()
                except Exception as e:
                    print_log("Exception during creating Movie object: {}".format(e))
        thread_instance.delete()
    else:
        return False


def genre_maker(genres):
    for genre in genres['genres']:
        genre_dict = {"genre_id"  : genre.get('id'),
                      "genre_name": genre.get('name'),
                      }
        try:
            Genres.objects.get_or_create(**genre_dict)
        except Exception as e:
            print_log(e)


def fetch_movie_metadata():
    print_log("fetching movie data...")
    thread_instance, created = ThreadManager.objects.get_or_create(type=2, status=0)
    if not created:
        return False
    fetcher = MetaFetcher()
    for movie_instance in Movie.objects.filter(status=False, scan_stat=False):
        try:
            params = copy.deepcopy(DEFAULT_PARAMS)
            params.update({"query": movie_instance.title})
            movie_result = get_json_response("{}movie/".format(TMDB_SEARCH_URL), params=params)
            movie_instance.scan_stat = True
            movie_instance.save()
            if movie_result:
                print_log(">>>Response of movie data... for {}".format(movie_instance.title))
                movies_data = movie_result.get('results', None)
                if movies_data:
                    movie = movies_data[0]
                    print_log(">>> Found movie data...")
                    # print_log(">>> {}".format(movies_data.get('id', None)))
                    genre_id = movie.get('genre_ids', None)
                    # for movie in movies_data:
                    if movie:
                        movie_instance.name = movie.get('title', None)
                        movie_instance.tmdb_id = movie.get('id', None)
                        movie_instance.overview = movie.get('overview', None)
                        movie_instance.release_date = movie.get('release_date', None)
                        movie_instance.vote_count = movie.get('vote_count', None)
                        movie_instance.vote_average = movie.get('vote_average', None)
                        try:
                            movie_instance.save()
                        except Exception as e:
                            print_log("Movie... saving meta data exception : {}".format(e))
                        # TODO: INCLUDE ME IN CLASS!!! GET TRAILER
                        if movie_instance.tmdb_id:
                            trailer_id = fetcher.get_movie_trailer(movie_instance.tmdb_id)
                            if trailer_id:
                                movie_instance.trailer_id = trailer_id
                            casts, crews = fetcher.get_credits(movie_instance.tmdb_id)
                            if casts:
                                for cast in casts:
                                    cast_role = cast.pop('role')
                                    cast_work = cast.pop('character')
                                    try:
                                        person_instance = Person.objects.get_or_create(**cast)[0]
                                        PersonRole.objects.create(person=person_instance,
                                                                  role=cast_role, character=cast_work,
                                                                  movie=movie_instance)
                                    except Exception as e:
                                        print_log(
                                            "Exception in creating person role: {}\n cast: {} \n cast_role:>> {} <<".format(
                                                e, cast, cast_role))
                            if crews:
                                for crew in crews:
                                    crew_role = crew.pop('role')
                                    crew_work = crew.pop('character')
                                    try:
                                        person_instance = Person.objects.get_or_create(**crew)[0]
                                        PersonRole.objects.create(person=person_instance,
                                                                  role=crew_role, character=crew_work,
                                                                  movie=movie_instance)
                                    except Exception as e:
                                        print_log(
                                            "Exception in creating person role: {}\n crew: {} \n crew_role:>> {} <<".format(
                                                e, crew, crew_role))
                        if genre_id:
                            [movie_instance.genre_name.add(Genres.objects.get(genre_id=i)) for i in genre_id]
                        try:
                            movie_instance.save()
                        except Exception as e:
                            print_log("Movie... saving meta data exception : {}".format(e))
                        image_set_thread = Thread(target=set_image, args=(movie_instance, movie))
                        image_set_thread.start()
                        movie_instance.status = True
                        movie_instance.save()
        except Exception as e:
            print_log("Exception in movie creation for object :  {}\n Exception: {}".format(movie_instance, e))
    thread_instance.delete()


def insert_raw_data(request):
    success_url = reverse_lazy('index')
    sniffer = DirSniffer()
    fetcher_thread = Thread(target=sniffer.structure_maker)
    fetcher_thread.start()
    return HttpResponseRedirect(success_url)


def file_filter(request):
    filter_thread = Thread(target=filter_raw_data)
    filter_thread.start()
    genres = get_genre("tv")
    genres.update(get_genre("movie"))
    genre_thread = Thread(target=genre_maker, args=(genres,))
    genre_thread.start()
    return HttpResponseRedirect(reverse_lazy('index'))


def update_meta_data(request):
    populate_obj = PopulateMetaData()
    movie_thread = Thread(target=fetch_movie_metadata)
    tv_thread = Thread(target=populate_obj.search_tv_data)
    tv_thread.start()
    movie_thread.start()
    # tv_thread_status = [t for t in tv_thread if t.is_alive()]
    # print_log(tv_thread_status)
    return HttpResponseRedirect(reverse_lazy('index'))
