from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime as dt
import os

try:
    from .solo_settings import solo_path, base_path, name_base_path, mail_set_base_path
except:
    from solo_settings import solo_path, base_path, name_base_path, mail_set_base_path


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

    def __init__(self, code, collection_id=int(), motive=True):
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
        

class Table_row:
    def __init__(self, vcode, number='', consig=''):
        self.vcode = vcode
        self.consig = consig
        self.number = number
        self.collection = ''
        self.comment = ''
        

Name_Base = declarative_base()


class VCodeName(Name_Base):
    __tablename__ = "names_vendor_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    collection_id = Column(Integer, ForeignKey("collections_factory.id"))
    name = Column(String)

    def __init__(self, code, collection_id=int(), name=''):
        self.code = code
        if collection_id:
            self.collection_id = collection_id
        if name:
            self.name = name


class Collection_Factory(Name_Base):
    __tablename__ = "collections_factory"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    boxes = Column(Integer)
    vcodes = relationship("VCodeName", backref='collection')
    factory_id = Column(Integer, ForeignKey("factories.id"))

    def __init__(self, name, boxes=1, factory_id=int()):
        self.name = name
        if boxes:
            self.boxes = boxes

        if factory_id:
            self.factory_id = factory_id


class Factory(Name_Base):
    __tablename__ = "factories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    actual = Column(Boolean, default=False)
    collections = relationship("Collection_Factory", backref='factory')

    def __init__(self, name):
        self.name = name
        

Mail_Base = declarative_base()


class MailAddress(Mail_Base):
    __tablename__ = "mail_addresses"

    id = Column(Integer, primary_key=True)


# check exist and create sqlite3 basefile
def check_bd_file(path_to_basefile, base_class):
    if not os.path.exists(path_to_basefile):
        engine = create_engine('sqlite:///%s' % path_to_basefile, echo=False)
        base_class.metadata.create_all(bind=engine)


base_dict = {
    base_path: Base,
    name_base_path: Name_Base,
    mail_set_base_path: Mail_Base,
}
for path, base_cls in base_dict.items():
    check_bd_file(path, base_cls)


class SoloUser(models.Model):

    user_id = models.IntegerField(unique=True, null=True)
    # email = models.EmailField(_('email address'), blank=True)

    is_solo_user = models.BooleanField(
        _('solo staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this solo tables site.'),
    )
    is_solo_admin = models.BooleanField(default=False)

