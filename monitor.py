from flask import Flask, request
from lxml import html
from fbpage import page
import requests
import time
import dbhandler as db
import os

seconds = 30

def notify_all(cur_products):
    for user in db.get_table("user_id", "users"):
        page.send(user, "\n".join(cur_products))
    print("All users notified")

def get_current():
    while(True):
        page = requests.get('http://acrnm.com')
        tree = html.fromstring(page.content)

        # create a list of products:
        cur_products = tree.xpath('//div[@class="name"]/text()')
        if cur_products != db.get_table("prod_id","products"):
            notify_all(cur_products)
        db.insert_list("products", "prod_name", cur_products)
        time.sleep(seconds)

if  __name__ == "__main__":
    db.create_tables()
    get_current()
