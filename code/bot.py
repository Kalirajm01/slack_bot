
# import os
# import cv2
# import requests
# from pathlib import Path
# from dotenv import load_dotenv
# from flask import Flask, request, Response, jsonify
# from slack import WebClient
# import json
# from slackeventsapi import SlackEventAdapter
# from pymongo import MongoClient
# import easyocr
# import numpy as np
# from datetime import datetime
# from slack_sdk.errors import SlackApiError

# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

# app = Flask(__name__)

# mongo_uri = os.getenv("MONGO_URI")
# mongo_client = MongoClient(mongo_uri)
# db = mongo_client.get_database("slack_bot")
# expenses_collection = db.get_collection("slackbot")

# slack_signing_secret = os.getenv("SIGNING_SECRET")
# slack_events_adapter = SlackEventAdapter(
#     slack_signing_secret, '/slack/events', app)

# slack_token = os.getenv("SLACK_TOKEN")
# slack_client = WebClient(token=slack_token)

# bot_id = slack_client.api_call("auth.test")['user_id']
# print("botid")
# print(bot_id)

# # Initialize EasyOCR reader
# reader = easyocr.Reader(['en'])
# processed_events = set()
# # Define Celery task for OCR processing


# # def extract_text(image_data):
# #     image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
# #     extracted_text = reader.readtext(image)

# #     return extract_text
# lable = ["Food", "Travel", "Stay", "Electronics"]

# url = "http://127.0.0.1:5200/predict"

# last_assigned_id = 0

# @slack_events_adapter.on('message')
# def handle_message(event_data):
#     print("inside the message")
#     event = event_data['event']
#     # print(event)
#     channel_id = event['channel']
#     user_id = event.get('user')
#     #print(event)
#     print("userid")
#     print(user_id)
#     text = event.get('text', '').lower()

#     if user_id != bot_id and 'expense' in text:
#         prompt_message = "Please upload a receipt image/PDF for your expense."
#         slack_client.chat_postMessage(channel=channel_id, text=prompt_message)
#         # slack_client.chat_postMessage(
#         #     channel=channel_id,
#         #     blocks=adaptive_card["blocks"]
#         # )

# # Event handler for file uploads
# @slack_events_adapter.on('file_shared')
# def handle_file_upload(event_data):
#     print("inside the file shared")
#     event = event_data['event']
#     event_id = event_data.get('event_id')
#     channel_id = event['channel_id']
#     user_id = event['user_id']
#     print(event_data)
#     file_id = event['file_id']
#     print(event_id)
#     print(processed_events)
#     print(len(processed_events))
#     if len(processed_events):
#         print("Greater than one")
#         if event_id in processed_events:
#             print("Duplicate Diducted")
#             return 
#     processed_events.add(event_id)

#     # Retrieve file information
#     file_info = slack_client.files_info(file=file_id)
#     file_url = file_info['file']['url_private']
#     file_name = file_info['file']['name']
#     print(file_name)
    
#     headers = {
#         "Authorization": f"Bearer {slack_client.token}"
#     }
#     print("before reading the file")
#     r = requests.get(file_url, headers=headers)
#     with open("temp.jpg", 'wb') as f:
#         for chunk in r.iter_content(chunk_size=1024):
#             if chunk:
#                 f.write(chunk)
#     print("After reading the file")
#     # image_data = file_rep.content
#     # Extract text from OCR results
#     # extracted_text = extract_text(image_data)
#     print("Before text extraction")
#     res = reader.readtext('temp.jpg')
#     extracted_text = ""
#     for (bbox, text, prob) in res:
#         extracted_text += text
#         extracted_text += " "
#     print("After text extraction")
#     # Retrieve the previously sent expense message associated with the user
#     #prev_expense_message = expenses_collection.find_one({"user_id": user_id})
#     #print("hello" + prev_expense_message)
#     prev_expense_message = 1
#     if prev_expense_message:
#         print("condition true")

#         Date = datetime.now()
#         last_entry = expenses_collection.find_one(sort=[("ID", -1)])
#         print(last_entry)
#         if last_entry:
#             last_assigned_id = last_entry["ID"]
#             next_id = last_assigned_id + 1
#         else:
#             next_id = 1

#         expenses_collection.insert_one({
#             "ID": next_id,
#             "Employee_ID": user_id,
#             "Employee_Name": "Kaliraj",
#             "File": {"URL": file_url, "File_Name": file_name},
#             "Extracted-Text": extracted_text,
#             "Status": "Pending",
#             "Sent_Date": Date
#         })

#         payload = json.dumps({
#             "text": extracted_text
#         })
#         headers = {
#             'Content-Type': 'application/json'
#         }

#         response = requests.request("POST", url, headers=headers, data=payload)

#         print(response.text)
#         adaptive_card = [
#             {
#                 "type": "divider"
#             },
#             {
#                 "type": "section",
#                 "block_id": "section1",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": lable[int(response.text[-2])]
#                 }
#             },
#             {
#                 "type": "section",
#                 "block_id": "section2",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": "Kaliraj Expenses "
#                 }
#             },
#             {
#                 "type": "actions",
#                 "block_id": "actions1",
#                 "elements": [
#                     {
#                         "type": "button",
#                         "text": {
#                             "type": "plain_text",
#                             "text": "Accept"
#                         },
#                         "style": "primary",
#                         "action_id": "accept_button",
#                         "value": "accept"
#                     },
#                     {
#                         "type": "button",
#                         "text": {
#                             "type": "plain_text",
#                             "text": "Reject"
#                         },
#                         "style": "danger",
#                         "action_id": "reject_button",
#                         "value": "reject"
#                     }
#                 ]
#             },
#             {
#                 "type": "divider"
#             }
#         ]
#         # Respond to the user
#         cat = lable[int(response.text[-2])]
#         print(cat)
#         response_message = f"Category of the bill '{file_name}':\n '{cat}'"
#         slack_client.chat_postMessage(
#             channel=channel_id, text=response_message)
#         slack_client.chat_postMessage(
#             channel='U06TP4D0U1G', blocks=adaptive_card)

#     else:
#         response_message = "You need to send an expense message first."
#         slack_client.chat_postMessage(
#             channel=channel_id, text=response_message)

# @app.route('/slack/actions', methods=['POST'])
# def slack_actions():
#     try:
#         payload = json.loads(request.form['payload'])
#         action_id = payload['actions'][0]['action_id']
#         user_id = payload['user']['id']
#         channel_id = payload['channel']['id']
#         file_url = payload['message']['blocks'][1]['text']['text'].split(" ")[-1][1:-1]

#         if action_id == "accept_button":
#             update_result = expenses_collection.update_one(
#                 {"File.URL": file_url},
#                 {"$set": {"Status": "Accepted"}}
#             )
#             if update_result.modified_count == 1:
#                 success_message = "Your request has been accepted successfully."
#                 slack_client.chat_postMessage(channel=channel_id, text=success_message)
#             else:
#                 print("No document matched the query.")
    
#         elif action_id == "reject_button":
#             update_result = expenses_collection.update_one(
#                 {"File.URL": file_url},
#                 {"$set": {"Status": "Rejected"}}
#             )
#             if update_result.modified_count == 1:
#                 reject_message = "Your request has been rejected."
#                 slack_client.chat_postMessage(channel=channel_id, text=reject_message)
#             else:
#                 print("No document matched the query.")

#         return jsonify(status=200)
#     except Exception as e:
#         print("An error occurred:", str(e))
#         return jsonify(status=500, error=str(e))


# # Start the Flask server
# if __name__ == "__main__":
#     app.run(debug=True)






import os
import cv2
import requests
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify
from slack import WebClient
import json
from slackeventsapi import SlackEventAdapter
from pymongo import MongoClient
import easyocr
from datetime import datetime
from slack_sdk.errors import SlackApiError

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)
db = mongo_client.get_database("slack_bot")
expenses_collection = db.get_collection("slackbot")

slack_signing_secret = os.getenv("SIGNING_SECRET")
slack_events_adapter = SlackEventAdapter(
    slack_signing_secret, '/slack/events', app)

slack_token = os.getenv("SLACK_TOKEN")
slack_client = WebClient(token=slack_token)

bot_id = slack_client.api_call("auth.test")['user_id']
print("botid")
print(bot_id)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])
processed_events = set()
# Define Celery task for OCR processing

lable = ["Food", "Travel", "Stay", "Electronics"]

url = "http://127.0.0.1:5200/predict"

last_assigned_id = 0

@slack_events_adapter.on('message')
def handle_message(event_data):
    print("inside the message")
    event = event_data['event']
    channel_id = event['channel']
    user_id = event.get('user')
    print("userid")
    print(user_id)
    text = event.get('text', '').lower()

    if user_id != bot_id and 'expense' in text:
        prompt_message = "Please upload a receipt image/PDF for your expense."
        slack_client.chat_postMessage(channel=channel_id, text=prompt_message)

@slack_events_adapter.on('file_shared')
def handle_file_upload(event_data):
    print("inside the file shared")
    event = event_data['event']
    event_id = event_data.get('event_id')
    channel_id = event['channel_id']
    user_id = event['user_id']
    print(event_data)
    file_id = event['file_id']
    print(event_id)
    print(processed_events)
    print(len(processed_events))
    if len(processed_events):
        print("Greater than one")
        if event_id in processed_events:
            print("Duplicate Diducted")
            return 
    processed_events.add(event_id)

    file_info = slack_client.files_info(file=file_id)
    file_url = file_info['file']['url_private']
    file_name = file_info['file']['name']
    print(file_name)
    
    headers = {
        "Authorization": f"Bearer {slack_client.token}"
    }
    print("before reading the file")
    r = requests.get(file_url, headers=headers)
    with open("temp.jpg", 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print("After reading the file")

    res = reader.readtext('temp.jpg')
    extracted_text = ""
    for (bbox, text, prob) in res:
        extracted_text += text
        extracted_text += " "
    print("After text extraction")

    prev_expense_message = 1
    if prev_expense_message:
        print("condition true")

        Date = datetime.now()
        last_entry = expenses_collection.find_one(sort=[("ID", -1)])
        print(last_entry)
        if last_entry:
            last_assigned_id = last_entry["ID"]
            next_id = last_assigned_id + 1
        else:
            next_id = 1

        expenses_collection.insert_one({
            "ID": next_id,
            "Employee_ID": user_id,
            "Employee_Name": "Kaliraj",
            "File": {"URL": file_url, "File_Name": file_name},
            "Extracted-Text": extracted_text,
            "Status": "Pending",
            "Sent_Date": Date
        })

        payload = json.dumps({
            "text": extracted_text
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
        user_info = expenses_collection.find_one({"Employee_ID": user_id})
        price = '268.00'
        gst = 'AAAC05022HSD001'

        adaptive_card = [
            {
                "type": "divider"
            },

            {
            "type": "section",
            "block_id": "section1",
            "text": {
                "type": "mrkdwn",
                "text": f"*A Employee has submitted a Expense for approval* "
                    }
            },
            {
            "type": "section",
            "block_id": "section2",
            "text": {
                "type": "mrkdwn",
                "text": f"*Employee ID:* {user_id}   *Employee Name:* {user_info['Employee_Name']}"
                    }
            },

            {
                        "type": "section",
                        "block_id": "section3",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Date:* {Date.strftime('%Y-%m-%d %H:%M:%S')}   *Category:* {lable[int(response.text[-2])]}"
                        }
                    },

            {
            "type": "section",
            "block_id": "section4",
            "text": {
                "type": "mrkdwn",
                "text": f"*Total Amount:* {price}   *GST Number:* {gst}"
                    }
            },

            {
                "type": "section",
                "block_id": "section5",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*ID:* {next_id}"
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
                        "action_id": "a"+str(next_id),
                        "value": file_url
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reject"
                        },
                        "style": "danger",
                        "action_id": "r"+str(next_id),
                        "value": file_url
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]

        adaptive_card1 = [
            {
                "type": "divider"
            },

            {
            "type": "section",
            "block_id": "section2",
            "text": {
                "type": "mrkdwn",
                "text": f"*Employee ID:* {user_id}   *Employee Name:* {user_info['Employee_Name']}"
                    }
            },

            {
                        "type": "section",
                        "block_id": "section3",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Date:* {Date.strftime('%Y-%m-%d %H:%M:%S')}   *Category:* {lable[int(response.text[-2])]}"
                        }
                    },

            {
            "type": "section",
            "block_id": "section4",
            "text": {
                "type": "mrkdwn",
                "text": f"*Total Amount:* {price}   *GST Number:* {gst}"
                    }
            },

            {
                "type": "section",
                "block_id": "section5",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*ID:* {next_id}"
                }
            },
            {
                "type": "divider"
            }
        ]

        # slack_client.chat_postMessage(
        #     channel=channel_id, text=response_message)
        slack_client.chat_postMessage(
            channel='U06TP4D0U1G', blocks=adaptive_card)
        slack_client.chat_postMessage(
            channel='U06TL668F4M', blocks=adaptive_card1)

    else:
        response_message = "You need to send an expense message first."
        slack_client.chat_postMessage(
            channel=channel_id, text=response_message)
@app.route('/slack/actions', methods=['POST'])
def slack_actions():
    try:
        payload = json.loads(request.form['payload'])
        action_id = payload['actions'][0]['action_id']
        user_id = payload['user']['id']
        channel_id = payload['channel']['id']
        file_url = payload['actions'][0]['value']
        doc_id = int(action_id[1:])
        print(doc_id)
        if action_id[0] == 'a':
            print("Accepted")
            update_result = expenses_collection.update_one(
                {"ID": doc_id},
                {"$set": {"Status": "Accepted"}}
            )
            if update_result.modified_count == 1:
                success_message = "Your request has been accepted successfully."
                slack_client.chat_postMessage(channel='U06TL668F4M', text=success_message)
                return jsonify(status=200)
            else:
                print("No document matched the query.")
                return jsonify(status=404, error="No document matched the query.")

        elif action_id[0] == 'r':
            print("Reject")
            update_result = expenses_collection.update_one(
                {"ID": doc_id},
                {"$set": {"Status": "Rejected"}}
            )
            if update_result.modified_count == 1:
                reject_message = "Your request has been rejected."
                slack_client.chat_postMessage(channel='U06TL668F4M', text=reject_message)
                return jsonify(status=200)
            else:
                print("No document matched the query.")
                return jsonify(status=404, error="No document matched the query.")

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify(status=500, error=str(e))




if __name__ == "__main__":
    app.run(debug=True)

