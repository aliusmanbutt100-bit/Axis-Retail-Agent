#i tried very hard but this method dont work and i cant do live with this method bcz of meta publish requiremenyt and this file is just to show that i work or learn these things also
#This is to connect our this project with whatsapp using meta developers.com with help of flask
from main import get_agent_response
from flask import Flask, request
#ik alag terminal mei( ngrok http 5000 ) chala lena or dosry mei app.py run karna and jo forwarding mei url mily ga ngrok terminal mei wo dalna meta developers ky webhook mei
app = Flask(__name__)

VERIFY_TOKEN = "myapp123"   # wahi jo .env mein rakha

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403
#Receive msg function
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        message = value["messages"][0]

        sender_number = message["from"]
        message_text = message["text"]["body"]

        # Agent se jawab liya, thread_id = customer ka number
        reply = get_agent_response(message_text, sender_number)

        # Jawab WhatsApp pe wapis bheja
        send_whatsapp_message(sender_number, reply)

    except (KeyError, IndexError):
        pass

    return "OK", 200
#Function to send msg on whatsapp
import requests
import os
from dotenv import load_dotenv
load_dotenv
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

def send_whatsapp_message(to: str, message: str):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)
if __name__ == "__main__":
    app.run(port=5000, debug=True)