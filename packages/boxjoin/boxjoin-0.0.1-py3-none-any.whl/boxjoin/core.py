import cv2

def BoxClustering(boxes, img, path, w, h, offset):
    clusters = start_clustering(boxes)

    for _, cluster in enumerate(clusters):
        x1, y1, x2, y2 = find_cluster_coordinate(cluster)
        x1, y1, x2, y2 = offset_box(x1, y1, x2, y2, w, h, offset)
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 8)
    cv2.imwrite(path, img)

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
            box, cluster, boxes, done_boxes
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
                next_box, boxes, cluster, done_boxes
            )

    return cluster


# Check if two boxes overlap
def boxes_overlap(box1, box2):
    x1, y1, x2, y2 = map(int, box1)
    x3, y3, x4, y4 = map(int, box2)

    return x1 < x4 and x3 < x2 and y1 < y4 and y3 < y2


# Find the big rectangle coordinate of a cluster
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
