# Azure Event Grid Trigger

Azure Event grid is a Publish/Subscribe service offered by MS Azure to connect various internal and external events and process them.

The creation, linking and reciving the event are the 3 steps involved in Azure Event Grids.

In this example, we will use an Azure Function App to receive the trigger, and the event grid python sdk provided by microsoft to send an event through code

### Step 1:
Create an Event grid topic under Azure. This will generate a topic endpoint URL and a key, which we need to copy paste into our parameters.json file under EventGridTrigger/

### Step 2:
Create a Function app in vscode or through the portal. The template to be used is "Azure Event Grid Trigger". The template will be generated for you. The important part now is to publish the app so it is available and running on Azure.

### Step 3:
Linking the "Publish" service to the "Subscribe" service is done through Event Subscriptions. They are seperate entities under Azure Portal. A new subscription is to be created where the appropriate topic is chosen and Azure Functions is chosen as the endpoint for the subscription. This will link them together.

Now any event sent to that particular topic (using that topics URL) will automatically trigger the Function and it will display the output in the log. More logic can be added to do something on receiving an event.