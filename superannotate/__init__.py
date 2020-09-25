import json
import logging
from pathlib import Path

import packaging.version
import requests

from .annotation_helpers import (
    add_annotation_bbox_to_json, add_annotation_cuboid_to_json,
    add_annotation_ellipse_to_json, add_annotation_point_to_json,
    add_annotation_polygon_to_json, add_annotation_polyline_to_json,
    add_annotation_template_to_json
)
from .api import API
from .common import (
    annotation_status_int_to_str, annotation_status_str_to_int,
    image_path_to_annotation_paths, project_type_int_to_str,
    project_type_str_to_int, user_role_str_to_int
)
from .db.annotation_classes import (
    create_annotation_class, create_annotation_classes_from_classes_json,
    delete_annotation_class, download_annotation_classes_json,
    get_annotation_class_metadata, search_annotation_classes
)
from .db.exports import (
    download_export, get_export_metadata, get_exports, prepare_export
)
from .db.images import (
    add_annotation_bbox_to_image, add_annotation_cuboid_to_image,
    add_annotation_ellipse_to_image, add_annotation_point_to_image,
    add_annotation_polygon_to_image, add_annotation_polyline_to_image,
    add_annotation_template_to_image, delete_image, download_image,
    download_image_annotations, download_image_preannotations,
    get_image_annotations, get_image_bytes, get_image_metadata,
    get_image_preannotations, search_images, set_image_annotation_status,
    upload_annotations_from_json_to_image
)
from .db.project import get_project_metadata, search_projects
from .db.project_images import copy_image, move_image, upload_image_to_project
from .db.projects import (
    create_project, create_project_like_project, delete_project,
    get_project_image_count, get_project_settings, get_project_workflow,
    rename_project, set_project_settings, set_project_workflow, share_project,
    unshare_project, upload_annotations_from_folder_to_project,
    upload_images_from_folder_to_project,
    upload_images_from_s3_bucket_to_project, upload_images_to_project,
    upload_preannotations_from_folder_to_project
)
from .db.teams import invite_contributor_to_team
from .db.users import search_team_contributors
from .exceptions import (
    SABaseException, SAExistingAnnotationClassNameException,
    SAExistingProjectNameException, SANonExistingAnnotationClassNameException,
    SANonExistingProjectNameException
)
from .input_converters.conversion import (
    convert_platform, export_annotation_format, import_annotation_format
)
from .version import Version

formatter = logging.Formatter(fmt='SA-PYTHON-SDK - %(levelname)s - %(message)s')
#formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("superannotate-python-sdk")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def _check_version():
    _req = requests.get('https://pypi.python.org/pypi/superannotate/json')
    if _req.ok:
        _Version = packaging.version.parse(Version)
        _version_on_pip = packaging.version.parse('0')
        _j = _req.json()
        _releases = _j.get('releases', [])
        for _release in _releases:
            _ver = packaging.version.parse(_release)
            if not _ver.is_prerelease:
                _version_on_pip = max(_version_on_pip, _ver)
        if _version_on_pip > _Version:
            logger.info(
                "There is newer version of SuperAnnotate Python SDK available on PyPI. Run 'pip install --upgrade superannotate' to upgrade from your version %s to %s.",
                _Version, _version_on_pip
            )


_api = API.get_instance()


def init(path_to_config_json):
    """Initializes and authenticates to SuperAnnotate platform using the config file.
    If not initialized then $HOME/.superannotate/config.json
    will be used.

    :param path_to_config_json: Location to config JSON file
    :type path_to_config_json: str or Path
    """
    _api.init(path_to_config_json)


_check_version()
init(None)
