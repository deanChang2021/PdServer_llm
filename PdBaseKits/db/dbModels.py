import json
from datetime import datetime
import peewee
from PdBaseKits.db import db

class BaseModel(peewee.Model):
    class Meta:
        database = db

class User(BaseModel):
    username = peewee.CharField()
    password = peewee.TextField()
    nickname = peewee.TextField()
    email = peewee.TextField()
    registeTime = peewee.DateTimeField(default=datetime.now())

class InformationModel(BaseModel):
    id=peewee.AutoField()
    title= peewee.CharField()
    author= peewee.CharField()
    classify= peewee.CharField()
    content= peewee.TextField()
    level= peewee.CharField()
    state= peewee.CharField()
    tags= peewee.CharField()
    createDate= peewee.DateTimeField(default=datetime.now())


def initDbModels():
    """在启动时调用此方法，完成表结构初始化"""

    if False == User.table_exists():
        User.create_table()
        admin = User(username="admin", password="admin123", nickname="administrator", email="admin@126.com" )
        admin.save()

    if False == InformationModel.table_exists():
        InformationModel.create_table()




