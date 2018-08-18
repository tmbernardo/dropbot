from fbpage import page
import dbhandler as db
import os
from fbmq import QuickReply, Template

page.greeting("Click Get Started below to subscribe!!")

def show_persistent_menu(sender_id):
    page.show_persistent_menu([Template.ButtonPostBack('Unsubscribe', 'MENU_PAYLOAD/Unsubscribe')])
    return "Done with persistent menu section"

@page.handle_postback
def received_postback(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_postback = event.timestamp
    # show_persistent_menu(sender_id)

    payload = event.payload

    if(payload == "SUBSCRIBE"):
        db.insert("users","fb_id",sender_id)
        page.send(sender_id, "Subbed ur bitchass")

    elif(payload == "MENU_PAYLOAD/Unsubscribe"):
        db.delete_row("users", "fb_id", sender_id)
        print("trying to delete")
        page.send(sender_id, "Unsubbed ur bitchass")

    print("Received postback for user %s and page %s with payload '%s' at %s"
          % (sender_id, recipient_id, payload, time_of_postback))

@page.handle_message
def message_handler(event): 
    # get whatever message a user sent the bot
    page.send(event.sender_id, "\n".join(db.get_table("prod_name", "products")))
    return "Message Processed"

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
