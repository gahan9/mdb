from django.test import TestCase

from .models import *
from .utils import *


class RawDataTests(TestCase):
    def test_fetch_raw_content(self):
        util_obj = DataFilter()
        contents = util_obj.content_fetcher(directory_path=SCRAPE_DIR)
        self.assertIs(contents, False)
