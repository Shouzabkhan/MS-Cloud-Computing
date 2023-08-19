import os
import boto3
import json
from datetime import datetime


def email_handler(event, context):
email="khanshouzab123@gmail.com"
    email = event['email']
    data = event['data']

    now = datetime.now()
    subject = "File notification ({})".format(now.strftime("%Y-%m-%d %H:%M:%S"))

    email_message = {
        "Subject": {
            "Data": subject,
        },
        "Body": {
            "Text": {
                "Data": data,
            },
        },
    }

    ses_client = boto3.client("ses",
    ACCESS_KEY = "AKIAWORBIWID26ZOLELY",
    SECRET_KEY ="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",
    ACCESS_REGION="us-east-1"
)
    ses_client.send_email(
        Source=email,
        Destination={"ToAddresses": [email]},
        Message=email_message,
    )

    print("Email sent successfully!")
