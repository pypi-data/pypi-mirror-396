## boxjoin

### Install

```shell
pip install boxjoin
````

### How it works

It works by detecting overlapped bounding box. Overlapped box will be grouped as one large bouding box.
It is useful for grouping some bounding box (from YOLO, etc).
But, currently it is not label aware and working based on coordinate.

### Showcase

#### Group of people
![Inference](https://raw.githubusercontent.com/dukenmarga/boxjoin/main/images/people.jpg)
![Grouped](https://raw.githubusercontent.com/dukenmarga/boxjoin/main/images/people-grouped.jpg)

#### Walking at the park
![Inference](https://raw.githubusercontent.com/dukenmarga/boxjoin/main/images/people-walking.jpg)
![Grouped](https://raw.githubusercontent.com/dukenmarga/boxjoin/main/images/people-walking-grouped.jpg)

#### Group of text from Medium
Source: https://stackoverflow.com/questions/66490374/how-to-merge-nearby-bounding-boxes-opencv

![Medium](https://raw.githubusercontent.com/dukenmarga/boxjoin/main/images/medium.jpg)
![Grouped](https://raw.githubusercontent.com/dukenmarga/boxjoin/main/images/medium-grouped.jpg)

### Example

```python
import boxjoin
import cv2

filename = "people-walking-original.jpg"
save_path = "people-walking-original-grouped.jpg"

img = cv2.imread(filename)

# Each box is in the format of [x1, y1, x2, y2]
# They can be extracted from YOLO output.
# This example is simply for demonstration
boxes = [
    [143, 91, 174, 118],
    [142, 98, 164, 123],
    [143, 87, 204, 165],
    [127, 118, 225, 181],
    [371, 195, 386, 220],
    [334, 152, 380, 243],
    [293, 193, 335, 301],
    [470, 136, 494, 167],
    [464, 123, 500, 214],
    [565, 234, 586, 260],
    [554, 178, 582, 261],
    [219, 313, 261, 405],
    [182, 297, 223, 387],
    [151, 315, 196, 421]
]

clusters = boxjoin.BoxClustering(boxes=boxes, img=img, save_path=save_path)

for i, cluster in enumerate(clusters):
    print(f"Cluster {i}: {cluster}")
    # The output should look like this:
    # Cluster 0: [[143, 91, 174, 118], [142, 98, 164, 123], [143, 87, 204, 165], [127, 118, 225, 181]]
    # Cluster 1: [[371, 195, 386, 220], [334, 152, 380, 243], [293, 193, 335, 301]]
    # Cluster 2: [[470, 136, 494, 167], [464, 123, 500, 214]]
    # Cluster 3: [[565, 234, 586, 260], [554, 178, 582, 261]]
    # Cluster 4: [[219, 313, 261, 405], [182, 297, 223, 387], [151, 315, 196, 421]]
```

Full example can be found in `example` directory