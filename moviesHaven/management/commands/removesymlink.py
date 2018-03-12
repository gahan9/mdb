import os

from django.utils import timezone
from django.core.management.base import BaseCommand

from moviesHaven.models import StreamAuthLog


class Command(BaseCommand):
    diff_hours = 4
    help = 'Removes the streams older then {} hours'.format(diff_hours)

    def add_arguments(self, parser):
        parser.add_argument('hours', nargs='?', type=int, default=self.diff_hours)

    def handle(self, *args, **options):
        arg = options.get('hours', None)
        if arg:
            self.diff_hours = arg
        time_diff = timezone.now() - timezone.timedelta(hours=self.diff_hours)
        stream_instances = StreamAuthLog.objects.filter(date_created__lt=time_diff)
        for stream in stream_instances:
            if stream.sym_link_path:
                try:
                    if os.path.exists(stream.sym_link_path):
                        os.remove(stream.sym_link_path)
                    stream.delete()
                except Exception as e:
                    print("STREAM DELETE FAILED: {} - {}\nreason: {}".format(stream.id, stream.sym_link_path, e))
            else:
                stream.delete()
