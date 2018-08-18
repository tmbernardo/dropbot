#!/usr/bin/python
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship

import os
import psycopg2
import sqlalchemy

DATABASE_URL = os.environ['DATABASE_URL']

# def connect(user, password, db, host='localhost', port=5432):
#     '''Returns a connection and a metadata object'''
#     # We connect with the help of the PostgreSQL URL
#     # postgresql://federer:grandestslam@localhost:5432/tennis
#     url = 'postgresql://{}:{}@{}:{}/{}'
#     url = url.format(user, password, host, port, db)

#     # The return value of create_engine() is our connection object
#     con = sqlalchemy.create_engine(url, client_encoding='utf8')

#     # We then bind the connection to MetaData()
#     meta = sqlalchemy.MetaData(bind=con, reflect=True)
#     Base = declarative_base()

#     return con, meta

# class User(Base):
#     __tablename__ = 'users'
#     user_id = Column(String, primary_key=True)
#     fb_id = Column(BigInteger, nullable=False, unique=True)

# class Product(Base):
#     __tablename__ = 'products'
#     prod_id = Column(String, primary_key=True)
#     prod_name = Column(String, nullable=False, unique=True)

# class Subscription(Base):
#     __tablename__ = 'subscriptions'
#     prod_id = Column(Integer, ForeignKey('products.prod_id'))
#     user_id = Column(Integer, ForeignKey('users.user_id'))
#     product = relationship("Product", foreign_keys=[prod_id])
#     user = relationship("User", foreign_keys=[user_id])

# class Current(Base):
#     __tablename__ = 'current'
#     prod_id = Column(Integer, ForeignKey('products.prod_id'))
#     product = relationship("Product", foreign_keys=[prod_id])

def execute_cmd(command, rowcount=False, execmany=False, valuelist=False):
    """ executes sql command """
    rv = None
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        if not execmany:
            # execute one command
            cur.execute(command)
        else:
            # execute many
            cur.executemany(command, valuelist)
        # returns rowcount if rowcount is true
        rv = True if rowcount else False
        # commit the changes
        conn.commit()
        # close communication with the PostgreSQL database server
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def create_tables():
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
    
    # if not con.dialect.has_table(con, 'users'):
    #     users = Table('users', meta,
    #     Column('user_id', String, primary_key=True),
    #     Column('fb_id', BigInteger, nullable=False, unique=True)
    #     )

    # if not con.dialect.has_table(con, 'products'):
    #     products = Table('products', meta,
    #     Column('prod_id', String, primary_key=True),
    #     Column('prod_name', String, nullable=False, unique=True)
    #     )

    # if not con.dialect.has_table(con, 'subscriptions'):
    #     subscriptions = Table('subscriptions,', meta,
    #     Column('prod_id', Integer, ForeignKey('products.prod_id')),
    #     Column('user_id', Integer, ForeignKey('users.user_id'))
    #     )

    # if not con.dialect.has_table(con, 'current'):
    #     current = Table('current', meta,
    #     Column('prod_id', Integer, ForeignKey('products.prod_id'))
    #     )

    # meta.create_all(con)

    for cmd in cmds:
        execute_cmd(cmd)


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
