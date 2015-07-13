from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine, Column, Integer, String, Date, Table, \
    ForeignKey, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import settings

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))

def create_deals_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class RFP(DeclarativeBase):
    __tablename__ = 'rfps'

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    URL = Column('URL', String)
    posted = Column('posted', Date, nullable=True)
    response_due = Column('response_due', Date, nullable=True)
    classification_code = Column('classification_code', String, nullable=True)
    NAICS_code = Column('NAISC_code', String, nullable=True)
    set_aside_code = Column('set_aside_code', String, nullable=True)
    contracting_office_address = Column('contracting_office_address', String,
                                        nullable=True)
    description = Column('description', Text, nullable=True)
    point_of_contact = relationship('PointOfContact', secondary='rfp_contacts',
                                    backref='RFP')

class PointOfContact(DeclarativeBase):
    __tablename__ = 'points_of_contact'

    id = Column(Integer, primary_key=True)
    name = Column('name', String, unique=True)
    title = Column('title', String, nullable=True)
    phone = Column('phone', String, nullable=True)
    fax = Column('fax', String, nullable=True)
    email = Column('email', String, nullable=True)
    rfp = relationship(RFP, secondary='rfp_contacts', backref='PointOfContact')


class RFP_contacts(DeclarativeBase):
    __tablename__ = 'rfp_contacts'

    id = Column(Integer, primary_key=True)
    rfp_id = Column(Integer, ForeignKey('rfps.id'))
    contact_id = Column(Integer, ForeignKey('points_of_contact.id'))
