# Ship-monitoring-platform
[TOC]
## 更新内容
实现多区域同时监控并检测追踪

## 数据库改动
flowofday表增加area字段（String）表示区域

boat_record表增加no字段（int）表示船舶编号，现id字段只是一个自增的主键字段

## 运行
服务段运行：python app2.py

多客服端运行：python client.py -s [server_ip] -a [area_name]
(area_name默认分为四个区域：area1、area2、area3、area4)

## 接口：

### /srcVideo_feed get
获取监控画面

参数：rpiName区域名,可选四个值
area1、area2、area3、area4

### /outVideo_feed get
获取检测追踪后得画面

参数：rpiName区域名,可选四个值
area1、area2、area3、area4


### /get_counts  get
获取各区域当天实时船舶通行量

返回：
```python
{
    "area1": 0,
    "area2": 0,
    "area3": 0,
    "area4": 0
}
```

### /get_flowofday post
根据时间范围和页数查询历史每天统计量

参数：page当前页   time_s开始时间（可空）   time_e结束时间（可空）

返回：
```python
{
    "flowdata": [
        {
            "area": "area1",
            "day": "2020-07-20",
            "flow": 0,
            "id": 10
        },
        {
            "area": "area1",
            "day": "2020-07-20",
            "flow": 1,
            "id": 9
        }
    ],
    "num": 24
}
```

### /get_shiptype  get
获取船型类别

返回：
```python
[
  "客货船",
  "普通货船",
  "集装箱船",
  "滚装船",
  "载驳货船",
  "散货船",
  "油船",
  "液化气体船",
  "兼用船",
  "其它"
]
```

### /get_boatrecord  post
获取船舶的通行记录

参数：
page:   当前页
time_s--time_e: 起止时间（分别针对船舶进入时间和离开时间，即in_time>=time_s && out_time<=time_e） 可空，空即查询所有
时间参数样例：2020-07-10 16:15:52

返回样例：
```python
{
    "boatrecords": [
        {
            "area": "area1",
            "id": 78,
            "in_time": "2020-07-20 16:39:51",
            "in_x": 390,
            "in_y": 294,
            "no": 2,
            "out_time": "2020-07-20 16:40:01",
            "out_x": 393,
            "out_y": 293,
            "type": "船舶"
        },
        {
            "area": "area1",
            "id": 77,
            "in_time": "2020-07-20 16:39:06",
            "in_x": 328,
            "in_y": 286,
            "no": 0,
            "out_time": "2020-07-20 16:39:41",
            "out_x": 372,
            "out_y": 250,
            "type": "船舶"
        }
    ],
    "num": 78
}
```

