from flask import Flask, render_template, Response, jsonify, request
import threading
import cv2
from detect_track import track
import argparse
from entity.model import FLowOfDay, BoatRecord
from util.dbutil import DatabaseManagement, objToDict
from sqlalchemy import and_

outputFrame = None
lock = threading.Lock()
counts = 0

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False


def get_outframe(vs):
    print("[INFO] 开始线程")
    global outputFrame, lock, counts
    while True:
        _, frame = vs.read()
        if frame is None:
            break
        frame, new_counts = track(frame)
        with lock:
            outputFrame = frame.copy()
            counts = new_counts


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


@app.route('/get_counts')
def get_counts():
    global counts
    ret = {
        'counts': counts,
    }
    return jsonify(ret)


@app.route('/get_shiptype')
def get_shiptype():
    shiptype = ["客货船",
                "普通货船",
                "集装箱船",
                "滚装船",
                "载驳货船",
                "散货船",
                "油船",
                "液化气体船",
                "兼用船",
                "其它"]
    return jsonify(shiptype)


@app.route("/get_flowofday", methods=['POST'])
def get_flowofday():
    page = int(request.form.get("page"))
    time_s = request.form.get("time_s")
    time_e = request.form.get("time_e")
    pagesize = 2
    fliter = None
    if time_s is not None and time_e is not None:
        fliter = and_(FLowOfDay.day >= time_s, FLowOfDay.day <= time_e)
    if time_s is not None and time_e is None:
        fliter = and_(FLowOfDay.day >= time_s)
    if time_s is None and time_e is not None:
        fliter = and_(FLowOfDay.day <= time_e)

    dbm = DatabaseManagement()
    flows = dbm.query_page(FLowOfDay, page, pagesize, fliter)
    num = dbm.count(FLowOfDay, fliter)
    dbm.close()
    list = []
    for flow in flows:
        dict = objToDict(flow)
        dict['day'] = dict['day'].strftime('%Y-%m-%d')
        list.append(dict)
    ret = {
        'num': num,
        'flowdata': list
    }
    return jsonify(ret)


@app.route("/get_boatrecord", methods=['POST'])
def get_boatrecord():
    page = int(request.form.get("page"))
    time_s = request.form.get("time_s")
    time_e = request.form.get("time_e")
    pagesize = 2
    fliter = None
    if time_s is not None and time_e is not None:
        fliter = and_(BoatRecord.in_time >= time_s, BoatRecord.out_time <= time_e)
    if time_s is not None and time_e is None:
        fliter = and_(BoatRecord.in_time >= time_s)
    if time_s is None and time_e is not None:
        fliter = and_(BoatRecord.out_time <= time_e)
    dbm = DatabaseManagement()
    boatrecords = dbm.query_page(BoatRecord, page, pagesize, fliter)
    num = dbm.count(BoatRecord, fliter)
    dbm.close()
    list = []
    for boatrecord in boatrecords:
        dict = objToDict(boatrecord)
        dict['in_time'] = dict['in_time'].strftime('%Y-%m-%d %H:%M:%S')
        dict['out_time'] = dict['out_time'].strftime('%Y-%m-%d %H:%M:%S')
        list.append(dict)
    ret = {
        'num': num,
        'boatrecords': list
    }
    return jsonify(ret)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", type=str, default='videos/example_01.mp4',
                    help="path to optional input video file")
    args = vars(ap.parse_args())
    print("[INFO] 获取视频源")
    vs = cv2.VideoCapture(args['input'])

    # start a thread that will perform motion detection
    t = threading.Thread(target=get_outframe, args=(vs,))
    t.daemon = True
    t.start()

    # start the flask app
    print("[INFO] 开启flask")
    app.run(debug=True,
            threaded=True, use_reloader=False)
