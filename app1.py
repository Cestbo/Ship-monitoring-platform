from flask import Flask, render_template, jsonify, request
from entity.model import FLowOfDay, BoatRecord
from util.dbutil import DatabaseManagement, objToDict
from sqlalchemy import and_

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    return render_template("base.html")

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