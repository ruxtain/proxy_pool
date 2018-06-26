'''
重构模型的 count 计数更新规则
使用 mongoengine 替代自制的 orm
'''

import os
import random
from datetime import datetime
from proxy_pool import settings
import logging
import proxy_pool
from mongoengine import *

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
logfile = os.path.join(path, 'proxy_pool.log')
logging.basicConfig(
    filename=logfile, 
    filemode='a', 
    level=logging.DEBUG,
    datefmt='[%Y-%m-%d %H:%M:%S]',
    format='%(asctime)s %(message)s',
)
# 因为 proxy 的状态需要打印到日志，所以把日志配置到这里，以及把 print_log 定义到这里
# 之所以用 a 模式是因为多进程写日志用 w 只能允许某一个进程写入，
# 用 a 的话，每次允许程序前清空日志，可以达到类似 w 的效果。

def init_log():
    with open(logfile, 'w', encoding='utf-8') as f:
        pass

def print_log(content, level='debug'):
    print(content)
    if level == 'debug':
        logging.debug(content)
    elif level == 'info':
        logging.info(content)
    elif level == 'warning':
        logging.warning(content)
    elif level == 'critical':
        logging.critical(content)

class Proxy(Document):
    value = StringField(required=True, unique=True)
    count = IntField(default=0) 
    update_time = DateTimeField(default=datetime.now())
    def __str__(self):
        return "({}, count={})".format(self.value, self.count)

    @classmethod
    def total(cls):
        '''return the total number of proxies'''
        collection = cls._get_collection()
        return collection.count()

    @classmethod
    def random(cls):
        collection = cls._get_collection()
        # count = collection.count()
        # rand = random.choice(range(1, count+1))
        # _id = collection.find().limit(-1).skip(rand).next()['_id']
        # a = dict(collection.find().limit(-1).skip(rand).next())
        # return cls.objects.get(value=value)
        # _id = list(collection.aggregate([{ '$sample': { 'size': 1 } }]))[0]['_id'] # 未经大量测试的随机
        _id = list(collection.aggregate([{ '$sample': { 'size': 1 } }]))[0]['_id']
        return cls.objects.get(id=_id) # mongoengine 中 _id 被写作 id

    @classmethod
    def quality_rate(cls):
        '''
        良品率：
        当良品率过低时，表明代理质量很差，
        需要增加检测有效性的进程数
        '''
        good = cls.objects.filter(count=0).count()
        bad = cls.objects.filter(count__gt=0).count() 
        return good / (bad + 1)

    def status(self, *info):
        content = '{:<24} count: {:<5}update: {:<12}total: {}   -->   {}'.format(
            self.value,
            self.count,
            self.update_time.strftime("%H:%M:%S"),
            self.total(),
            ' '.join([str(i) for i in info])
        )
        print(content)
        logging.debug(content)

connect(
    Proxy.__name__,
    host = settings.DB_HOST,
    port = settings.DB_PORT
) # 用类名作为 db 名

if __name__ == '__main__':
    p = Proxy.random()
    print(p)

    # p=Proxy(value='23.67.189.1000:7878')
    # p = Proxy.objects.order_by().first()
    # print(p)
    # p = Proxy.objects.get(count=0)
    # print(p.value)
    # print(p)