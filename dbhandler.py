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
    Session = sessionmaker(bind=engine, autocommit=False)
    return Session()

def create_tables():
    sess = start_sess()
    Base.metadata.create_all(engine)
    sess.commit()
    sess.close()

def user_exists():
    pass

def prod_exists():
    pass

def insert_products(vlist):
    sess = start_sess()
    prods = []
    users = get_object(Users)

    for v in vlist:
        product = Products(prod_name=v)
        product.subscribers.extend(users)
        prods.append(product)

    sess.add_all(prods)
    sess.commit()
    sess.close()

    return prods

def insert_users(vlist):
    sess = start_sess()
    users = []
    products = get_object(Products)
    
    for v in vlist:
        user = Users(fb_id=v)
        user.subscriptions.extend(products)
        users.append(user)
    
    sess.add_all(users)
    sess.commit()
    sess.close()

def insert_current(vlist):
    sess = start_sess()

    sess.close()

def get_current():
    sess = start_sess()
    current = sess.query(Products.name).join(Current).all()
    return list(zip(*results))[0]

def get_object(table):
    sess = start_sess()
    results = sess.query(table).all()
    sess.close()
    return results

def get_table(table, column):
    sess = start_sess()
    results = sess.query(getattr(table_dict[table],column)).all()
    sess.close()
    return  [] if len(results)==0 else list(zip(*results))[0]

def delete_user(fb_id):
    """ delete entry and associations by fb_id
    TODO: try catch if fb_id is not found
    """
    sess = start_sess()
    user = sess.query(Users).filter(Users.fb_id==fb_id).first()
    user.subscriptions.clear()
    sess.delete(user)
    sess.commit()
    sess.close()

def delete_sub(fb_id, prod_name):
    pass
