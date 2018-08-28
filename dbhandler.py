#!/usr/bin/python
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey, Sequence
from sqlalchemy.orm import joinedload, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os
import psycopg2
import sqlalchemy as sql

Base = declarative_base()

#heroku pg:psql -a acrbot
#import dburl
url = os.environ['DATABASE_URL']
engine = sql.create_engine(url, pool_size=17, client_encoding='utf8')

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    fb_id = Column(BigInteger, nullable=False, unique=True)
    state = Column(Integer, nullable=False, default=0)
    subscriptions = relationship('Products', secondary='subscriptions', backref=sql.orm.backref('subscribers', lazy='dynamic'))

class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    prod_name = Column(String, nullable=False, unique=True)
    
    def __eq__(self, other):
        return self.prod_name == other.prod_name

class Subs(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    prod_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

class Current(Base):
    __tablename__ = "current"
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

def user_exists(user, sess):
    return sess.query(Users).filter(Users.fb_id==user).scalar()

def prod_exists(prod, sess):
    return sess.query(Products).filter(Products.prod_name==prod).scalar()

def current_exists(prod_name, sess):
    return sess.query(Current).filter(Current.product.has(Products.prod_name==prod_name)).scalar()

def new_items(vlist):
    new = []
    restock = {}
    sess = start_sess()

    for v in vlist:
        prod = prod_exists(v,sess)
        cur = current_exists(v,sess)
        if not prod:
            new.append(v)
        if prod and (not cur):
            for sub in prod.subscribers:
                restock.setdefault(sub.fb_id, []).append(v)

    sess.close()
    return new, restock

def insert_products(vlist):
    sess = start_sess()
    prods = []
    users = get_object(Users, sess)

    for v in vlist:
        product = Products(prod_name=v)
        product.subscribers.extend(users)
        prods.append(product)

    sess.add_all(prods)
    sess.commit()
    sess.close()

    return prods

def insert_user(value):
    sess = start_sess()
    products = get_object(Products, sess)
    
    user = Users(fb_id=value)
    user.subscriptions.extend(products)
    
    sess.add(user)
    sess.commit()
    sess.close()
    return True

def insert_current(vlist):
    sess = start_sess()
    prods = []

    sess.query(Current).delete()

    for v in vlist:
        prod = get_product(v, sess)
        curr = Current()
        curr.product = prod
        prods.append(curr)

    sess.add_all(prods)
    sess.commit()
    sess.close()

""" Private getters """
def get_subscribers(prod, sess):
    p = sess.query(Products).filter(Products==prod).first()
    rv = p.subscribers.all()
    return rv

def get_product(prod, sess):
    return sess.query(Products).filter(Products.prod_name==prod).first()

def get_object(table, sess):
    results = sess.query(table).all()
    return results

""" Public getters """
def get_current():
    sess = start_sess()
    current = sess.query(Products.prod_name).join(Current).all()
    sess.close()
    return list(zip(*current))[0]

def get_table(table, column):
    sess = start_sess()
    results = sess.query(getattr(table_dict[table],column)).all()
    sess.close()
    return [] if len(results)==0 else list(zip(*results))[0]

def get_state(fb_id):
    sess = start_sess()
    user = sess.query(Users).filter(Users.fb_id==fb_id).first() 
    rv = user.id
    sess.close()
    return rv

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

def change_state(fb_id, state):
    sess = start_sess()
    if(user_exists(fb_id, sess)):
        user = sess.query(Users).filter(Users.fb_id==fb_id).first() 
        user.state = state
        sess.commit()
        sess.close()
        return True
    sess.close()
    return False

def delete_sub(fb_id, prod_name):
    sess = start_sess()

    prod = prod_exists(prod_name, sess)
    
    if not prod:
        sess.close()
        return False

    print(prod.prod_name)

    user = sess.query(Users).filter(Users.fb_id==fb_id).first()
    for x in user.subscriptions:
        print(x.prod_name)
    user.subscriptions.remove(prod)
    sess.commit()
    sess.close()

    return True
