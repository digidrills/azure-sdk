# msal-authentication
## Sample code to authenticate client application with the Microsoft Graph API using Python.

### Dependencies
Run "pip install -r requirements.txt" file recursively to install all required dependencies.

### Pre-requisites
A Microsoft Azure free tier account is required to communicate with the Graph API. you can activate or create your account at "portal.azure.com"
Once made, go to "App Registrations" section and create a new app registration. Once made, from the overview section of your newly made App registration, copy the "Client ID".
Next, go to the "Certificates and secrets" section and make a new "client secret". Make sure to copy this and store it safely as it is shown only **once**. These values will be required in further steps to authenticate your app/program.

### Authentication
The code provided focuses on authenticating user application with the ms-graph API and accessing a file stored on user's OneDrive. The app is first Authenticated by any one of the multiple options available which returns the app with an access token which can in turn be used to access the ms-graph services such as onedrive, azure etc. We use the "acquire_token_by_username_password" method from msal for the sake of this example, however it is recommended to use other methods as having the username and password in the code might be unsafe. Be sure to replace the client_id and client_secret placeholders with your Client ID and Secret obtained in the previous step.

The acquired access token can be stored as Serializable Token cache for repeated use, read more at https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache

### Accessing MS Graph
We communicate with the Microsoft Graph service using REST APIs by sending POST requests to the ms-graph endpoint, for the case of our example we will be using the endpoint 

        https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/children

This will give us details about all children items in the root folder of the authenticated user's onedrive. 
To read more about the onedrive API with ms-graph refer to

        https://docs.microsoft.com/en-us/onedrive/developer/rest-api/resources/driveitem?view=odsp-graph-online

*Note that to access items in a user's Shared directory, you must use the "/sharedWithMe" endpoint.*

### Accessing files stored on a SharePoint site
To get the files stored on a sharepoint site, you must first get the site ID of the SharePoint site who's files you are trying to access (It is assumed that you have the necessary authority to get the files from the SharePoint site you are trying to access. To know more about how to get the access_token for your credentials, refer to the Authentication section of this repository). This can be done by going to:

        https://www.{tenant}.sharepoint.com/sites/{site-url}/_api/site/id
From the browser.

SharePoint sites also stores all files in an allocated OneDrive storage space and hence to access these files, you must use:

        https://graph.microsoft.com/sites/{site-id}/drive/root/children

This will list all the child items within the root directory of the sharepoint site.
To access files within a specific folder, use:

        https://graph.microsoft.com/sites/{site-id}/drive/root:/path/to/folder/children

To access a specific file within a folder, use:

        https://graph.microsoft.com/sites/{site-id}/drive/root:/path/to/file/content

This will give us the file binary.