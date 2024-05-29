import os
import cv2
import requests
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slack import WebClient
import json
from slackeventsapi import SlackEventAdapter
from pymongo import MongoClient
import easyocr
import numpy as np

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize Flask app
app = Flask(__name__)

# Initialize MongoDB client
mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)
db = mongo_client.get_database("slack_genAI")
expenses_collection = db.get_collection("slack")

# Initialize Slack Event Adapter
slack_signing_secret = os.getenv("SIGNING_SECRET")
slack_events_adapter = SlackEventAdapter(
    slack_signing_secret, '/slack/events', app)

# Initialize Slack WebClient
slack_token = os.getenv("SLACK_TOKEN")
slack_client = WebClient(token=slack_token)

# Get bot ID
bot_id = slack_client.api_call("auth.test")['user_id']
print("botid")
print(bot_id)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Define Celery task for OCR processing


# def extract_text(image_data):
#     image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
#     extracted_text = reader.readtext(image)

#     return extract_text
lable = ["Food", "Travel", "Stay", "Electronics"]

url = "http://127.0.0.1:8000/predict"


@slack_events_adapter.on('message')
def handle_message(event_data):
    event = event_data['event']
    # print(event)
    channel_id = event['channel']
    user_id = event.get('user')
    print("userid")
    print(user_id)
    text = event.get('text', '').lower()

    if user_id != bot_id and 'expense' in text:
        # Store the expense message in MongoDB
        # expenses_collection.insert_one({"user_id": user_id, "message": text})

        prompt_message = "Please upload a receipt image/PDF for your expense."
        slack_client.chat_postMessage(channel=channel_id, text=prompt_message)
        # slack_client.chat_postMessage(
        #     channel=channel_id,
        #     blocks=adaptive_card["blocks"]
        # )


# Event handler for file uploads
@slack_events_adapter.on('file_shared')
def handle_file_upload(event_data):
    event = event_data['event']
    channel_id = event['channel_id']
    user_id = event['user_id']
    file_id = event['file_id']

    # Retrieve file information
    file_info = slack_client.files_info(file=file_id)
    file_url = file_info['file']['url_private']
    file_name = file_info['file']['name']

    headers = {
        "Authorization": f"Bearer {slack_client.token}"
    }
    r = requests.get(file_url, headers=headers)
    with open("temp.jpg", 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    # image_data = file_rep.content
    # Extract text from OCR results
    # extracted_text = extract_text(image_data)

    res = reader.readtext('temp.jpg')
    extracted_text = ""
    for (bbox, text, prob) in res:
        extracted_text += text
        extracted_text += " "

    # Retrieve the previously sent expense message associated with the user
    prev_expense_message = expenses_collection.find_one({"user_id": user_id})

    if prev_expense_message:
        prev_expense_text = prev_expense_message.get("message", "")
        # Log both the expense message and the image URL in MongoDB
        expenses_collection.insert_one({
            "user_id": user_id,
            "expense_message": prev_expense_text,
            "image": {"url": file_url, "name": file_name}
        })

        payload = json.dumps({
            "text": extracted_text
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
        adaptive_card = [
            {
                "type": "divider"
            },
            {
                "type": "section",
                "block_id": "section1",
                "text": {
                    "type": "mrkdwn",
                    "text": lable[int(response.text[-2])]
                }
            },
            {
                "type": "section",
                "block_id": "section2",
                "text": {
                    "type": "mrkdwn",
                    "text": "Kaliraj Expenses "
                }
            },
            {
                "type": "actions",
                "block_id": "actions1",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Accept"
                        },
                        "style": "primary",
                        "action_id": "accept_button",
                        "value": "accept"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reject"
                        },
                        "style": "danger",
                        "action_id": "reject_button",
                        "value": "reject"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]
        # Respond to the user
        cat = lable[int(response.text[-2])]
        print(cat)
        response_message = f"Category of the bill '{file_name}':\n '{cat}'"
        slack_client.chat_postMessage(
            channel=channel_id, text=response_message)
        slack_client.chat_postMessage(
            channel='U06TL668F4M', blocks=adaptive_card)

    else:
        # If there's no previous expense message, notify the user
        response_message = "You need to send an expense message first."
        slack_client.chat_postMessage(
            channel=channel_id, text=response_message)


# Start the Flask server
if __name__ == "__main__":
    app.run(debug=True)
