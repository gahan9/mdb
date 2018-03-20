import itertools
import django_tables2 as tables

from .models import *


class MediaInfoTable(tables.Table):
    # sr_no = tables.TemplateColumn("""{{total_records|add:'-1'}}""", verbose_name="Sr No")
    id = tables.TemplateColumn("""<a href="{{ record.get_href }}">{{ record.id }}</a>""")
    file = tables.TemplateColumn("""
                <a style="text-decoration:None" href="{{record.get_stream_url}}">
                    {{record.file.name}}
                </a>
            """)
    path = tables.TemplateColumn("""{{ record.file.path }}""")
    fetched_title = tables.TemplateColumn("""
                        {{ record.get_info_object }}
                    """, order_by=('meta_movie__title', 'meta_episode__title'))

    def __init__(self, *args, **kwargs):
        super(MediaInfoTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    class Meta:
        model = MediaInfo
        fields = ['id', 'file', 'path',
                  # 'frame_width', 'runtime'
                  ]
        attrs = {'class': 'table table-sm table-responsive'}
