from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Extra


class Limit(BaseModel):
    max_image_count: Optional[int]
    remaining_image_count: int


class UserLimits(BaseModel):
    user_limit: Optional[Limit]
    project_limit: Limit
    folder_limit: Limit


class UploadAnnotationAuthData(BaseModel):
    access_key: str
    secret_key: str
    session_token: str
    region: str
    bucket: str
    images: Dict[int, dict]

    class Config:
        extra = Extra.allow
        fields = {
            "access_key": "accessKeyId",
            "secret_key": "secretAccessKey",
            "session_token": "sessionToken",
            "region": "region",
        }

    def __init__(self, **data):
        credentials = data["creds"]
        data.update(credentials)
        del data["creds"]
        super().__init__(**data)


class DownloadMLModelAuthData(BaseModel):
    access_key: str
    secret_key: str
    session_token: str
    region: str
    bucket: str
    paths: List[str]

    class Config:
        extra = Extra.allow
        fields = {
            "access_key": "accessKeyId",
            "secret_key": "secretAccessKey",
            "session_token": "sessionToken",
            "region": "region",
        }

    def __init__(self, **data):
        credentials = data["tokens"]
        data.update(credentials)
        del data["tokens"]
        super().__init__(**data)


class UploadAnnotationsResponse(BaseModel):
    class Resource(BaseModel):
        classes: Optional[List[str]]
        templates: Optional[List[str]]
        attributes: Optional[List[str]]
        attribute_groups: Optional[List[str]]
    failedItems: List[str] = []
    missingResources: Optional[Resource]


class ServiceResponse(BaseModel):
    status: int
    reason: str
    content: Union[bytes, str]
    data: Any

    def __init__(self, response, content_type=None):
        data = {
            "status": response.status_code,
            "reason": response.reason,
            "content": response.content,
        }
        if response.ok:
            if content_type:
                data["data"] = content_type(**response.json())
            else:
                data["data"] = response.json()
        super().__init__(**data)

    @property
    def ok(self):
        return 199 < self.status < 300

    @property
    def error(self):
        return getattr(self.data, "error", "Unknown error.")
