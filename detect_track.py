from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
import cv2
import imutils
import dlib
import numpy as np
import time
from util.dbutil import DatabaseManagement
from entity.model import FLowOfDay
from datetime import datetime


# 定义参数
prototxt = 'models/mobilenetSSD/MobileNetSSD_deploy.prototxt'
model = 'models/mobilenetSSD/MobileNetSSD_deploy.caffemodel'
set_confidence = 0.4
skip_frames = 30

# initialize the list of class labels MobileNet SSD was trained to
# detect
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

print("[INFO] 加载网络")
net = cv2.dnn.readNetFromCaffe(prototxt, model)
W = None
H = None
trackers = []
trackableObjects = {}
totalFrames = 0
ct_dict = {
    "area1": CentroidTracker(maxDisappeared=40, maxDistance=50),
    "area2": CentroidTracker(maxDisappeared=40, maxDistance=50),
    "area3": CentroidTracker(maxDisappeared=40, maxDistance=50),
    "area4": CentroidTracker(maxDisappeared=40, maxDistance=50),
}
# 保存各区域的船舶计数量
counts_dict = {
    "area1": 0,
    "area2": 0,
    "area3": 0,
    "area4": 0
}


def track(frame, area):
    global W, H, totalFrames, skip_frames, set_confidence, trackers, counts_dict, CLASSES
    ct = ct_dict[area]
    # 0点清空计数
    t = time.strftime("%H:%M:%S")
    if t == '00:00:00':
        dbm = DatabaseManagement()
        dbm.add_obj(FLowOfDay(datetime.now(), counts_dict[area], area))
        dbm.close()
        for key in counts_dict.keys():
            counts_dict[key] = 0

    frame = imutils.resize(frame, width=500)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # if the frame dimensions are empty, set them
    if W is None or H is None:
        (H, W) = frame.shape[:2]

    rects = []

    # check to see if we should run a more computationally expensive
    # object detection method to aid our tracker
    if totalFrames % skip_frames == 0:
        trackers = []

        # convert the frame to a blob and pass the blob through the
        # network and obtain the detections
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
        net.setInput(blob)
        detections = net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated
            # with the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by requiring a minimum
            # confidence
            if confidence > set_confidence:
                # extract the index of the class label from the
                # detections list
                idx = int(detections[0, 0, i, 1])

                # if the class label is not a person, ignore it
                if CLASSES[idx] != "person":
                    continue

                # compute the (x, y)-coordinates of the bounding box
                # for the object
                box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = box.astype("int")

                # construct a dlib rectangle object from the bounding
                # box coordinates and then start the dlib correlation
                # tracker
                tracker = dlib.correlation_tracker()
                rect = dlib.rectangle(int(startX), int(startY), int(endX), int(endY))
                tracker.start_track(rgb, rect)

                # add the tracker to our list of trackers so we can
                # utilize it during skip frames
                trackers.append(tracker)

    # otherwise, we should utilize our object *trackers* rather than
    # object *detectors* to obtain a higher frame processing throughput
    else:
        # loop over the trackers
        for tracker in trackers:
            # update the tracker and grab the updated position
            tracker.update(rgb)
            pos = tracker.get_position()

            # unpack the position object
            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())

            # add the bounding box coordinates to the rectangles list
            rects.append((startX, startY, endX, endY))

    # use the centroid tracker to associate the (1) old object
    # centroids with (2) the newly computed object centroids
    objects = ct.update(rects, area)

    # loop over the tracked objects
    for (objectID, centroid) in objects.items():
        # check to see if a trackable object exists for the current
        # object ID
        to = trackableObjects.get(objectID, None)

        # if there is no existing trackable object, create one
        if to is None:
            to = TrackableObject(objectID, centroid)

        # otherwise, there is a trackable object so we can utilize it
        # to determine direction
        else:
            to.centroids.append(centroid)

            # check to see if the object has been counted or not
            if not to.counted:
                counts_dict[area] += 1
                to.counted = True

        # store the trackable object in our dictionary
        trackableObjects[objectID] = to

        # draw both the ID of the object and the centroid of the
        # object on the output frame
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
    totalFrames += 1

    return frame
