# Simple Class to access OneDrive

This code contains a simple class which implements common methods to access directories and data from onedrive. 

To use this code, and to populate the parameters.json file, please follow instructions [here](https://docs.microsoft.com/en-us/graph/auth-v2-service)

Additional details like client secret are also to be generated.

### Current limitations are:
- This class only works for accessing information from OneDrive, even though Graph API as a whole can be used to access services thoughout Microsoft's services.
- The class can currently only access all resources to the /me endpoint, which will require delegated access permissions under the app registration and username/password from the user. There are currently issues with accessing data from non-/me endpoints without using username/pass flow.
- New methods are always being added