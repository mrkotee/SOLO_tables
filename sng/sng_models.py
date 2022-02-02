
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime as dt
import os
try:
    from solo_settings import sng_base_path
except:
    from solo.solo_settings import sng_base_path


# base_filename = "sng_base.bd"
# base_path = os.path.join(os.getcwd(), base_filename)
base_path = sng_base_path


Base = declarative_base()

association_table = Table(
    'associacion', Base.metadata,
    Column('client_id', Integer, ForeignKey('clients.id')),
    Column('name_id', Integer, ForeignKey('code_names.id'))
)


class VCode(Base):
    __tablename__ = "vendor_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    names = relationship("CodeName", backref='vendor_code')

    def __init__(self, code):
        self.code = code


class CodeName(Base):
    __tablename__ = "code_names"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    vcode_id = Column(Integer, ForeignKey("vendor_codes.id"))
    clients = relationship("Client", secondary=association_table, back_populates='code_names')

    def __init__(self, name, vcode_id, client=False):
        self.name = name
        self.vcode_id = vcode_id
        if client:
            self.clients = client


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code_names = relationship("CodeName", secondary=association_table, back_populates='clients')

    def __init__(self, name):
        self.name = name


class Clients_row():

    def __init__(self, id, name):
        self.id = id
        self.name = name
        


if not os.path.exists(base_path):
    engine = create_engine('sqlite:///%s' % base_path, echo=False)
    Base.metadata.create_all(bind=engine)
