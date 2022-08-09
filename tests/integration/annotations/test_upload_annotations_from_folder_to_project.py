import os
from pathlib import Path

from src.superannotate import SAClient
from tests.integration.base import BaseTestCase

sa = SAClient()


class TestAnnotationUploadVector(BaseTestCase):
    PROJECT_NAME = "Test-upload_annotations_from_folder_to_project"
    PROJECT_DESCRIPTION = "Desc"
    PROJECT_TYPE = "Vector"
    TEST_FOLDER_PATH = "data_set/sample_vector_annotations_with_tag_classes"
    TEST_BIG_FOLDER_PATH = "data_set/sample_big_json_vector"
    IMAGE_NAME = "example_image_1.jpg"

    @property
    def folder_path(self):
        return os.path.join(Path(__file__).parent.parent.parent, self.TEST_FOLDER_PATH)

    @property
    def big_annotations_folder_path(self):
        return os.path.join(Path(__file__).parent.parent.parent, self.TEST_BIG_FOLDER_PATH)
    
    def test_annotation_folder_upload_download(self):
        self._attach_items()
        sa.create_annotation_classes_from_classes_json(
            self.PROJECT_NAME, f"{self.folder_path}/classes/classes.json"
        )
        uploaded, _, _ = sa.upload_annotations_from_folder_to_project(
            self.PROJECT_NAME, self.folder_path
        )
        assert len(uploaded) == 1

        annotation = sa.get_annotations(self.PROJECT_NAME, ["example_image_1.jpg"])[0]

        assert annotation["instances"][-1]["type"] == "tag"
        assert annotation["instances"][-2]["type"] == "tag"
        # assert annotation["instances"][-1]["attributes"] == []
        # assert annotation["instances"][-2]["attributes"] == []

    def test_upload_big_annotations(self):
        sa.attach_items(
            self.PROJECT_NAME,
            [{"name": f"aearth_mov_00{i}.jpg", "url": f"url_{i}"} for i in range(1, 2)]  # noqa
        )
        sa.create_annotation_classes_from_classes_json(
            self.PROJECT_NAME, f"{self.big_annotations_folder_path}/classes/classes.json"
        )
        _, _, _ = sa.upload_annotations_from_folder_to_project(
            self.PROJECT_NAME, self.big_annotations_folder_path
        )
        annotations = sa.get_annotations(self.PROJECT_NAME)
        assert len(annotations) == 5