from flask import Flask, request
from pymessenger.bot import Bot
from lxml import html
import requests
import time

seconds = 1
products = []

app = Flask(__name__)
with open('access-token.txt', 'r') as access_file:
    access = access_file.read().replace('\n', '')
with open('verify-token.txt', 'r') as verify_file:
    verify = verify_file.read().replace('\n', '')
ACCESS_TOKEN = access
VERIFY_TOKEN = verify
bot = Bot(ACCESS_TOKEN)

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
        products = get_products()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    #Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        send_message(recipient_id, products)
                    #if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        send_message(recipient_id, product)
        return "Message Processed"

def get_products():
    page = requests.get('http://acrnm.com')
    tree = html.fromstring(page.content)

    # create a list of products:
    cur_products = tree.xpath('//div[@class="name"]/text()')
    return cur_products
    # if(products != cur_products):
    #     products = cur_products
    #     # send notification to messenger

    # # time.sleep(seconds)
    # print(products)

def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def send_message(recipient_id, products):
    #sends user the text message provided via input response parameter
    response = ""
    for product in products:
        response += product + '\n'
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == '__main__':
    app.run()

