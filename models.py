# from django.db import models

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime as dt
import os

try:
    from .solo_settings import solo_path, base_path
except:
    from solo_settings import solo_path, base_path



# base_path = os.getcwd() + r"/base.bd")

def path_for_old_base(update_time=False):
    dt_now = dt.now()
    # dt_now_str = f"{dt_now.year}-{dt_now.mounth}-{dt_now.day}-{dt_now.hour}-{dt_now.minute}"
    dt_now_str = "-".join([str(dt_now.year), str(dt_now.month), str(dt_now.day), str(dt_now.hour), str(dt_now.minute)])
    if update_time:
        with open("last_update_time.txt", "w") as f:
            f.write(dt_now_str)
    return solo_path + r'old_bases/base{}.bd'.format(dt_now_str)


Base = declarative_base()


class VCode(Base):
    __tablename__ = "vendor_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    consigments = relationship("Consigment", backref='vendor_code')
    collection_id = Column(String, ForeignKey("collections.id"))
    motive = Column(Boolean)

    def __init__(self, code, collection_id=int(), motive=Boolean()):
        self.code = code
        if collection_id:
            self.collection_id = collection_id
        if motive:
            self.motive = motive


class Paired_vcode(Base):
    __tablename__ = "paired_vcodes"
    id = Column(Integer, primary_key=True)
    code_id = Column(String, ForeignKey("vendor_codes.id"))
    paired_ids = relationship("VCode", backref='paired_vcodes')

    def __init__(self, code_id, paired_ids):
        self.code_id = code_id
        self.paired_ids = paired_ids


class Consigment(Base):
    __tablename__ = "consigments"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    vcode_id = Column(String, ForeignKey("vendor_codes.id"))
    amount = Column(Integer, nullable=False, default=0)
    # vendor_code = relationship("VCode", backref='consigments')

    def __init__(self, name, vcode, amount):
        self.name = name
        self.vcode_id = vcode
        self.amount = amount


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    boxes = Column(Integer)
    vcodes = relationship("VCode", backref='collection')

    def __init__(self, name, boxes=1):
        self.name = name
        if boxes:
            self.boxes = boxes
        


if not os.path.exists(base_path):
    engine = create_engine('sqlite:///%s' % base_path, echo=False)
    Base.metadata.create_all(bind=engine)


class Table_row:
    def __init__(self, vcode, number='', consig=''):
        self.vcode = vcode
        self.consig = consig
        self.number = number
        self.collection = ''
        self.comment = ''
        
