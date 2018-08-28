from lxml import html
from fbpage import page
from flask import Flask, request
import os
import time
import requests
import dbhandler as db
import proxy_requests as pr

def notify(new, restock):
    if new:
        for user in db.get_table("Users", "fb_id"):
            page.send(user, "NEW ITEMS\n"+"\n".join(new))
        print("Notified all users")
    
    for sub in restock.keys():
        page.send(sub, "RESTOCK:\n"+"\n".join(restock[sub]))

def get_current():
    while(True):
        print("Checking if new products are on ACRNM")
        site = pr.ProxyRequests("https://acrnm.com")
        site.get()
        tree = html.fromstring(str(site))
        # create a list of products from the website
        products = tree.xpath('//div[@class="name"]/text()')

        new, restock = db.new_items(products)
        notify(new, restock)
        
        if new:
            db.insert_products(new)
        if new or restock:
            db.insert_current(products)

if  __name__ == "__main__":
    db.create_tables()
    get_current()
