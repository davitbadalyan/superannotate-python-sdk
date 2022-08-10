import os
import tempfile
from pathlib import Path

import pytest

from src.superannotate import SAClient
from tests.integration.base import BaseTestCase


sa = SAClient()


class TestUploadVideoAnnotation(BaseTestCase):
    PROJECT_NAME = "video annotation upload"
    PATH_TO_URLS = "data_set/attach_video_for_annotation.csv"
    PROJECT_DESCRIPTION = "desc"
    PROJECT_TYPE = "Video"
    ANNOTATIONS_PATH = "data_set/video_annotation"
    ANNOTATIONS_WITHOUT_CLASSES_PATH = "data_set/annotations"
    CLASSES_PATH = "data_set/video_annotation/classes/classes.json"
    ANNOTATIONS_PATH_INVALID_JSON = "data_set/video_annotation_invalid_json"
    MINIMAL_ANNOTATION_PATH = "data_set/video_annotation_minimal_fields"
    MINIMAL_ANNOTATION_TRUTH_PATH = "data_set/minimal_video_annotation_truth"

    maxDiff = None

    @property
    def minimal_annotation_truth_path(self):
        return os.path.join(self.folder_path, self.MINIMAL_ANNOTATION_TRUTH_PATH)

    @property
    def folder_path(self):
        return Path(__file__).parent.parent.parent

    @property
    def csv_path(self):
        return os.path.join(self.folder_path, self.PATH_TO_URLS)

    @property
    def annotations_path(self):
        return os.path.join(self.folder_path, self.ANNOTATIONS_PATH)

    @property
    def minimal_annotations_path(self):
        return os.path.join(self.folder_path, self.MINIMAL_ANNOTATION_PATH)

    @property
    def annotations_without_classes(self):
        return os.path.join(self.folder_path, self.ANNOTATIONS_WITHOUT_CLASSES_PATH)

    @property
    def invalid_annotations_path(self):
        return os.path.join(self.folder_path, self.ANNOTATIONS_PATH_INVALID_JSON)

    @property
    def classes_path(self):
        return os.path.join(self.folder_path, self.CLASSES_PATH)

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def test_video_annotation_upload_invalid_json(self):
        sa.create_annotation_classes_from_classes_json(self.PROJECT_NAME, self.classes_path)

        _, _, _ = sa.attach_items(
            self.PROJECT_NAME,
            self.csv_path,
        )
        (uploaded_annotations, failed_annotations, missing_annotations) = sa.upload_annotations_from_folder_to_project(
            self.PROJECT_NAME, self.invalid_annotations_path)
        self.assertEqual(len(uploaded_annotations), 0)
        self.assertEqual(len(failed_annotations), 1)
        self.assertEqual(len(missing_annotations), 0)
        self.assertIn("Couldn't validate ", self._caplog.text)

    def test_upload_annotations_without_class_name(self):
        sa.create_annotation_classes_from_classes_json(self.PROJECT_NAME, self.classes_path)

        _, _, _ = sa.attach_items(
            self.PROJECT_NAME,
            self.csv_path,
        )
        sa.upload_annotations_from_folder_to_project(self.PROJECT_NAME, self.annotations_without_classes)

    def test_upload_annotations_empty_json(self):
        sa.create_annotation_classes_from_classes_json(self.PROJECT_NAME, self.classes_path)

        _, _, _ = sa.attach_items(
            self.PROJECT_NAME,
            self.csv_path,
        )
        export = sa.prepare_export(self.PROJECT_NAME)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = temp_dir
            sa.download_export(self.PROJECT_NAME, export, output_path, True)
            uploaded, _, _ = sa.upload_annotations_from_folder_to_project(self.PROJECT_NAME, output_path)
            self.assertEqual(len(uploaded), 1)
