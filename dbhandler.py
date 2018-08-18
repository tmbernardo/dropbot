#!/usr/bin/python
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

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

    for cmd in cmds:
        execute_cmd(cmd)

def insert(table, column ,value):
    """ insert a new value into a table """
    cmd = """INSERT INTO {}({}) VALUES('{}') ON CONFLICT ({}) DO NOTHING;""".format(table, column, value, column)
    execute_cmd(cmd)

def insert_list(table, column, vlist):
    """ insert multiple entries into a table  """
    lst = []
    for i in range(len(vlist)):
        e = (vlist[i], )
        lst.append(e)
    
    cmd = "INSERT INTO {} ({}) VALUES (%s) ON CONFLICT ({}) DO NOTHING".format(table, column, column)
    execute_cmd(cmd, execmany=True, valuelist=lst)

def update_vendor(vendor_id, vendor_name):
    """ update name based on the id """
    cmd = """ UPDATE vendors
                SET vendor_name = %s
                WHERE vendor_id = %s""" 
    return execute_cmd(cmd, True)

def delete_row(table, column, ID):
    """ delete entry by id """
    cmd = "DELETE FROM {} WHERE {} = {}".format(table, column, ID)
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
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        return l
