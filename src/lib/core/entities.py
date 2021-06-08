from abc import ABC
from abc import abstractmethod
from io import BytesIO
from typing import Any


class BaseEntity(ABC):
    def __init__(self, uuid: Any = None):
        self._uuid = uuid

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value: Any):
        self._uuid = value

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError


class ConfigEntity(BaseEntity):
    def __init__(self, uuid: str, value: str):
        super().__init__(uuid)
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def to_dict(self):
        return {"key": self.uuid, "value": self.value}


class ProjectEntity(BaseEntity):
    def __init__(
        self,
        uuid: int = None,
        team_id: int = None,
        name: str = None,
        project_type: int = None,
        description: str = None,
        status: int = None,
        folder_id: int = None,
        upload_state: int = None,
    ):
        super().__init__(uuid)
        self.team_id = team_id
        self.name = name
        self.project_type = project_type
        self.description = description
        self.status = status
        self.folder_id = folder_id
        self.upload_state = upload_state

    def to_dict(self):
        return {
            "id": self.uuid,
            "team_id": self.team_id,
            "name": self.name,
            "type": self.project_type,
            "description": self.description,
            "status": self.status,
            "folder_id": self.folder_id,
            "upload_state": self.upload_state,
        }


class FolderEntity(BaseEntity):
    def __init__(
        self,
        uuid: int = None,
        parent_id: int = None,
        project_id: int = None,
        team_id: int = None,
        name: str = None,
    ):
        super().__init__(uuid)
        self.team_id = team_id
        self.name = name
        self.parent_id = parent_id
        self.project_id = project_id

    def to_dict(self):
        return {
            "id": self.uuid,
            "team_id": self.team_id,
            "name": self.name,
            "parent_id": self.parent_id,
            "project_id": self.project_id,
        }


class ImageEntity(BaseEntity):
    def __init__(
        self,
        uuid: int = None,
        name: str = None,
        path: str = None,
        project_id: int = None,
        team_id: int = None,
        annotation_status_code: int = None,
        folder_id: int = None,
        annotator_id: int = None,
        annotator_name: str = None,
    ):
        super().__init__(uuid)
        self.team_id = team_id
        self.name = name
        self.path = path
        self.project_id = project_id
        self.project_id = project_id
        self.annotation_status_code = annotation_status_code
        self.folder_id = folder_id
        self.annotator_id = annotator_id
        self.annotator_name = annotator_name

    def to_dict(self):
        return {
            "id": self.uuid,
            "team_id": self.team_id,
            "name": self.name,
            "path": self.path,
            "project_id": self.project_id,
            "annotation_status": self.annotation_status_code,
            "folder_id": self.folder_id,
            "annotator_id": self.annotator_id,
            "annotator_name": self.annotator_name,
        }


class ImageFileEntity(BaseEntity):
    def __init__(self, uuid, data: BytesIO, metadata: dict = None):
        super().__init__(uuid)
        self.data = data
        self.metadata = metadata

    def to_dict(self):
        return {"uuid": self.uuid, "bytes": self.data, "metadata": self.metadata}
