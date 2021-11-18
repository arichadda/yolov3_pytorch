#!/usr/bin/python3

import os
import sys
import cv2
import time
import torch
import rospy
import torch.optim as optim
import torch.nn as nn
from PIL import Image
from sensor_msgs.msg import CompressedImage
from torchvision import datasets, transforms
from matplotlib import patches, patheffects
from paramiko import SSHClient
from scp import SCPClient


sys_paths = ['../']
for p in sys_paths:
    p = os.path.abspath(p)
    if p not in sys.path:
        sys.path.append(p)

from yolov3_pytorch.utils import *
from yolov3_pytorch.yolov3 import *
from yolov3_pytorch.yolov3_tiny import *

FREQUENCY = 10
IMG_WIDTH = 640
IMG_HEIGHT = 480
FOV = 60

class ObjectDetection:
    def __init__(self):
        self.class_names = ['person', 'bicycle', 'car', 'motorbike', 'aeroplane', 'bus', \
        'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', \
        'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', \
        'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', \
        'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', \
        'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', \
        'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', \
        'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', \
        'donut', 'cake', 'chair', 'sofa', 'pottedplant', 'bed', 'diningtable', \
        'toilet', 'tvmonitor', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', \
        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', \
        'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

        self.sz = 416

        self._img_sub = rospy.Subscriber('camera/rgb/image_raw/compressed', CompressedImage, callback=self._image_callback, queue_size=1)

        self.rel_angle = None
        self.timestamp_secs = None
        self.timestamp_nsecs = None

        self.model = Yolov3Tiny(num_classes=len(self.class_names))
        self.model.load_state_dict(torch.load('../yolov3_pytorch/yolov3_tiny_coco_01.h5'))

    # http://wiki.ros.org/rospy_tutorials/Tutorials/WritingImagePublisherSubscriber
    # https://github.com/holli/yolov3_pytorch
    def _image_callback(self, msg):
        np_arr = np.fromstring(msg.data, np.uint8)
        image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        img_org = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        img_org = Image.fromarray(img_org)
        img_resized = img_org.resize((self.sz, self.sz))
        img_torch = image2torch(img_resized)

        all_boxes = self.model.predict_img(img_torch, conf_thresh=0.2)[0]
        boxes_found = nms(all_boxes, 0.3)
        b = np.array(boxes_found)
        if len(b) > 0:
            classes = b[:, -1].astype(int)
            boxes = b[:, 0:4]

            boxes[:, 0] *= IMG_WIDTH
            boxes[:, 2] *= IMG_WIDTH
            boxes[:, 1] *= IMG_HEIGHT
            boxes[:, 3] *= IMG_HEIGHT

            for i in range(len(boxes)):
                b, class_id = boxes[i], classes[i]

                if b[0] == 0:
                    break
                if self.class_names[classes[i]] == 'clock':
                    self.timestamp_secs = msg.header.stamp.secs
                    self.timestamp_nsecs = msg.header.stamp.nsecs
                    x, y = b[0], b[1]
                    w, h = b[2], b[3]

                    bb_bottom = (x + w/2, y)
                    rel_angle = np.radians((FOV/(IMG_WIDTH) * bb_bottom[0] - FOV/2) * -1)
                    self.rel_angle = rel_angle

            plot_img_detections(img_resized, boxes_found, figsize=(8,8), class_names=self.class_names)

    # https://stackoverflow.com/questions/43577248/scp-in-python-by-using-password
    def ssh_scp_files(self, ssh_host, ssh_user, ssh_password, ssh_port, source_volume, destination_volume):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(ssh_host, username=ssh_user, password=ssh_password, look_for_keys=False)

        with SCPClient(ssh.get_transport()) as scp:
            scp.put(source_volume, recursive=True, remote_path=destination_volume)

    def detect(self):
        rate = rospy.Rate(FREQUENCY)
        while not rospy.is_shutdown():
            if self.rel_angle:
                with open('./object_angle.txt', 'w') as f:
                    f.write(str(self.rel_angle) + ' ' + str(self.timestamp_secs) + ' ' + str(self.timestamp_nsecs))
                self.ssh_scp_files(ssh_host='192.168.0.1', ssh_user='husarion', ssh_password='husarion', ssh_port='11311', source_volume='./object_angle.txt', destination_volume='/home/husarion/husarion_ws/src/hide-n-seek/src/hide_n_seek/nodes/object_angle.txt')
                rate.sleep()

if __name__ == "__main__":
    rospy.init_node('object_detection')
    object_detection = ObjectDetection()
    rospy.sleep(2)
    object_detection.detect()
