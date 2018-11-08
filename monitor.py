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
        page.send(sub, "RESTOCK:\n"+"\n".join(list(zip(*restock[sub]))[1]))

def alt_current(url, site, store_name, ppath, upath, prod_names, prod_urls):
    print("Checking if new products are on {} on proxy: {}".format(store_name, site.proxy_used))
    if not site.get().ok:
        print("Proxy or website is unresponsive. Trying again...")
        site.proxy_used = site.sockets.pop(0)
        return False
    
    tree = html.fromstring(str(site))
    tree.make_links_absolute(url)

    prod_names.extend([store_name+pname.split() for pname in tree.xpath(ppath)])
    prod_urls.extend(tree.xpath(upath))

    return True

def get_current():
    url = "https://acrnm.com"
    site = ProxyRequests(url)
    
    failures = 0

    while True:

        print("Checking if new products are on ACRNM on proxy: {}".format(site.proxy_used))
        if not site.get().ok:
            print("Proxy or website is unresponsive. Trying again...")
            failures += 1
            site.proxy_used = site.sockets.pop(0)
            continue
        else:
            failures = 0
        
        tree = html.fromstring(str(site))
        tree.make_links_absolute(url)

        prod_names = tree.xpath("//div[@class='name']/text()")
        prod_urls = tree.xpath("//a[contains(concat(' ', normalize-space(@class), ' '), ' tile ')]/@href")

        new, restock = db.new_items(prod_names, prod_urls)

        if new:
            new = list(zip(*new))
            notify(new[1], restock)
            db.insert_products(new[0])
        else:
            notify(new, restock)

        db.insert_current(prod_names, prod_urls)
                
if  __name__ == "__main__":
    db.create_tables()
    get_current()
