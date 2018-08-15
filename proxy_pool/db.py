"""
    A new version of Mongo ORM (based on mongoengine)
"""

from mongoengine import Document, StringField, IntField, DateTimeField
from mongoengine import connect, errors

from proxy_pool import settings
import proxy_pool

from datetime import datetime
import logging
import random
import os


DoesNotExist = errors.DoesNotExist
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
    """ clear previous log before running """
    with open(logfile, 'w', encoding='utf-8') as f:
        pass

def print_log(content, level='debug'):
    """ output log to both console and proxy_pool.log file """
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
    def valid(cls):
        '''
        return the number of valid proxies
        I define them by count == 0
        '''
        return cls.objects.filter(count__lt=2).count()

    @classmethod
    def random(cls): # 只取 count < 2 的高质量代理
        return random.choice(cls.objects.filter(count__lt=2))

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
        content = '{:<24} update: {:<12}total: {:<6}valid: {}   ->   {}'.format(
            self.value,
            self.update_time.strftime("%H:%M:%S"),
            self.total(),
            self.valid(),
            ' '.join([str(i) for i in info])
        )
        print_log(content)
        
        
# MAC 下报警告：UserWarning: MongoClient opened before fork. Create MongoClient only after forking. See PyMongo's documentation for details: http://api.mongodb.org/python/current/faq.html#is-pymongo-fork-safe
# "MongoClient opened before fork. Create MongoClient only "
# WIN 下没有任何问题，暂时不深究。
connect(
    Proxy.__name__,
    host = settings.DB_HOST,
    port = settings.DB_PORT,
    connect = False,
) 

if __name__ == '__main__':
    p = Proxy.random()
    print(p)

    # p=Proxy(value='23.67.189.1000:7878')
    # p = Proxy.objects.order_by().first()
    # print(p)
    # p = Proxy.objects.get(count=0)
    # print(p.value)
    # print(p)