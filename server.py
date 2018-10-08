from fbpage import page
from flask import Flask, request

import os
import messenger

app = Flask(__name__)

VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

@app.before_first_request
def _run_on_start():
    messenger.p_menu()

@app.route('/webhook', methods=['GET'])
def validate():
    if request.args.get('hub.mode', '') == 'subscribe' and \
        request.args.get('hub.verify_token', '') == VERIFY_TOKEN:
        # print("Validating webhook")
        return request.args.get('hub.challenge', '')
    else:
        return 'Failed validation. Make sure the validation tokens match.'

@app.route('/webhook', methods=['POST'])
def webhook():
  page.handle_webhook(request.get_data(as_text=True))
  return "ok"

if __name__ == "__main__":
    app.run(threaded=True)
