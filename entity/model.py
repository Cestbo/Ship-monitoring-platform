from sqlalchemy import Column, String, INT, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # 创建对象的基类


class FLowOfDay(Base):
    __tablename__ = "flowofday"
    id = Column(INT(), primary_key=True)
    day = Column(Date())
    flow = Column(INT())

    def __init__(self,day,flow):
        self.day=day
        self.flow=flow
