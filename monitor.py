from lxml import html
from fbpage import page
from flask import Flask, request
import os
import time
import requests
import dbhandler as db

seconds = 15

def notify_all(new):
    for user in db.get_table("Users", "fb_id"):
        page.send(user, "NEW ITEMS\n"+"\n".join(new))
    print("All users notified")

def get_current():
    while(True):
        print("Checking if new products are on ACRNM")
        site = requests.get('http://acrnm.com')
        tree = html.fromstring(site.content)

        # create a list of products from the website
        products = set(tree.xpath('//div[@class="name"]/text()'))
        new, restock = db.new_items(products)
        
        if new:
            notify_all(new)
            db.insert_products(new)
        if restock:
            for sub in restock.keys():
                page.send(sub, "RESTOCK:\n"+"\n".join(restock[sub]))
        if new or restock:
            db.insert_current(products)

        time.sleep(seconds)

if  __name__ == "__main__":
    db.create_tables()
    get_current()
