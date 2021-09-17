import os
from os.path import dirname

import src.superannotate as sa
from tests.integration.base import BaseTestCase


class TestVideoUrls(BaseTestCase):
    PROJECT_NAME = "test attach video urls"
    PATH_TO_URLS = "data_set/attach_urls.csv"
    PATH_TO_URLS_WITHOUT_NAMES = "data_set/attach_urls_with_no_name.csv"
    PROJECT_DESCRIPTION = "desc"
    PROJECT_TYPE = "Video"

    @property
    def csv_path(self):
        return os.path.join(dirname(dirname(__file__)), self.PATH_TO_URLS)

    @property
    def csv_path_without_name_column(self):
        return os.path.join(dirname(dirname(__file__)), self.PATH_TO_URLS)

    def test_attach_video_urls(self):
        uploaded, could_not_upload, existing_images = sa.attach_video_urls_to_project(
            self.PROJECT_NAME,
            self.csv_path,
        )
        self.assertEqual(len(uploaded), 8)
        self.assertEqual(len(could_not_upload), 1)
        self.assertEqual(len(existing_images), 1)

    def test_attach_video_urls_without_name_column(self):
        uploaded, could_not_upload, existing_images = sa.attach_video_urls_to_project(
            self.PROJECT_NAME,
            self.csv_path_without_name_column
        )
        self.assertEqual(len(uploaded), 8)
        self.assertEqual(len(could_not_upload), 1)
        self.assertEqual(len(existing_images), 1)
