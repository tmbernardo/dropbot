from fbpage import page
from fbmq import QuickReply, Template
import os
import dbhandler as db

page.greeting("Click Get Started below to subscribe!!")
page.show_starting_button("Subscribe")

pers_menu_btns = [
        "Current Products",
        "Remove notification",
        "Unsubscribe"
]

quick_replies = [
        QuickReply(title="Yes", payload="Yes"),
        QuickReply(title="No", payload="No")
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
        page.send(sender_id, "Subbed to all products.")
    
    elif(payload == "Current Products"):
        page.send(event.sender_id, "CURRENT PRODUCTS:\n"+"\n".join(db.get_current()))
    
    elif(payload == "Unsubscribe"):
        db.delete_row("users", "fb_id", sender_id)
        page.send(sender_id, "Unsubbed. You may now delete the conversation.")

    elif(payload == "Remove notification"):
        sender_id = event.sender_id
        db.change_state(sender_id, 1)
        page.send(sender_id, "Insert product name. Make sure name is exact, then send it back to me.")

    page.typing_off(sender_id)
    
    print("Received postback for user %s and page %s with payload '%s' at %s"
          % (sender_id, recipient_id, payload, time_of_postback))

@page.handle_message
def message_handler(event):
    sender_id = event.sender_id
    state = db.get_state(sender_id)
    if(state == 0):
        # get whatever message a user sent the bot
        page.send(sender_id, "CURRENT PRODUCTS:\n"+"\n".join(db.get_current()))
    else:
        product = event.payload
        deleted = db.delete_sub(sender_id, product)
        if(deleted):
            page.send(sender_id, "Deleted your item.")
        else:
            page.send(sender_id, "Error. Item not found.")
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
