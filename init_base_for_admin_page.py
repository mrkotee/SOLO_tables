
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from alchemy_models import Factory, VCodeName, Collection_Factory, MailAddress, Name_Base
from alchemy_models import check_bd_file
from solo_settings import name_base_path, mail_set_base_path
from m_settings import mail_list, marys_mail


def create_session(_base_path):
    engine = create_engine('sqlite:///%s' % _base_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

OldNameBase = declarative_base()
class OldFactory(OldNameBase):
    __tablename__ = "factories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    collections = relationship("Collection_Factory", backref='factory')

    def __init__(self, name):
        self.name = name


def add_mail_to_base():
    m_session = create_session(mail_set_base_path)

    for mail in mail_list:
        if m_session.query(MailAddress).filter(MailAddress.email == mail).first():
            continue
        m_session.add(MailAddress(mail))
    m_session.commit()
    for mail in marys_mail:
        if m_session.query(MailAddress).filter(MailAddress.email == mail).first():
            continue
        m_session.add(MailAddress(mail, marrys=True))
    m_session.commit()


def migrate_factory(old_session, new_session):
    old_objects = old_session.query(OldFactory).all()
    for obj in old_objects:
        new_session.add(Factory(name=obj.name))
    new_session.commit()


def migrate_collections(old_session, new_session):
    old_objects = old_session.query(Collection_Factory).all()
    for obj in old_objects:
        new_session.add(
            Collection_Factory(
                        name=obj.name,
                        boxes=obj.boxes,
                        factory_id=obj.factory_id,
            )
        )
    new_session.commit()


def migrate_vcodes(old_session, new_session):
    old_objects = old_session.query(VCodeName).all()
    for obj in old_objects:
        new_session.add(VCodeName(
            code=obj.code, collection_id=obj.collection_id, name=obj.name
        )
                        )
    new_session.commit()


def migrate_namebase():
    old_base_path = name_base_path + '.old'
    file_id = 0
    while os.path.exists(old_base_path):
        file_id += 1
        old_base_path += str(file_id)

    os.rename(name_base_path, old_base_path)

    check_bd_file(name_base_path, Name_Base)

    old_session = create_session(old_base_path)
    new_session = create_session(name_base_path)

    migrate_factory(old_session, new_session)

    migrate_collections(old_session, new_session)

    migrate_vcodes(old_session, new_session)


if __name__ == '__main__':
    add_mail_to_base()
    migrate_namebase()
