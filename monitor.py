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
    url = "https://acrnm.com"
    site = ProxyRequests(url)
    start_time = time.time()
    while(True):
        print("Checking if new products are on ACRNM on proxy: {}".format(site.proxy_used))
        site.get()
        tree = html.fromstring(str(site))
        tree.make_links_absolute(url)

        prod_names = tree.xpath("//div[@class='name']/text()")
        prod_urls = tree.xpath("//a[contains(concat(' ', normalize-space(@class), ' '), ' tile ')]/@href")
        new, restock = db.new_items(prod_names, prod_urls)
        new = list(zip(*new))[0]
        restock = list(zip(*restock))[0]
        notify(new, restock)
        
        if new:
            db.insert_products(new)
        if new or restock:
            db.insert_current(prod_names, prod_urls)
            
        time.sleep(1)

        if (time.time() - start_time)/60 > 25:
            print("Pinging the app")
            requests.get("https://acrbot.herokuapp.com/")
            start_time = time.time()
        

if  __name__ == "__main__":
    db.create_tables()
    get_current()
