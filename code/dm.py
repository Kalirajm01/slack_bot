# import os
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Initialize Slack WebClient
# slack_token = os.getenv("SLACK_TOKEN")
# client = WebClient(token=slack_token)


# def send_dm(user_id, message):
#     try:
#         # Open a DM channel with the user
#         response = client.conversations_open(users=[user_id])
#         dm_channel = response["channel"]["id"]

#         # Send a direct message to the user
#         client.chat_postMessage(channel=dm_channel, text=message)
#         print(f"Message sent to user {user_id}")

#     except SlackApiError as e:
#         error_message = e.response['error']
#         if error_message == "cannot_dm_bot":
#             print("Error: The user ID provided belongs to a bot.")
#         else:
#             print(f"Error sending message: {error_message}")


# if __name__ == "__main__":
#     # Replace 'USER_ID' with the actual Slack user ID you want to message
#     user_id = 'U06TL668F4M'
#     message = "Hello! This is a test direct message."

#     send_dm(user_id, message)



import os
import json
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

# Load environment variables
load_dotenv()
slack_token = os.getenv("SLACK_TOKEN")
client = WebClient(token=slack_token)

# Initialize Flask app
app = Flask(__name__)

def send_dm_with_block(user_id, blocks):
    try:
        response = client.conversations_open(users=[user_id])
        dm_channel = response["channel"]["id"]

        client.chat_postMessage(channel=dm_channel, blocks=blocks)
        print(f"Message sent to user {user_id}")

    except SlackApiError as e:
        error_message = e.response['error']
        if error_message == "cannot_dm_bot":
            print("Error: The user ID provided belongs to a bot.")
        else:
            print(f"Error sending message: {error_message}")

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = json.loads(request.form["payload"])
    user_id = data["user"]["id"]
    action_id = data["actions"][0]["action_id"]

    if action_id == "accept_button":
        send_email(user_id, "Request Accepted", "Your request has been accepted successfully.")
        send_confirmation_dm(user_id, "Success! Your request has been accepted.")
    elif action_id == "reject_button":
        send_email(user_id, "Request Rejected", "Your request has been rejected.")
        send_confirmation_dm(user_id, "Your request has been rejected.")
        
    return jsonify(status=200)

def send_confirmation_dm(user_id, text):
    try:
        response = client.conversations_open(users=[user_id])
        dm_channel = response["channel"]["id"]

        client.chat_postMessage(channel=dm_channel, text=text)
        print(f"Confirmation message sent to user {user_id}")
    except SlackApiError as e:
        error_message = e.response['error']
        print(f"Error sending confirmation message: {error_message}")

def send_email(user_id, subject, body):
    email_address = get_user_email(user_id)
    if not email_address:
        print(f"Error: No email address found for user {user_id}")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = os.getenv("EMAIL_SENDER")
    msg["To"] = email_address

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")

    print(f"Connecting to SMTP server {smtp_server} on port {smtp_port}...")

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
            server.sendmail(os.getenv("EMAIL_SENDER"), email_address, msg.as_string())
        print(f"Email sent to {email_address} with subject '{subject}'")
    except Exception as e:
        print(f"Error sending email: {e}")

def get_user_email(user_id):
    try:
        response = client.users_info(user=user_id)
        return response['user']['profile']['email']
    except SlackApiError as e:
        print(f"Error fetching user email: {e.response['error']}")
        return None

if __name__ == "__main__":
    # Start the Flask app
    app.run(port=3000)

    # Send the initial DM with buttons to a user
    user_id = 'U06TL668F4M'
    message_blocks = [
        {
            "type": "divider"
        },
        {
            "type": "section",
            "block_id": "section1",
            "text": {
                "type": "mrkdwn",
                "text": "*Hello!* :wave:"
            }
        },
        {
            "type": "section",
            "block_id": "section2",
            "text": {
                "type": "mrkdwn",
                "text": "Expense"
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

    send_dm_with_block(user_id, message_blocks)

