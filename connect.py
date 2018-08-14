#!/usr/bin/python
 
import psycopg2
import dbhandler as db
 

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            fb_id VARCHAR(255) NOT NULL UNIQUE
        )
        """,
        """
        CREATE TABLE products (
            prod_id SERIAL PRIMARY KEY,
            prod_name VARCHAR(255) NOT NULL UNIQUE
        )
        """,
        """ 
        CREATE TABLE dictionary (
            prod_id VARCHAR(255) NOT NULL,
            user_id VARCHAR(255) NOT NULL
        )
        """
        )
    conn = None
    try:
        # read the connection parameters
        params = db.config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def drop_table(table):
    cmd = "DROP TABLE {}".format(table)
    db.execute_cmd(cmd)

def create_table():
    cmd = "CREATE TABLE users (user_id SERIAL PRIMARY KEY, fb_id VARCHAR(255) NOT NULL)"
    db.execute_cmd(cmd)

# create_tables()
# create_table()
# drop_table("users")
# drop_table("products")
# drop_table("dictionary")
lst = ["fdjsaklfdsa", "rewroew", "rieqopreqw", "fdjsaklfdsa"]
db.insert_list("users","fb_id", lst)

u = db.get_table("fb_id", "users")
print(u)

db.insert("users", "fb_id", "fdjsaklfdsa")

u = db.get_table("fb_id", "users")
print(u)

