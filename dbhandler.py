#!/usr/bin/python
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

import os
import psycopg2
import sqlalchemy

Base = declarative_base()

url = os.environ['DATABASE_URL']
con = sqlalchemy.create_engine(url, client_encoding='utf8')
Session = sessionmaker(bind=con, autocommit=True)
session = Session()

class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    fb_id = Column(BigInteger, nullable=False, unique=True)

class Product(Base):
    __tablename__ = 'products'
    prod_id = Column(Integer, Sequence('prod_id_seq'), primary_key=True)
    prod_name = Column(String, nullable=False, unique=True)

class Subscription(Base):
    __tablename__ = 'subscriptions'
    sub_id = Column(Integer, Sequence('sub_id_seq'), primary_key=True)
    prod_id = Column(Integer, ForeignKey('products.prod_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    product = relationship("Product", foreign_keys=[prod_id])
    user = relationship("User", foreign_keys=[user_id])

class Current(Base):
    __tablename__ = 'current'
    curr_id = Column(Integer, Sequence('curr_id_seq'), primary_key=True)
    prod_id = Column(Integer, ForeignKey('products.prod_id'))
    product = relationship("Product", foreign_keys=[prod_id])

table_dict = {
        "users": User,
        "products": Product,
        "subscriptions": Subscription,
        "current": Current
        }

def create_tables(sess):
    """ create tables in the PostgreSQL database"""
 
    cmds = (
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            fb_id BIGINT NOT NULL UNIQUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS products (
            prod_id SERIAL PRIMARY KEY,
            prod_name VARCHAR(255) NOT NULL UNIQUE
        )
        """,
        """ 
        CREATE TABLE IF NOT EXISTS subscription (
            prod_id integer,
            user_id integer,
            constraint fk_prod_id
                foreign key (prod_id)
                REFERENCES products (prod_id),
            constraint fk_user_id
                foreign key (user_id)
                REFERENCES users (user_id)
        )
        """,
        """ 
        CREATE TABLE IF NOT EXISTS current (
            prod_id integer,
            constraint fk_prod_id
                foreign key (prod_id)
                REFERENCES products (prod_id)
        )
        """
        )

    for cmd in cmds:
        sess.execute(cmd)

def insert_list(table, column, vlist):
    """ insert multiple entries into a table  """

    table = table_dict[table]
    # need to instantiate objects
    objects = [setattr(table, column,value) for value in vlist]
    sess.bulk_save_objects(objects)

def delete_row(table, column, ID):
    """ delete entry by id """
    table = table_dict[table]
    table.query.filter(table(getattr(column)=value)).delete()

def get_table(table1, column1, table2, column2):
    """ query data from a table """
    query = session.query(table1).options(
            joinedload(table1(getattr(column1)), innerjoin=True)\
                    .joinedload(table2(getattr(column2)), innerjoin=True))

    return query.all()
