from lxml import html
#from fbpage import page
from flask import Flask, request
import os
import time
import requests
import dbhandler as db

seconds = 15

def notify_all(new):
    for user in db.get_table("Users", "fb_id"):
        page.send(user, "\n".join(new))
    print("All users notified")

def get_current():
    while(True):
        print("Checking if new products are on ACRNM")
        page = requests.get('http://acrnm.com')
        tree = html.fromstring(page.content)

        # create a list of products:
        products = set(tree.xpath('//div[@class="name"]/text()'))
#         old_prods = set(db.get_table("Products","prod_name"))
        
#         if len(old_prods)<1:
#             db.insert_products(products)
#         elif products != old_prods:
#             diff = list(products.difference(old_prods))
# #            notify_all(diff)
#             db.insert_products(diff)
        new, restock = db.new_items(products)
        if new:
            notify_all(new)
            db.insert_products(new)
        if restock:
            for re in restock:
                for sub in re.subscribers.all():
                    page.send(sub.fb_id, re.prod_name)

        db.insert_current(new)

        time.sleep(seconds)

if  __name__ == "__main__":
    db.create_tables()
    get_current()
