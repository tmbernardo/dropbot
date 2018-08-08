from flask import Flask, request
from lxml import html
import requests
import time

seconds = 1
products = []
cur_products = []

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])

def receive_message():
    if request.method == 'GET':
        # before allowing people to message your bot, Facebook has implemented a verify token
        # that confirms all requests that your bot receives came from Facebook. 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    #Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        response_sent_text = get_message()
                        send_message(recipient_id, response_sent_text)
                    #if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_nontext = get_message()
                        send_message(recipient_id, response_sent_nontext)
        return "Message Processed"

def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    response = ""
    for product in products:
        response += product + '\n'
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == '__main__':
    app.run()

while(True):
    page = requests.get('http://acrnm.com')
    tree = html.fromstring(page.content)

    # create a list of products:
    cur_products = tree.xpath('//div[@class="name"]/text()')

    if(products != cur_products):
        products = cur_products
        # send notification to messenger

    # time.sleep(seconds)
    print(products)
