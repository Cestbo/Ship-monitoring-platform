# Ship-monitoring-platform

## 运行
python app2.py -i 'video_path'  (default：videos/example_01.mp4)

## 接口：

### /video_feed
获取监控画面

### /get_counts  get
获取当天实时船舶通行量

返回：counts

### /get_flowofday post
根据时间范围和页数查询历史每天统计量
参数：page当前页   time_s开始时间（可空）   time_e结束时间（可空）

返回：
```python
{
  "flowdata":[
     {
      'day':'2020-07-07',
      'flow':3,
      'id':1
     },
     {
      'day':'2020-07-07',
      'flow':3,
      'id':2
     }
  ],
  'num':8
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
            "area": "区域一",
            "id": 9,
            "in_time": "2020-07-10 16:16:10",
            "in_x": 410,
            "in_y": 64,
            "out_time": "2020-07-10 16:16:15",
            "out_x": 393,
            "out_y": 346,
            "type": "船舶"
        },
        {
            "area": "区域一",
            "id": 8,
            "in_time": "2020-07-10 16:16:10",
            "in_x": 335,
            "in_y": 62,
            "out_time": "2020-07-10 16:16:15",
            "out_x": 354,
            "out_y": 361,
            "type": "船舶"
        }
    ],
    "num": 9
}
```