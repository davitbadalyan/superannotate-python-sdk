import os
from pathlib import Path

from src.superannotate import SAClient
sa = SAClient()
from tests.integration.base import BaseTestCase


class TestMoveItems(BaseTestCase):
    PROJECT_NAME = "TestMoveItemsVector"
    PROJECT_DESCRIPTION = "TestCopyItemsVector"
    PROJECT_TYPE = "Vector"
    IMAGE_NAME = "test_image"
    FOLDER_1 = "folder_1"
    FOLDER_2 = "folder_2"
    CSV_PATH = "data_set/attach_urls.csv"

    @property
    def scv_path(self):
        return os.path.join(Path(__file__).parent.parent.parent, self.CSV_PATH)

    def test_move_items_from_root(self):
        uploaded, _, _ = sa.attach_items(self.PROJECT_NAME, self.scv_path)
        assert len(uploaded) == 7
        sa.create_folder(self.PROJECT_NAME, self.FOLDER_1)
        skipped_items = sa.move_items(self.PROJECT_NAME, f"{self.PROJECT_NAME}/{self.FOLDER_1}")
        assert len(skipped_items) == 0
        assert len(sa.search_items(f"{self.PROJECT_NAME}/{self.FOLDER_1}")) == 7

    def test_move_items_from_folder(self):
        sa.create_folder(self.PROJECT_NAME, self.FOLDER_1)
        sa.create_folder(self.PROJECT_NAME, self.FOLDER_2)
        uploaded, _, _ = sa.attach_items(f"{self.PROJECT_NAME}/{self.FOLDER_1}", self.scv_path)
        assert len(uploaded) == 7
        skipped_items = sa.move_items(f"{self.PROJECT_NAME}/{self.FOLDER_1}", f"{self.PROJECT_NAME}/{self.FOLDER_2}")
        assert len(skipped_items) == 0
        assert len(sa.search_items(f"{self.PROJECT_NAME}/{self.FOLDER_2}")) == 7
        assert len(sa.search_items(f"{self.PROJECT_NAME}/{self.FOLDER_1}")) == 0

