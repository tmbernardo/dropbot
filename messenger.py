from fbpage import page
import dbhandler as db
import os

@page.handle_message
def message_handler(event): 
    print("receive_message")
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
