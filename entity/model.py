from sqlalchemy import Column, String, INT, Date, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # 创建对象的基类


class FLowOfDay(Base):
    __tablename__ = "flowofday"
    id = Column(INT(), primary_key=True)
    day = Column(Date())
    flow = Column(INT())
    area = Column(String())

    def __init__(self, day, flow, area):
        self.day = day
        self.flow = flow
        self.area = area


class BoatRecord(Base):
    __tablename__ = 'boat_record'
    id = Column(INT(), primary_key=True, autoincrement=True)
    no = Column(INT())
    in_time = Column(DateTime())
    in_x = Column(Float())
    in_y = Column(Float())
    out_time = Column(DateTime())
    out_x = Column(Float())
    out_y = Column(Float())
    type = Column(String())
    area = Column(String())

    def __init__(self, no, in_time, in_x, in_y, out_time, out_x, out_y, type='船舶', area='区域一'):
        self.no = no
        self.in_time = in_time
        self.in_x = in_x
        self.in_y = in_y
        self.out_time = out_time
        self.out_x = out_x
        self.out_y = out_y
        self.type = type
        self.area = area
