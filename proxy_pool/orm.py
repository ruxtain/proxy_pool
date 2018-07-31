'''
A mini ORM for mongodb.
You can extend it if you want.

I might switch to mongoengine in the future 
as there's no need to reinvent the wheel.

http://docs.mongoengine.org/tutorial.html
'''

import random
import pymongo
from datetime import datetime
from proxy_pool import settings

class ClassPropertyDescriptor(object):
    '''
    classmethod decorator
    thanks to `Mahmoud Abdelkader`: 
    https://stackoverflow.com/questions/5189699/how-to-make-a-class-property
    '''

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        return self.fget.__get__(obj, cls)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self

def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


#########
#  ORM  #
#########

class InvalidFieldError(Exception):
    def __init__(self, err='Make sure the arguments match their fields type'):
        Exception.__init__(self, err)

class AttributeNotExistsError(Exception):
    def __init__(self, err='Attribute does not exist'):
        Exception.__init__(self, err)

class ModelNotExistsError(Exception):
    def __init__(self, err='Model does not exist'):
        Exception.__init__(self, err)        

class Field:
    def __init__(self, name=None, primary_key=False):
        self.name = name
        self.primary_key = primary_key

class CharField(Field):
    def validate(self, value):
        return isinstance(value, str)

class IntegerField(Field):
    def validate(self, value):
        return isinstance(value, int)

class DatetimeField(Field):
    def validate(self, value):
        return isinstance(value, datetime)

class ModelBase(type):
    '''
        metaclass for models
    '''
    def __new__(cls, name, bases, attrs):
        __primary_key__ = None
        mappings = {}
        for attr, field in attrs.items(): # include other built-in attributes
            if isinstance(field, Field):
                mappings[attr] = field
                if field.primary_key == True:
                    __primary_key__ = attr

        if __primary_key__:
            attrs['__primary_key__'] = __primary_key__ # Proxy --> Proxy.value is pk
        attrs['__mappings__'] = mappings # pass fields and their names
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=ModelBase):
    '''
    To avoid the following warning,
    UserWarning: MongoClient opened before fork. Create MongoClient only after forking. See PyMongo's documentation for details: http://api.mongodb.org/python/current/faq.html#is-pymongo-fork-safe
    "MongoClient opened before fork. Create MongoClient only "
    A database connection must be created with each Model instance, namely, "after fork".
    '''
    def __init__(self, **kwargs): 
        for attr, value in kwargs.items(): # 新建的 Proxy 对象的参数字典
            if attr != '_id': # mappings 中不含 _id 
                field = self.__mappings__[attr]
                if field.validate(value):
                    setattr(self, attr, value)
                else:
                    raise InvalidFieldError

    @classproperty
    def __collection__(cls): # fork 之后创建 client，以免报警告
        '''
        connect (optional): if True (the default), immediately begin connecting to 
        MongoDB in the background. Otherwise connect on the first operation.
        '''
        client = pymongo.MongoClient(settings.DB_HOST, settings.DB_PORT, connect=True)
        model_name = cls.__name__
        return client[model_name.lower()][model_name.capitalize()]

    @classmethod
    def get(cls, **kwargs):
        '''
        搜索结果数大于1时返回匹配条件的第一个对象（而不是报错）
        '''
        cls.__mappings__['_id'] = None # default
        defined_attrs = set(cls.__mappings__.keys()) # 模型中定义的属性的集合
        query_attrs = set(kwargs)
        if defined_attrs >= query_attrs: # 父集 > 子集， > 和 < 是属于符合
            record = cls.__collection__.find_one(kwargs)
            if record:
                _model = cls(**record)
                _model._id = record['_id']
                return _model
            else:
                return None
        else:
            no_exist_attrs = query_attrs - defined_attrs
            print('no_exist_attrs', no_exist_attrs)
            raise AttributeNotExistsError

    @classmethod
    def random(cls, **kwargs):
        '''
        返回任意一项
        '''
        count = cls.__collection__.count()
        rand = random.choice(range(1, count+1))
        _id = cls.__collection__.find().limit(-1).skip(rand).next()['_id']
        return cls.get(_id=_id)

    @classmethod
    def filter(cls, **kwargs):
        defined_attrs = set(cls.__mappings__.keys()) # 模型中定义的属性的集合
        query_attrs = set(kwargs)
        if defined_attrs >= query_attrs: # 父集 > 子集， > 和 < 是属于符合
            records = cls.__collection__.find(kwargs)
            if records:
                for record in records:
                    _model = cls(**record)
                    _model._id = record['_id']
                    yield _model
            else:
                return None
        else:
            no_exist_attrs = query_attrs - defined_attrs
            raise AttributeNotExistsError

    @classmethod
    def _count(cls):
        '''
        返回 item 的总数
        maybe 加个 objects 使得基类方法和类方法不怕重名
        '''
        return cls.__collection__.count()

    @classmethod
    def delete(cls, **kwargs):
        _model = cls.get(**kwargs)
        if _model:
            cls.__collection__.delete_one({'_id': _model._id})
        else:
            raise ModelNotExistsError

    def save(self): 
        '''
        Query `self` by _id, if it has no _id,
        query primary_key instead,
        if no promary_key, then add a record in database
        return True if it's adding new record;
        return Flase if it's update an existing one.
        '''

        if hasattr(self, '_id'):
            if self.__collection__.find_one({'_id': self._id}):
                self.__collection__.update_one(
                    {'_id': self._id}, 
                    {'$set': self.__dict__}
                )   
                return False         
            else:
                self.__collection__.insert_one(self.__dict__)
                return True
        elif hasattr(self, '__primary_key__'):
            if self.__collection__.find_one({self.__primary_key__: self.__getattribute__(self.__primary_key__)}):
                self.__collection__.update_one(
                    {self.__primary_key__: self.__getattribute__(self.__primary_key__)}, 
                    {'$set': self.__dict__}
                )
                return False
            else:
                self.__collection__.insert_one(self.__dict__)
                return True
        else:
            self.__collection__.insert_one(self.__dict__)
            return True

###########
#  Model  #
###########

class Proxy(Model):
    value = CharField('proxy', primary_key=True)
    count = IntegerField('fail time') 
    update = DatetimeField('datetime')
    def __str__(self):
        return str(self.__dict__)
    def status(self, *info):
        print('{:<24} count: {:<5}update: {:<12}total: {}   -->   {}'.format(
            self.value,
            self.count,
            self.update.strftime("%H:%M:%S"),
            self._count(),
            ' '.join([str(i) for i in info])
        ))        

#############
#  Testing  #
#############

def main():
    m1 = Proxy(value='123.123.12.123:8000', count=1, update=datetime.now())
    m1.count = 2
    m1.save()
    # r1 = Proxy.random()
    # Proxy.delete(value='123.123.12.123:8000')
