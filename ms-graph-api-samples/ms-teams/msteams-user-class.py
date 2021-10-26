import json
import msal
import requests
from requests import Response
from pprint import pprint
import os
# All text within angular brackets (<>) are meant to be replaced with your custom values of their respective fields.
# TODO: Integration of all API methods and funtcions into a single program


# method to GET Authentication Token using MSAL
# TODO: change from username and password to more secure methods.
def authorisation(client_username, client_password):
    config = json.load(open("./parameters.json"))
    app = msal.ConfidentialClientApplication(
        config["client_id"],
        authority=config["authority"],
        client_credential=config["secret"],
    )
    result = app.acquire_token_by_username_password(
        scopes=(config["scope"]),
        username=client_username,
        password=client_password
    )
    if "access_token" in result:
        print("Success")
        return result["access_token"]
    else:
        print("Failed to get Access Token. Check your credentials.")

# GETs all chats from a user's ms-teams. 
# TODO: group_chat_length should give total number of chats
def teams_get_chats():
    chat_list = requests.get("https://graph.microsoft.com/v1.0/me/chats",
                             headers=headers)
    group_chat_list = chat_list.json()['value']
    group_chat_length = len(group_chat_list)
    return group_chat_list

# GETs the id of the referenced chat
# REQUIRES: topic of the chat
# TODO: currently the topic entered must be case sensitive, find a way to match the entered topic regardless of case
def get_chat_id(topic_name):
    group_chat_list = teams_get_chats()
    i = 0
    while i < len(teams_get_chats()):
        if group_chat_list[i]['topic'] == topic_name:
            group_chat_id = group_chat_list[i]['id']
            return group_chat_id
        i += 1
    return "No such chat found, please check your spelling"

# SEND a message to a teams chat using the chat ID
# REQUIRES: chat id
def teams_send_message(message):
    topic = "Test Group Chat 1"
    chat_id = get_chat_id(topic)
    data = {"body": {"content": f"{message}"}}
    data = json.dumps(data)
    sent_request = requests.post(
        f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages", headers=headers, data=data)
    return sent_request.json()

#  GETs the user's default calendar metadata
def get_calendar():
    calData = requests.get("https://graph.microsoft.com/v1.0/me/calendar",
                           headers=headers)
    return calData.json()

#  GETs the user's default calendar's list of events in JSON format
def get_calendar_events():
    calData = requests.get(
        "https://graph.microsoft.com/v1.0/me/calendar/events", headers=headers)
    return calData.json()

# POSTs a new calendar event onto the user's default calendar
# REQUIRES: subject, body, content, start and end datetime, location, attendees
# TODO: need to add input fields for the calendar event data, currently present data is placeholder hardcoded data
# TODO: the same json schema must be followed for sending a calendar event or a invalid payload error will be thrown
def create_calendar_event():
    data = {
        "subject": "Let's go for lunch",
        "body": {
            "contentType": "HTML",
            "content": "Does late morning work for you?"
        },
        "start": {
            "dateTime": "2019-06-16T12:00:00",
            "timeZone": "Pacific Standard Time"
        },
        "end": {
            "dateTime": "2019-06-16T14:00:00",
            "timeZone": "Pacific Standard Time"
        },
        "location": {
            "displayName": "Harry's Bar"
        },
        "attendees": [
            {
                "emailAddress": {
                    "address": "adelev@contoso.onmicrosoft.com",
                    "name": "Adele Vance"
                },
                "type": "required"
            }
        ]
    }
    data = json.dumps(data)
    calData = requests.post(
        "https://graph.microsoft.com/v1.0/me/calendar/events", headers=headers, data=data)
    return calData.json()

# GETs the user's default sharepoint root site metadata
def get_sharepoint_sites():
    sharepointData = requests.get(
        "https://graph.microsoft.com/v1.0/sites/root", headers=headers)
    return sharepointData.json()

# GETs all the user's lists within their default root sharepoint site
def get_sharepoint_lists():
    sharepointData = requests.get(
        "https://graph.microsoft.com/v1.0/sites/root/lists", headers=headers)
    return sharepointData.json()

# TODO: Ignore for now, this function is meant to get specific chat-ids, currently a work in progress
def get_chats():
    data = {
        "policyViolation": {
            "policyTip": {
                "generalText": "This item has been blocked by the administrator.",
                "complianceUrl": "https://contoso.com/dlp-policy-page",
                "matchedConditionDescriptions": ["Credit Card Number"]
            },
            "verdictDetails": "AllowOverrideWithoutJustification,AllowFalsePositiveOverride",
            "dlpAction": "BlockAccess"
        }
    }
    data = json.dumps(data)
    chatData = requests.patch(
        f"https://graph.microsoft.com/v1.0/me/chats/{get_chat_id('Test Group Chat 1')}/messages/19:962cd34f89824659b41ff976cf09d6ba@thread.v2", headers=headers, data=data)
    return chatData.json()

# the variables used for fetching the access_token from ms
# TODO: Encryption of these variable important to maintain security
access_token = authorisation("<username>", "<password>")
headers = {"Authorization": "Bearer " +
           access_token, "Content-type": "application/json"}

pprint()
