from server import page
import dbhandler as db

@page.handle_message
def message_handler(event): 
    print("receive_message")
    # get whatever message a user sent the bot
    page.send(event.sender_id, "\n".join(db.get_table("prod_name", "products")))
    return "Message Processed"
