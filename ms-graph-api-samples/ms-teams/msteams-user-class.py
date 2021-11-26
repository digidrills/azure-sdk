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
        scopes=(config["scope"]), username=client_username, password=client_password
    )
    if "access_token" in result:
        print("Success")
        return result["access_token"]
    else:
        print("Failed to get Access Token. Check your credentials.")


# GETs all chats from a user's ms-teams.
# TODO: group_chat_length should give total number of chats
def teams_get_chats():
    chat_list = requests.get(
        "https://graph.microsoft.com/v1.0/me/chats", headers=headers
    )
    group_chat_list = chat_list.json()["value"]
    group_chat_length = len(group_chat_list)
    return group_chat_list


# GETs the id of the referenced chat
# REQUIRES: topic of the chat
# TODO: currently the topic entered must be case sensitive, find a way to match the entered topic regardless of case
def get_chat_id(topic_name):
    group_chat_list = teams_get_chats()
    i = 0
    while i < len(teams_get_chats()):
        if group_chat_list[i]["topic"] == topic_name:
            group_chat_id = group_chat_list[i]["id"]
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
        f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages",
        headers=headers,
        data=data,
    )
    return sent_request.json()


#  GETs the user's default calendar metadata
def get_calendar():
    calData = requests.get(
        "https://graph.microsoft.com/v1.0/me/calendar", headers=headers
    )
    return calData.json()


#  GETs the user's default calendar's list of events in JSON format
def get_calendar_events():
    calData = requests.get(
        "https://graph.microsoft.com/v1.0/me/calendar/events", headers=headers
    )
    return calData.json()


# POSTs a new calendar event onto the user's default calendar
# REQUIRES: subject, body, content, start and end datetime, location, attendees
# TODO: the same json schema must be followed for sending a calendar event or a invalid payload error will be thrown
def create_calendar_event(
    subject, content, start_time, end_time, location, attendee_email, attendee_name
):
    data = {
        "subject": f"{subject}",
        "body": {"contentType": "HTML", "content": f"{content}"},
        "start": {"dateTime": f"{start_time}", "timeZone": "Indian Standard Time"},
        "end": {"dateTime": f"{end_time}", "timeZone": "Indian Standard Time"},
        "location": {"displayName": f"{location}"},
        "attendees": [
            {
                "emailAddress": {
                    "address": f"{attendee_email}",
                    "name": f"{attendee_name}",
                },
                "type": "required",
            }
        ],
    }
    data = json.dumps(data)
    calData = requests.post(
        "https://graph.microsoft.com/v1.0/me/calendar/events",
        headers=headers,
        data=data,
    )
    return calData.json()


# GETs the user's default sharepoint root site metadata
def get_sharepoint_sites():
    sharepointData = requests.get(
        "https://graph.microsoft.com/v1.0/sites/root", headers=headers
    )
    return sharepointData.json()


# GETs all the user's lists within their default root sharepoint site
def get_sharepoint_lists():
    sharepointData = requests.get(
        "https://graph.microsoft.com/v1.0/sites/root/lists", headers=headers
    )
    return sharepointData.json()




# GETs the ID of the required team
def get_team_id():
    channelData = requests.get(
        "https://graph.microsoft.com/v1.0/me/joinedTeams", headers=headers
    )
    return channelData.json()["value"][1]["id"]

def get_chat_id_from_teams(topic_name):
    group_chat_list = teams_get_chats()
    i = 0
    while i < len(teams_get_chats()):
        if group_chat_list[i]["topic"] == topic_name:
            group_chat_id = group_chat_list[i]["id"]
            return group_chat_id
        i += 1
    return "No such chat found, please check your spelling"

# get channel id from teams


def get_channel_id(channel_name):
    channelData = requests.get(
        "https://graph.microsoft.com/v1.0/me/joinedTeams", headers=headers)
    i = 0
    while i < len(channelData.json()['value']):
        if channelData.json()['value'][i]['displayName'] == channel_name:
            channel_id = channelData.json()['value'][i]['id']
            return channel_id
        i += 1
    return "No such channel found, please check your spelling"

# edit chat message in teams
def edit_chat_message(message_id, message):
    data = {"body": {"content": f"{message}"}}
    data = json.dumps(data)
    sent_request = requests.patch(
        f"https://graph.microsoft.com/v1.0/chats/{message_id}/messages", headers=headers, data=data)
    return sent_request.json()


# the variables used for fetching the access_token from ms
# TODO: Encryption of these variable important to maintain security
access_token = authorisation("<username>", "<password>")
headers = {
    "Authorization": "Bearer " + access_token,
    "Content-type": "application/json",
}

pprint(get_chat_id_from_teams("Test Group Chat 1"))
