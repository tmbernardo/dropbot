from fbpage import page
from fbmq import QuickReply, Template

import os
import dbhandler as db

page.greeting("Click Get Started below to subscribe!!")
page.show_starting_button("Subscribe")

menu_buttons = [
        Template.ButtonPostBack("My Subscriptions", "Subs"),
        Template.ButtonPostBack("Current Products", "Products"),
        Template.ButtonPostBack("Remove Notification", "Remove"),
]

sub_btn = [
        Template.ButtonPostBack("Unsubscribe", "Unsub")
]

quick_replies = [
        QuickReply(title="Yes, resubscribe", payload="Yes_r"),
        QuickReply(title="No", payload="No")        
]

def handle_unsub(sender_id):
    page.send(sender_id, "You are unsubscribed, do you want to resubscribe?", quick_replies=quick_replies)

@page.handle_postback
def received_postback(event):    
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_postback = event.timestamp
    payload = event.payload

    page.typing_on(sender_id)

    if(payload == "Subscribe"):
        if db.insert_user(sender_id):
            page.send(sender_id, "Subbed to all products")
            page.send(sender_id, Template.Buttons("Menu", [button for button in menu_buttons]))
            page.send(sender_id, Template.Buttons("------------------------------", [button for button in sub_btn]))
        else:
            page.send(sender_id, "Already subscribed")

    page.typing_off(sender_id)
    
    # print("Received postback for user %s and page %s with payload '%s' at %s"
    #       % (sender_id, recipient_id, payload, time_of_postback))

@page.handle_message
def message_handler(event):
    sender_id = event.sender_id
    message = event.message['text']
    state = db.get_state(sender_id)
    
    if(state == 0):
        if(message.lower() == "unsubscribe"):
            db.delete_user(sender_id)
            page.send(sender_id, "Unsubbed, you may now delete the conversation")
        else:
            page.send(sender_id, Template.Buttons("Menu", [button for button in menu_buttons]))
            page.send(sender_id, Template.Buttons("------------------------------", [button for button in sub_btn]))
    elif(state == 1):
        deleted = db.delete_sub(sender_id, message)
        if(deleted):
            page.send(sender_id, "Deleted your item")
        else:
            page.send(sender_id, "Item not found (product name not exact or you are already unsubscribed to this product)")
        db.change_state(sender_id, 0)

    return "Message processed"

@page.handle_delivery
def received_delivery_confirmation(event):
    delivery = event.delivery
    message_ids = delivery.get("mids")
    watermark = delivery.get("watermark")

    # if message_ids:
    #     for message_id in message_ids:
            # print("Received delivery confirmation for message ID: %s" % message_id)

    # print("All message before %s were delivered." % watermark)

@page.handle_read
def received_message_read(event):
    watermark = event.read.get("watermark")
    seq = event.read.get("seq")
    # print("Received message read event for watermark %s and sequence number %s" % (watermark, seq))

@page.callback(['Subs'])
def callback_clicked_subs(payload, event):
    sender_id = event.sender_id
    subs = db.get_subscriptions(sender_id)
    if subs:
        page.send(sender_id, "YOUR SUBS:\n"+"\n".join(subs))
    else:
        handle_unsub(sender_id)

@page.callback(['Products'])
def callback_clicked_prods(payload, event):
    page.send(event.sender_id, "CURRENT PRODUCTS:\n"+"\n".join(db.get_current()))

@page.callback(['Remove'])
def callback_clicked_rem(payload, event):
    sender_id = event.sender_id
    if db.change_state(sender_id, 1):
        page.send(sender_id, "Insert product name. Make sure name is exact (Press 'Current Products' to see product list)")
    else:
        handle_unsub(sender_id)

@page.callback(['Unsub'])
def callback_clicked_unsub(payload, event):
    sender_id = event.sender_id
    db.delete_user(sender_id)
    page.send(sender_id, "Unsubbed, you may now delete the conversation")

@page.callback(['Yes_r'])
def callback_clicked_yes_r(payload, event):
    sender_id = event.sender_id
    db.insert_user(sender_id)
    page.send(sender_id, "Subbed to all products")

@page.callback(['No'])
def callback_clicked_no_r(payload, event):
    pass
