from flask import Response, jsonify, request
from app1 import app
import threading
import cv2
from detect_track import track
import argparse
import imagezmq
from detect_track import counts_dict

# 保存源视频帧
srcFrameDict = {
    "area1": None,
    "area2": None,
    "area3": None,
    "area4": None
}
lock_srcFrame = threading.Lock()

# 保存检测后的视频帧
outputFrameDict = {
    "area1": None,
    "area2": None,
    "area3": None,
    "area4": None
}
lock_outputFrame = threading.Lock()

# initialize the ImageHub object
imageHub = imagezmq.ImageHub()


def get_frame():
    print("[INFO] 开始线程:获取原视频帧并进行检测")
    global srcFrameDict, lock_srcFrame, outputFrameDict, lock_outputFrame
    while True:
        (rpiName, frame) = imageHub.recv_image()
        imageHub.send_reply(b'OK')
        # save src_frame
        with lock_srcFrame:
            srcFrameDict[rpiName] = frame
        # detect and track
        frame = track(frame, rpiName)
        # save output_frame and counts
        with lock_outputFrame:
            outputFrameDict[rpiName] = frame.copy()

def outFrame_gen(area):
    global outputFrameDict, lock_outputFrame
    while True:
        with lock_outputFrame:
            if outputFrameDict[area] is None:
                continue
            (flag, encodeImage) = cv2.imencode(".jpg", outputFrameDict[area])
            if not flag:
                continue
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodeImage) + b'\r\n')


def srcFrame_gen(rpiName):
    # grab global reference to the output frame and lock variables
    global srcFrameDict, lock_srcFrame

    # loop over frames from the ouput stream
    while True:
        # wait until the lock is acquired
        with lock_srcFrame:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if srcFrameDict[rpiName] is None:
                continue

            # encode the frame in JPEG format
            (flag, encodeImage) = cv2.imencode(".jpg", srcFrameDict[rpiName])

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yeild the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodeImage) + b'\r\n')


@app.route("/srcVideo_feed")
def srcVideo_feed():
    rpiName = request.args.get("rpiName")
    # return the response generated along with the specific media
    # type (mime type)
    return Response(srcFrame_gen(rpiName),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/outVideo_feed")
def outVideo_feed():
    rpiName = request.args.get("rpiName")
    # return the response generated along with the specific media
    # type (mime type)
    return Response(outFrame_gen(rpiName),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_counts')
def get_counts():
    return jsonify(counts_dict)


if __name__ == '__main__':
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--input", type=str, default='videos/example_01.mp4',
    #                 help="path to optional input video file")
    # args = vars(ap.parse_args())
    # print("[INFO] 获取视频源")
    # vs = cv2.VideoCapture(args['input'])

    # start threads that will perform motion detection
    t = threading.Thread(target=get_frame)
    t.daemon = True
    t.start()

    # start the flask app
    print("[INFO] 开启flask")
    app.run(debug=True,
            threaded=True, use_reloader=False)
