import cv2
from typing import Literal
import numpy as np

def BoxClustering(boxes, img = None, save_path = None, w = 0, h = 0, offset: int = 0, mode: Literal["xyxy", "xywh"] = "xyxy"):
    # If img is provided, path must be provided
    if img is not None and save_path is None:
        raise ValueError("path must be provided if img is provided")

    # img is preferred to be numpy array (BGR) opened with cv2.
    # If not, we assume it is PIL image (RGB). Convert it to numpy array.
    if img is not None:
        if isinstance(img, np.ndarray):
            pass
        else:
            numpy_image_rgb = np.array(img)
            img = cv2.cvtColor(numpy_image_rgb, cv2.COLOR_RGB2BGR)

    # If img is provided and w and h are not provided, get them from the image
    if img is not None and w == 0 and h == 0:
        h, w = img.shape[:2]

    # If img is not provided and w and h are not provided, set them to 99999
    # This is for operation that does not require image input
    if img is None and w == 0 and h == 0:
        w = 99999
        h = 99999

    # If mode is xywh, convert all boxes to xyxy
    if mode == "xyxy":
        # default mode
        pass
    elif mode == "xywh":
        for i, xywh in enumerate(boxes):
            # Convert XYWH format (x,y center point and width, height) to XYXY format (x,y top left and x,y bottom right).
            xyxy = xywh_to_xyxy(xywh)

            # replace the xywh with xyxy
            boxes[i] = xyxy
    else:
        raise ValueError("mode must be 'xyxy' or 'xywh'")

    clusters = start_clustering(boxes)


    grouped_boxes = []
    grouped_boxes_offset = []
    for _, cluster in enumerate(clusters):
        x1, y1, x2, y2 = find_cluster_coordinate(cluster)
        grouped_boxes.append([x1, y1, x2, y2])
        x1, y1, x2, y2 = offset_box(x1, y1, x2, y2, w, h, offset)
        grouped_boxes_offset.append([x1, y1, x2, y2])
        if img is not None:
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 8)

    if img is not None:
        cv2.imwrite(save_path, img)

    return clusters, grouped_boxes, grouped_boxes_offset

# Start clustering the boxes
def start_clustering(boxes):
    # clusters contains all the clusters
    clusters = []

    # done_boxes contains all the box indices that has formed a cluster
    done_boxes = []

    for i, box in enumerate(boxes):
        # If a box has formed or join to a cluster, skip
        if i in done_boxes:
            continue

        # If not, then start a new cluster and mark it.
        # cluster contains all the boxes in a cluster
        cluster = []
        cluster = fit_box_to_current_cluster(
            box=box, boxes=boxes, cluster=cluster, done_boxes=done_boxes
        )

        # If the cluster is not empty, add it to the clusters
        if len(cluster) > 0:
            clusters.append(cluster)

    return clusters


# Recursively fit a box to a cluster.
# It will check if the box overlaps with any of the boxes in the cluster.
# If it overlaps, it will add the box to the cluster and mark it as done.
def fit_box_to_current_cluster(box, boxes, cluster, done_boxes):
    for i, next_box in enumerate(boxes):
        # If a box has formed a cluster, skip
        if i in done_boxes:
            continue

        # If not, check if it overlaps with neighboring boxes
        if boxes_overlap(box, next_box):
            cluster.append(next_box)
            done_boxes.append(i)
            cluster = fit_box_to_current_cluster(
                box=next_box, boxes=boxes, cluster=cluster, done_boxes=done_boxes
            )

    return cluster


# Check if two boxes overlap
def boxes_overlap(box1, box2):
    x1, y1, x2, y2 = map(int, box1)
    x3, y3, x4, y4 = map(int, box2)

    return x1 < x4 and x3 < x2 and y1 < y4 and y3 < y2


# Determine the big rectangle coordinate of a cluster
# formed by a list of boxes.
# It will be determined by the most left, most top, most right, and most bottom
# of the boxes
def find_cluster_coordinate(cluster):
    for i, box in enumerate(cluster):
        if i == 0:
            x1 = int(box[0])
            y1 = int(box[1])
            x2 = int(box[2])
            y2 = int(box[3])
        else:
            x1 = min(x1, int(box[0]))
            y1 = min(y1, int(box[1]))
            x2 = max(x2, int(box[2]))
            y2 = max(y2, int(box[3]))
    return x1, y1, x2, y2


def offset_box(x1, y1, x2, y2, w, h, offset):
    x1 = max(0, x1 - offset)
    y1 = max(0, y1 - offset)
    x2 = min(w, x2 + offset)
    y2 = min(h, y2 + offset)

    return x1, y1, x2, y2

def xywh_to_xyxy(xywh):
    """
    Convert XYWH format (x,y center point and width, height) to XYXY format (x,y top left and x,y bottom right).
    :param xywh: [X, Y, W, H]
    :return: [X1, Y1, X2, Y2]
    """
    if isinstance(xywh, list) and len(xywh) != 4:
        for elem in xywh:
            if not isinstance(elem, (int, float)):
                raise ValueError('xywh format: [x1, y1, width, height]')
        raise ValueError('xywh format: [x1, y1, width, height]')
    x1 = xywh[0] - xywh[2] / 2
    y1 = xywh[1] - xywh[3] / 2
    x2 = xywh[0] + xywh[2] / 2
    y2 = xywh[1] + xywh[3] / 2

    return [int(x1), int(y1), int(x2), int(y2)]