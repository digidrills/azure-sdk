import os
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
import json

# make sure the parameters.json file has the correct key and endpoint, else this program wont work
config = json.load(
    open(os.path.join(os.path.abspath(""), "EventGridTrigger", "parameters.json"))
)

key = config["key"]
endpoint = config["endpoint"]

# event topic and subscription were set to event grid schema. Use custom schema for sending custom dicts
event = EventGridEvent(
    data={"team": "azure-sdk"},
    subject="Door1",
    event_type="Azure.Sdk.Demo",
    data_version="1.0",
)

credential = AzureKeyCredential(key)
client = EventGridPublisherClient(endpoint, credential)

client.send(event)
