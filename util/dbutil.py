# db_mg.py
from sqlalchemy import create_engine, func, distinct, and_
from sqlalchemy.orm import sessionmaker
from entity.model import FLowOfDay,BoatRecord
from datetime import datetime
import re


# 将类转换成字典
def objToDict(obj):
    obj_dict = obj.__dict__
    keys = obj_dict.keys()
    for key in list(keys):
        if re.match('_',key) is not None:
            del obj_dict[key]
    return obj_dict



class DatabaseManagement():
    def __init__(self):
        self.engine = create_engine('mssql+pymssql://sa:951115@localhost:1433/ship', echo=True)  # 初始化数据库连接
        DBsession = sessionmaker(bind=self.engine)  # 创建DBsession类
        self.session = DBsession()  # 创建对象

    def add_obj(self, obj):  # 添加内容
        self.session.add(obj)
        self.session.commit()  # 提交
        return obj

    def query_all(self, target_class, query_filter=None):  # 查询内容
        if query_filter is None:
            result_list = self.session.query(target_class).all()
        else:
            result_list = self.session.query(target_class).filter(query_filter).all()
        return result_list

    def update_by_filter(self, obj, update_hash, query_filter):  # 更新内容
        self.session.query(obj.__class__).filter(query_filter).update(update_hash)
        self.session.commit()

    def delete_by_filter(self, obj, query_filter):  # 删除内容
        self.session.query(obj).filter(query_filter).delete()

    def close(self):  # 关闭session
        self.session.close()

    def execute_sql(self, sql_str):  # 执行sql语句
        return self.session.execute(sql_str)

    def count(self, obj, filter = None):
        if filter is None:
            return self.session.query(func.count(distinct(obj.id))).scalar()
        else:
            return self.session.query(func.count(distinct(obj.id))).filter(filter).scalar()

    def query_page(self,obj,page_index,page_size,fliter=None):
        if fliter is None:
            return self.session.query(obj).order_by(obj.id.desc()).\
                limit(page_size).offset((page_index - 1) * page_size).all()
        else:
            return self.session.query(obj).filter(fliter).\
                order_by(obj.id.desc()).limit(page_size).offset((page_index - 1) * page_size).all()


if __name__=="__main__":
    dbm=DatabaseManagement()
    boat_record = BoatRecord(1,datetime.now(), 1, 1,
                             datetime.now(), 1, 1)
    dbm.add_obj(boat_record)
    dbm.close()