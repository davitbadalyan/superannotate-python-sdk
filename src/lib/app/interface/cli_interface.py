import io
import logging
import os
from pathlib import Path

import src.lib.core as constances
from lib.app.helpers import split_project_path
from src.lib.app.interface.base_interface import BaseInterfaceFacade
from src.lib.core.conditions import Condition
from src.lib.core.conditions import CONDITION_EQ as EQ
from src.lib.core.entities import ConfigEntity
from src.lib.infrastructure.repositories import ConfigRepository

logger = logging.getLogger()


class CLIFacade(BaseInterfaceFacade):
    def init(self):
        repo = ConfigRepository()
        config = repo.get_one(uuid=constances.TOKEN_UUID)
        if config:
            if not input(
                f"File {config} exists. Do you want to overwrite? [y/n] : "
            ).lower() in ("y", "yes"):
                return
        token = input(
            "Input the team SDK token from https://app.superannotate.com/team : "
        )
        config_entity = ConfigEntity(uuid=constances.TOKEN_UUID, value=token)
        repo.insert(config_entity)
        if config:
            print("Configuration file successfully updated.")
        else:
            print("Configuration file successfully created.")

    def create_project(self, name: str, description: str, type: str) -> dict:
        p_type = constances.ProjectType[type.upper()].value
        response = self.controller.create_project(name, description, p_type)
        if response.errors:
            return response.errors
        return response.data

    def create_folder(self, project: str, folder: str) -> dict:
        response = self.controller.create_folder(project=project, folder_name=folder)
        if response.errors:
            return response.errors
        return response.data

    def upload_images(
        self,
        project: str,
        folder: str,
        extensions: str = constances.DEFAULT_IMAGE_EXTENSIONS,
        set_annotation_status: str = constances.AnnotationStatus.NOT_STARTED.value,
        exclude_file_patterns=constances.DEFAULT_FILE_EXCLUDE_PATTERNS,
        recursive_subfolders=False,
        image_quality_in_editor=None,
    ):
        paths = []
        for extension in extensions:
            if not recursive_subfolders:
                paths += list(Path(folder).glob(f"*.{extension.lower()}"))
                if os.name != "nt":
                    paths += list(Path(folder).glob(f"*.{extension.upper()}"))
            else:
                paths += list(Path(folder).rglob(f"*.{extension.lower()}"))
                if os.name != "nt":
                    paths += list(Path(folder).rglob(f"*.{extension.upper()}"))

        filtered_paths = []
        for path in paths:
            not_in_exclude_list = [
                x not in Path(path).name for x in exclude_file_patterns
            ]
            if all(not_in_exclude_list):
                filtered_paths.append(path)

        controller = self.controller
        project_list_condition = Condition("name", project, EQ) & Condition(
            "team_id", controller.team_id, EQ
        )
        projects = controller.projects.get_all(condition=project_list_condition)
        app_folder_name = None
        if projects:
            project = projects[0]
            if not app_folder_name:
                folder_id = project.folder_id
            else:
                folder_condition = (
                    Condition("project_id", project.uuid, EQ)
                    & Condition("team_id", controller.team_id, EQ)
                    & Condition("name", app_folder_name, EQ)
                )
                folder_id = controller.folders.get_one(folder_condition).uuid
            image_info_entities = []
            for image_path in filtered_paths:
                with open(image_path, "rb") as f:
                    file = io.BytesIO(f.read())

                response = self.controller.upload_image_to_s3(
                    project=project,
                    image_path=image_path,
                    image=file,
                    folder_id=folder_id,
                )
                image_info_entities.append(response.data)

            if image_info_entities:
                self.controller.upload_images(
                    project=project,
                    images=image_info_entities,
                    annotation_status=set_annotation_status,
                    image_quality=image_quality_in_editor,
                )

    def export_project(self, project, folder, include_fuse, annotation_statuses):
        project_name, folder_name = split_project_path(project)
        project = self.controller.search_project(project_name).data[0]
        folders = []
        if folder_name:
            folders = [folder_name]
        self.controller.prepare_export(
            project, folders, include_fuse, False, annotation_statuses
        )
