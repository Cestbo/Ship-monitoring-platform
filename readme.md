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


