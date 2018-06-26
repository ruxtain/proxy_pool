'''
重构模型的 count 计数更新规则
使用 mongoengine 替代自制的 orm
'''

import random
from datetime import datetime
# from proxy_pool import settings
from mongoengine import *

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
        print('{:<24} count: {:<5}update: {:<12}total: {}   -->   {}'.format(
            self.value,
            self.count,
            self.update_time.strftime("%H:%M:%S"),
            self.total(),
            ' '.join([str(i) for i in info])
        ))     

connect(Proxy.__name__) # 用类名作为 db 名

if __name__ == '__main__':

    p = Proxy.random()
    print(p)

    # p=Proxy(value='23.67.189.1000:7878')
    # p = Proxy.objects.order_by().first()
    # print(p)
    # p = Proxy.objects.get(count=0)
    # print(p.value)
    # print(p)