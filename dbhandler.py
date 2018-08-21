#!/usr/bin/python
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

import os
import psycopg2
import sqlalchemy

DATABASE_URL = os.environ['DATABASE_URL']
Base = declarative_base()

def connect(user, password, db, host='localhost', port=5432):
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con, reflect=True)
    Base = declarative_base()

    return con, meta

class User(Base):
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


def create_tables(con):
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
        con.execute(cmd)


def insert(table, column ,value):
    """ insert a new value into a table """
    cmd = """INSERT INTO {}({}) VALUES('{}') ON CONFLICT ({}) DO NOTHING;""".format(table, column, value, column)
    # cmd = "{}.insert().values({}={})".format(table, column, value)
    # cmd = cmd.on_conflict_do_nothing(index_elements=[column])
    # con.execute(cmd)
    execute_cmd(cmd)

def insert_list(table, column, vlist):
    """ insert multiple entries into a table  """
    lst = []
    for i in range(len(vlist)):
        e = (vlist[i], )
        lst.append(e)
    
    cmd = "INSERT INTO {} ({}) VALUES (%s) ON CONFLICT ({}) DO NOTHING".format(table, column, column)
    # cmd = "meta.tables[{}].insert()".format(table)
    # cmd = cmd.on_conflict_do_nothing(index_elements=[column])
    # con.execute(cmd, lst)
    execute_cmd(cmd, execmany=True, valuelist=lst)

def delete_row(table, column, ID):
    """ delete entry by id """
    cmd = "DELETE FROM {} WHERE {} = {}".format(table, column, ID)
    # cmd = "{}.query.filter_by({}={}).delete()".format(table, column, ID)
    # cmd.execute()
    return execute_cmd(cmd, True)

def get_table(ID, table):
    """ query data from a table """
    conn = None
    l = []
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute("SELECT {} FROM {}".format(ID, table))
        row = cur.fetchone()
 
        while row is not None:
            l.append(row[0])
            row = cur.fetchone()
 
        cur.close()

        # for row in con.execute("{}.select()".format(table)):
        #     l.append(row[0])

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        return l
