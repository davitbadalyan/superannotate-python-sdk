import os
from os.path import dirname
from pathlib import Path

import pytest

import src.superannotate as sa
from tests.integration.base import BaseTestCase


class TestDF(BaseTestCase):
    PROJECT_NAME = "test df processing"
    PROJECT_DESCRIPTION = "Desc"
    PROJECT_TYPE = "Vector"
    TEST_FOLDER_PATH = "data_set/sample_project_vector"

    @property
    def folder_path(self):
        return Path(
            Path(os.path.join(dirname(dirname(__file__)), self.TEST_FOLDER_PATH))
        )

    def test_filter_instances(self):
        df = sa.aggregate_annotations_as_df(self.folder_path, self.PROJECT_TYPE)
        df = df[~(df.duplicated(["instanceId", "imageName"]))]
        df = df[df.duplicated(["trackingId"], False) & df["trackingId"].notnull()]
        self.assertEqual(len(df), 2)
        self.assertEqual(
            {df.iloc[0]["imageName"], df.iloc[1]["imageName"]},
            {"example_image_1.jpg", "example_image_2.jpg"},
        )


class TestDFWithTagInstance(BaseTestCase):
    PROJECT_TYPE = "Vector"
    TEST_FOLDER_PATH = "data_set/sample_project_vector_with_tag"

    @property
    def folder_path(self):
        return Path(
            Path(os.path.join(dirname(dirname(__file__)), self.TEST_FOLDER_PATH))
        )

    def test_filter_instances(self):
        df = sa.aggregate_annotations_as_df(self.folder_path, self.PROJECT_TYPE)
        self.assertEqual(df.iloc[0]["type"], "tag")


class TestClassDistributionWithTagInstance(BaseTestCase):
    PROJECT_TYPE = "Vector"
    EXPORT_ROOT_PATH = "data_set"
    PROJECT_NAME = "sample_project_vector_with_tag"

    @property
    def root_path(self):
        return Path(
            Path(os.path.join(dirname(dirname(__file__)), self.EXPORT_ROOT_PATH))
        )

    @pytest.mark.skip(reason="Need to adjust")
    def test_filter_instances(self):
        df = sa.class_distribution(export_root=self.root_path, project_names=[self.PROJECT_NAME])
        self.assertEqual(df.iloc[0]['count'], 1)
        self.assertEqual(df.iloc[0]['className'], "Weather")
