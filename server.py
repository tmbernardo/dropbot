from flask import Flask, request
from monitor import get_current
from dbhandler import create_tables
from messenger import page
import messenger
import os

app = Flask(__name__)

VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

@app.route('/webhook', methods=['GET'])
def validate():
    if request.args.get('hub.mode', '') == 'subscribe' and \
                    request.args.get('hub.verify_token', '') == VERIFY_TOKEN:

        print("Validating webhook")

        return request.args.get('hub.challenge', '')
    else:
        return 'Failed validation. Make sure the validation tokens match.'

@app.route('/webhook', methods=['POST'])
def webhook():
  page.handle_webhook(request.get_data(as_text=True))
  return "ok"

def apprun():
    app.run(threaded=True)

if __name__ == "__main__":
    q.enqueue(create_tables)
    q.enqueue(get_current)
    q.enqueue(apprun)
