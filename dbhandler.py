#!/usr/bin/python
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey, Sequence
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os
import psycopg2
import sqlalchemy

Base = declarative_base()

#url = os.environ['DATABASE_URL']
url="postgres://bjihtaefdfdzxn:5d519eff130605f764b523746a4b919e9f1b521c794a1c013f55375ce01a4463@ec2-50-16-196-138.compute-1.amazonaws.com:5432/d8k7t1e86358jk"
engine = sqlalchemy.create_engine(url, client_encoding='utf8')
Session = sessionmaker(bind=engine, autocommit=True)
sess = Session()

class users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    fb_id = Column(BigInteger, nullable=False, unique=True)

class products(Base):
    __tablename__ = 'products'
    prod_id = Column(Integer, Sequence('prod_id_seq'), primary_key=True)
    prod_name = Column(String, nullable=False, unique=True)

class subscriptions(Base):
    __tablename__ = 'subscriptions'
    sub_id = Column(Integer, Sequence('sub_id_seq'), primary_key=True)
    prod_id = Column(Integer, ForeignKey('products.prod_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    products = relationship("products", foreign_keys=[prod_id])
    user = relationship("users", foreign_keys=[user_id])

class current(Base):
    __tablename__ = 'current'
    curr_id = Column(Integer, Sequence('curr_id_seq'), primary_key=True)
    prod_id = Column(Integer, ForeignKey('products.prod_id'))
    products = relationship("products", foreign_keys=[prod_id])

table_dict = {
        "users": users,
        "products": products,
        "subscriptions": subscriptions,
        "current": current
        }

def create_tables():
    Base.metadata.create_all(engine)

def insert_list(table, column, vlist):
    """ insert multiple entries into a table  """
    objects = []
    table = table_dict[table]
    
    for v in vlist:
        row = table()
        setattr(row, column, v)
        objects.append(row)
    sess.bulk_save_objects(objects)

def delete_row(table, column, ID):
    """ delete entry by id """
    table = table_dict[table]
    sess.query(table).filter(getattr(table,column)==ID).delete()

def get_join(table1, column1, table2, column2):
    """ query data from a table """
    query = sess.query(table1).options(
            joinedload(getattr(table1,column1), innerjoin=True)\
                    .joinedload(getattr(table2,column2), innerjoin=True))
    return query.all()

def get_table(table, column):
    return sess.query(getattr(table_dict[table],column)).all()

#insert_list('products','prod_name', ['asdf','asdffths','artbnbgtyhn','asdftrns'])
print(*get_table('products','prod_name'))
sess.close()
