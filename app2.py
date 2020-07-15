from flask import Response, jsonify, request
from app1 import app
import threading
import cv2
from detect_track import track
import argparse
import imagezmq

outputFrame = None
counts = 0
lock_outframe = threading.Lock()

area = 'area1'
lock_area = threading.Lock()

outputFrameDict = {
    "area1": None,
    "area2": None,
    "area3": None,
    "area4": None
}
lock_dict = threading.Lock()

# initialize the ImageHub object
imageHub = imagezmq.ImageHub()


def get_srcframe():
    print("[INFO] 开始线程:获取原视频")
    global imageHub, outputFrameDict
    while True:
        (rpiName, frame) = imageHub.recv_image()
        imageHub.send_reply(b'OK')
        with lock_dict:
            outputFrameDict[rpiName] = frame


def get_outframe():
    print("[INFO] 开始追踪线程")
    global outputFrame, lock_outframe, counts, outputFrameDict, lock_dict, area, lock_area
    while True:
        with lock_dict, lock_area:
            frame = outputFrameDict[area]
        if frame is None:
            continue
        frame, new_counts = track(frame)
        with lock_outframe:
            outputFrame = frame.copy()
            counts = new_counts


def outframe_gen():
    global outputFrame, lock_outframe
    while True:
        with lock_outframe:
            if outputFrame is None:
                continue
            (flag, encodeImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodeImage) + b'\r\n')


def generate(rpiName):
    # grab global reference to the output frame and lock variables
    global outputFrameDict, lock_dict

    # loop over frames from the ouput stream
    while True:
        # wait until the lock is acquired
        with lock_dict:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrameDict[rpiName] is None:
                continue

            # encode the frame in JPEG format
            (flag, encodeImage) = cv2.imencode(".jpg", outputFrameDict[rpiName])

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yeild the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodeImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    rpiName = request.args.get("rpiName")
    # return the response generated along with the specific media
    # type (mime type)
    if rpiName == 'main':
        return Response(outframe_gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response(generate(rpiName),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_counts')
def get_counts():
    global counts
    ret = {
        'counts': counts,
    }
    return jsonify(ret)


@app.route('/change_area')
def change_area():
    global area
    with lock_area:
        area = request.args.get("area")
    ret = {
        'msg': '切换区域成功'
    }
    return jsonify(ret)


if __name__ == '__main__':
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--input", type=str, default='videos/example_01.mp4',
    #                 help="path to optional input video file")
    # args = vars(ap.parse_args())
    # print("[INFO] 获取视频源")
    # vs = cv2.VideoCapture(args['input'])

    # start a thread that will perform motion detection
    t1 = threading.Thread(target=get_srcframe)
    t2 = threading.Thread(target=get_outframe)
    for t in [t1, t2]:
        t.daemon = True
        t.start()

    # start the flask app
    print("[INFO] 开启flask")
    app.run(debug=True,
            threaded=True, use_reloader=False)
