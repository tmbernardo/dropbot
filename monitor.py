from lxml import html
from fbpage import page
from flask import Flask, request
from proxy_requests import ProxyRequests

import os
import time
import requests
import dbhandler as db

def notify(new, restock):
    if new:
        for user in db.get_table("Users", "fb_id"):
            page.send(user, "NEW ITEMS\n"+"\n".join(new))
        print("Notified all users")
    
    for sub in restock.keys():
        page.send(sub, "RESTOCK:\n"+"\n".join(restock[sub]))

def get_current():
    site = ProxyRequests("https://acrnm.com")

    while(True):
        print("Checking if new products are on ACRNM on proxy: {}".format(site.proxy_used))
        site.get()
        tree = html.fromstring(str(site))
        products = tree.xpath('//div[@class="name"]/text()')

        new, restock = db.new_items(products)
        notify(new, restock)
        
        if new:
            db.insert_products(new)
        if new or restock:
            db.insert_current(products)
        
        time.sleep(1)

if  __name__ == "__main__":
    db.create_tables()
    get_current()
