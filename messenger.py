from fbpage import page
from fbmq import QuickReply, Template

import os
import dbhandler as db

page.greeting("Click Get Started below to subscribe!!")
page.show_starting_button("Subscribe")

pers_menu_btns = [
        "Commands",
        "Unsubscribe"
]

buttons = [
        Template.ButtonPostBack("My Subscriptions", "Subs"),
        Template.ButtonPostBack("Current Products", "Products"),
        Template.ButtonPostBack("Remove Notification", "Remove"),
]

def show_persistent_menu():
    page.show_persistent_menu([Template.ButtonPostBack(btn, btn) for btn in pers_menu_btns])
    return "Done with persistent menu section"

@page.handle_postback
def received_postback(event):
    show_persistent_menu()
    
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_postback = event.timestamp
    payload = event.payload

    page.typing_on(sender_id)

    if(payload == "Subscribe"):
        db.insert_user(sender_id)
        page.send(sender_id, "Subbed to all products")
    
    elif(payload == "Commands"):
        page.send(sender_id, Template.Buttons("User Commands", [button for button in buttons]))

    elif(payload == "Unsubscribe"):
        db.delete_user(sender_id)
        page.send(sender_id, "Unsubbed, you may now delete the conversation")

    page.typing_off(sender_id)
    
    print("Received postback for user %s and page %s with payload '%s' at %s"
          % (sender_id, recipient_id, payload, time_of_postback))

@page.handle_message
def message_handler(event):
    sender_id = event.sender_id
    state = db.get_state(sender_id)
    print(state)
    if(state == 0):
        # get whatever message a user sent the bot
        page.send(sender_id, "CURRENT PRODUCTS:\n"+"\n".join(db.get_current()))
    elif(state == 1):
        product = event.message['text']
        deleted = db.delete_sub(sender_id, product)
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

    if message_ids:
        for message_id in message_ids:
            print("Received delivery confirmation for message ID: %s" % message_id)

    print("All message before %s were delivered." % watermark)

@page.handle_read
def received_message_read(event):
    watermark = event.read.get("watermark")
    seq = event.read.get("seq")
    print("Received message read event for watermark %s and sequence number %s" % (watermark, seq))

@page.callback(['Subs'])
def callback_clicked_subs(payload, event):
    page.send(event.sender_id, "YOUR SUBS:\n"+"\n".join(db.get_subscriptions(event.sender_id)))

@page.callback(['Products'])
def callback_clicked_prods(payload, event):
    page.send(event.sender_id, "CURRENT PRODUCTS:\n"+"\n".join(db.get_current()))

@page.callback(['Remove'])
def callback_clicked_rem(payload, event):
    sender_id = event.sender_id
    db.change_state(sender_id, 1)
    page.send(sender_id, "Insert product name. Make sure name is exact (Press 'Current Products' to see product list)")
