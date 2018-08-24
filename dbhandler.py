#!/usr/bin/python
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey, Sequence
from sqlalchemy.orm import joinedload, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os
import psycopg2
import sqlalchemy as sql

Base = declarative_base()

#url = os.environ['DATABASE_URL']
url="postgres://bjihtaefdfdzxn:5d519eff130605f764b523746a4b919e9f1b521c794a1c013f55375ce01a4463@ec2-50-16-196-138.compute-1.amazonaws.com:5432/d8k7t1e86358jk"
engine = sql.create_engine(url, pool_size=17, client_encoding='utf8')

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    fb_id = Column(BigInteger, nullable=False, unique=True)
    subscriptions = relationship('Products', secondary='subscriptions', backref=sql.orm.backref('subscribers', lazy='dynamic'))

class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    prod_name = Column(String, nullable=False, unique=True)

class Subs(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    prod_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

class Current(Base):
    __tablename__ = "current"
    id = Column(Integer, primary_key=True)
    prod_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    product = relationship('Products', uselist=False)

table_dict = {
        "Users": Users,
        "Products": Products,
        "Subscriptions": Subs,
        "Current": Current
        }

def start_sess():
    Session = sessionmaker(bind=engine, autocommit=True)
    return Session()

def create_tables():
    Base.metadata.create_all(engine)

def insert_list(table, column, vlist):
    """ insert multiple entries into a table  """
    sess = start_sess()
    objects = []
    table = table_dict[table]
    
    for v in vlist:
        row = table()
        setattr(row, column, v)
        objects.append(row)
    sess.bulk_save_objects(objects)
    sess.close()

def delete_row(table, column, ID):
    """ delete entry by id """
    sess = start_sess()
    table = table_dict[table]
    sess.query(table).filter(getattr(table,column)==ID).delete()
    sess.close()

def get_join(table1, column1, table2, column2):
    """ query data from a table """
    sess = start_sess()
    query = sess.query(table1).options(
            joinedload(getattr(table1,column1), innerjoin=True)\
                    .joinedload(getattr(table2,column2), innerjoin=True))
    results = query.all()
    sess.close()
    return results

def get_current():
    sess = start_sess()
    query = sess.query(Current).options(
            joinedload(Current.prod_id, innerjoin=True)\
                    .joinedload(Products.prod_id, innerjoin=True))
    results = query.all()
    sess.close()
    return results

def get_table(table, column):
    sess = start_sess()
    results = sess.query(getattr(table_dict[table],column)).all()
    sess.close()
    return list(zip(*results))[0] if results == None else []

