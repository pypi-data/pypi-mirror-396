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

![Inference](./images/people.jpg)
![Grouped](./images/people-grouped.jpg)


![Inference](./images/people-walking.jpg)
![Grouped](./images/people-walking-grouped.jpg)

### How to use

```python

```