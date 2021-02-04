import json
from threading import Thread

from sqlalchemy.orm import sessionmaker
import pika

from sqlalchemy import create_engine

from application.models import *
from config import SQLALCHEMY_DATABASE_URI, logger

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
    # echo=True
)
Base.metadata.create_all(engine)

# 创建session
DbSession = sessionmaker(bind=engine)
session = DbSession()


def RabbitMQ_channel(RabbitMQconfig):
    credentials = pika.PlainCredentials(
        username=RabbitMQconfig.user,
        password=RabbitMQconfig.password
    )  # mq用户名和密码
    # 虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RabbitMQconfig.host,
            port=RabbitMQconfig.port,
            virtual_host='/',
            credentials=credentials
        )
    )
    channel = connection.channel()
    return channel


def GetInsertOrUpdateObj(cls, data, filter_dict):
    '''
    cls:            Model 类名
    strFilter:      filter的参数.eg:"name='name-14'"
    **kw:           【属性、值】字典,用于构建新实例，或修改存在的记录

    '''
    # print('strFilter ; ',strFilter)
    existing = session.query(cls).filter_by(**filter_dict).first()
    if not existing:
        logger.info(f'即将新增1条数据:{json.dumps(data, ensure_ascii=False)}')
        res = cls()
        for k, v in data.items():
            if hasattr(res, k):
                setattr(res, k, v)
        return res
    else:
        res = existing
        if 'size' in data.keys():
            data.pop('size')
        logger.info(f'即将更新1条数据:{json.dumps(data, ensure_ascii=False)}')
        for k, v in data.items():
            if hasattr(res, k):
                setattr(res, k, v)

        return res


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
