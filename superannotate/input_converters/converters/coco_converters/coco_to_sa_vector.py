import json

import cv2
import numpy as np

from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

import time

from .coco_api import (_maskfrRLE, decode)

from ..sa_json_helper import (_create_vector_instance, _create_empty_sa_json)

from ....common import id2rgb, write_to_json


def annot_to_polygon(annot):
    if isinstance(annot['counts'], list):
        bitmask = _maskfrRLE(annot)
    elif isinstance(annot['counts'], str):
        bitmask = decode(annot)

    contours, _ = cv2.findContours(
        bitmask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    segments = []
    for contour in contours:
        contour = contour.flatten().tolist()
        if len(contour) > 4:
            segments.append(contour)

    return segments


def save_sa_jsons(coco_json, img_id_to_annot, output_dir):
    for img in tqdm(coco_json['images'], "Writing annotations to disk"):
        # json_template = _create_empty_sa_json()
        if 'file_name' in img:
            image_path = Path(img['file_name']).name
        else:
            image_path = img['coco_url'].split('/')[-1]

        if str(img['id']) not in img_id_to_annot:
            sa_instances = []
        else:
            sa_instances = img_id_to_annot[str(img['id'])]
        file_name = "%s___objects.json" % image_path
        write_to_json(output_dir / file_name, sa_instances)

        # json_template['instance'] = sa_instances
        # json_template['metadata'] = {
        #     'name': image_path,
        #     'width': img['width'],
        #     'height': img['height']
        # }
        # write_to_json(output_dir / file_name, json_template)


def coco_instance_segmentation_to_sa_vector(coco_path, output_dir):
    coco_json = json.load(open(coco_path))
    cat_id_to_cat = {}
    for cat in coco_json['categories']:
        cat_id_to_cat[cat['id']] = cat

    instance_groups = {}
    for annot in coco_json['annotations']:
        if 'id' in annot:
            if annot['id'] in instance_groups:
                instance_groups[annot['id']] += 1
            else:
                instance_groups[annot['id']] = 1

    image_id_to_annotations = {}
    for annot in tqdm(coco_json['annotations'], "Converting annotations"):
        if isinstance(annot['segmentation'], dict):
            annot['segmentation'] = annot_to_polygon(annot['segmentation'])

        cat = cat_id_to_cat[annot['category_id']]
        groupid = 0
        for polygon in annot['segmentation']:
            if 'id' in annot and annot[
                'id'] in instance_groups and instance_groups[annot['id']] > 1:
                groupid = annot['id']

            sa_obj = _create_vector_instance(
                'polygon', polygon, {}, [], cat['name']
            )
            if groupid != 0:
                sa_obj['groupId'] = groupid

            if str(annot['image_id']) not in image_id_to_annotations:
                image_id_to_annotations[str(annot['image_id'])] = [sa_obj]
            else:
                image_id_to_annotations[str(annot['image_id'])].append(sa_obj)

    save_sa_jsons(coco_json, image_id_to_annotations, output_dir)


def coco_object_detection_to_sa_vector(coco_path, output_dir):
    coco_json = json.load(open(coco_path))
    cat_id_to_cat = {}
    for cat in coco_json['categories']:
        cat_id_to_cat[cat['id']] = cat

    image_id_to_annotations = {}
    for annot in tqdm(coco_json['annotations'], "Converting annotations"):
        if isinstance(annot['segmentation'], dict):
            annot['segmentation'] = annot_to_polygon(annot['segmentation'])
        cat = cat_id_to_cat[annot['category_id']]

        points = (
            annot['bbox'][0], annot['bbox'][1],
            annot['bbox'][0] + annot['bbox'][2],
            annot['bbox'][1] + annot['bbox'][3]
        )

        sa_obj = _create_vector_instance('bbox', points, {}, [], cat['name'])

        if str(annot['image_id']) not in image_id_to_annotations:
            image_id_to_annotations[str(annot['image_id'])] = [sa_obj]
        else:
            image_id_to_annotations[str(annot['image_id'])].append(sa_obj)

    save_sa_jsons(coco_json, image_id_to_annotations, output_dir)


def coco_keypoint_detection_to_sa_vector(coco_path, output_dir):
    coco_json = json.load(open(coco_path))

    cat_id_to_cat = {}
    for cat in coco_json["categories"]:
        cat_id_to_cat[cat["id"]] = {
            "name": cat["name"],
            "keypoints": cat["keypoints"],
            "skeleton": cat["skeleton"]
        }

    image_id_to_annotations = {}
    for annot in tqdm(coco_json['annotations'], 'Converting annotations'):
        if annot['num_keypoints'] > 0:
            sa_points = [
                item for index, item in enumerate(annot['keypoints'])
                if (index + 1) % 3 != 0
            ]

            sa_points = [
                (sa_points[i], sa_points[i + 1])
                for i in range(0, len(sa_points), 2)
            ]
            if annot["category_id"] in cat_id_to_cat.keys():
                keypoint_names = cat_id_to_cat[annot["category_id"]
                                              ]['keypoints']

                bad_points = []
                id_mapping = {}
                index = 1
                points = []
                for point_index, point in enumerate(sa_points):
                    if sa_points[point_index] == (0, 0):
                        bad_points.append(point_index + 1)
                        continue
                    id_mapping[point_index + 1] = index
                    points.append({'id': index, 'x': point[0], 'y': point[1]})
                    index += 1

                connections = []
                for connection in cat_id_to_cat[annot["category_id"]
                                               ]['skeleton']:

                    index = cat['skeleton'].index(connection)
                    from_point = cat_id_to_cat[annot["category_id"]
                                              ]['skeleton'][index][0]
                    to_point = cat_id_to_cat[annot["category_id"]
                                            ]['skeleton'][index][1]

                    if from_point in bad_points or to_point in bad_points:
                        continue

                    connections.append(
                        {
                            'id': index + 1,
                            'from': id_mapping[from_point],
                            'to': id_mapping[to_point]
                        }
                    )

                pointLabels = {}
                for kp_index, kp_name in enumerate(keypoint_names):
                    if kp_index + 1 in bad_points:
                        continue
                    pointLabels[id_mapping[kp_index + 1] - 1] = kp_name

                sa_obj = _create_vector_instance(
                    'template', points, pointLabels, [],
                    cat_id_to_cat[annot["category_id"]]["name"], connections
                )
                if str(annot['image_id']) not in image_id_to_annotations:
                    image_id_to_annotations[str(annot['image_id'])] = [sa_obj]
                else:
                    image_id_to_annotations[str(annot['image_id']
                                               )].append(sa_obj)

    save_sa_jsons(coco_json, image_id_to_annotations, output_dir)
