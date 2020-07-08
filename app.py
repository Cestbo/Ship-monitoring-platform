from flask import Flask, render_template, Response
import threading
import datetime
import imutils
import cv2
import imagezmq
import numpy as np

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]
CONSIDER = set(["dog", "person", "car"])

app = Flask(__name__)
app.config['DEBUG'] = True

# initialize the ImageHub object
imageHub = imagezmq.ImageHub()


def detect_frame(frame, net):
    global CLASSES, CONSIDER

    frame = imutils.resize(frame, width=400)
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 0.007843, (300, 300), 127.5)
    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()

    # reset the object count for each object in the CONSIDER set
    objCount = {obj: 0 for obj in CONSIDER}

    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the confidence is
        # greater than the minimum confidence
        if confidence > 0.2:
            # extract the index of the class label from the
            # detections
            idx = int(detections[0, 0, i, 1])

            # check to see if the predicted class is in the set of
            # classes that need to be considered
            if CLASSES[idx] in CONSIDER:
                # increment the count of the particular object
                # detected in the frame
                objCount[CLASSES[idx]] += 1

                # compute the (x, y)-coordinates of the bounding box
                # for the object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the bounding box around the detected object on
                # the frame
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                              (255, 0, 0), 2)
    # draw the object count on the frame
    label = ", ".join("{}: {}".format(obj, count) for (obj, count) in
                      objCount.items())
    cv2.putText(frame, label, (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame


def detect_stream():
    # grab global references to the video stream, output frame, and
    # lock variables
    global imageHub, outputFrame, lock
    outputFrame = None

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe("models/mobilenetSSD/MobileNetSSD_deploy.prototxt",
                                   "models/mobilenetSSD/MobileNetSSD_deploy.caffemodel")

    frameDict = {}
    print("[INFO] detecting: {}...".format(", ".join(obj for obj in
                                                     CONSIDER)))
    # initialize the dictionary which will contain  information regarding
    # when a device was last active, then store the last time the check
    # was made was now
    lastActive = {}
    lastActiveCheck = datetime.datetime.now()

    # loop over frames from the video stream
    while True:
        (rpiName, frame) = imageHub.recv_image()
        imageHub.send_reply(b'OK')
        # if a device is not in the last active dictionary then it means
        # that its a newly connected device
        if rpiName not in lastActive.keys():
            print("[INFO] receiving data from {}...".format(rpiName))
        # record the last active time for the device from which we just
        # received a frame
        lastActive[rpiName] = datetime.datetime.now()

        frame = detect_frame(frame, net)

        # draw the sending device name on the frame
        cv2.putText(frame, rpiName, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # update the new frame in the frame dictionary
        frameDict[rpiName] = frame

        # acquire the lock, set the output frame, and release the
        # lock
        with lock:
            outputFrame = frame.copy()


def generate():
    # grab global reference to the output frame and lock variables
    global outputFrame, lock

    # loop over frames from the ouput stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodeImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yeild the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodeImage) + b'\r\n')


@app.route('/')
def index():
    return render_template("base.html")


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # start a thread that will perform motion detection
    t = threading.Thread(target=detect_stream)
    t.daemon = True
    t.start()

    # start the flask app
    app.run(debug=True,
            threaded=True, use_reloader=False)
