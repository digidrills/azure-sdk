#%%
# Remember to populate parameters.json before running this program

import json
import logging
from base64 import b64decode
from copy import deepcopy
from dataclasses import dataclass
from pprint import pprint
from typing import Dict, List, Optional, Tuple, Union
import mimetypes
import os

import msal
import requests

# logging.basicConfig(level=logging.DEBUG)


@dataclass
class SharedDrive:
    """
    Class to hold shared onedrive credentials
    """

    drive_id: str
    parent_id: str


@dataclass
class DriveItem:
    """
    Class to represent a single drive item, whether file or folder
    """

    name: str
    id: str
    drive_id: str
    folder: bool = False
    child_count: int = None


# %%
class OneDriveUser:
    """
    Abstract class representation of a OneDrive user used to authenticate to onedrive.
    Implemented basic methods like list root/shared and upload/download.
    This is done to prevent lot of repeated boilerplate code regarding sending
    http requests and parsing responeses
    """

    def __init__(
        self, path_to_json: dict, shared_scope: dict = None, auth_mode: str = "userpass"
    ) -> None:
        """
        :param path_to_json: path to the parameters.json file which contains all info
                        relating to authentication client to the app
        :param shared_folder_name: Name of the shared folder to interact with. Defaults to None (no shared folder access)
        :param auth_mode: str param to describe authentication mode used. either code flow or username password. Currently supported auth-modes:
        - `userpass`: default. uses username/pass passed into path_to_json to login. this flow can be used to access the me endpoints.
        - `codeflow`: uses client secret and /token endpoint to get access to account without need for password. cannot access me endpoint
        """
        """
        TODO
        - include working/root_dir in upload/download calls. will have to change the api
        - get user id from or username, because we will need to access the drive. /me endpoint wont work
        - change download, list, upload api's to accomodate new urls
        """
        # cache-like object params
        self.all_shared_items = []
        self.all_root_items = []

        # Normal class params
        self.config = path_to_json
        self.auth_url = self.config["authority"]
        self.client_id = self.config["client_id"]
        self.scope = "Files.ReadWrite.All"
        self.default_scope = self.config["scope"]
        self.secret = self.config["secret"]
        self.endpoint = "https://graph.microsoft.com/v1.0"
        self.endpoint_me = f"{self.endpoint}/me/drive"
        self.tenant_id = self.config["tenant_id"]
        self.username = b64decode(self.config["username"].encode("utf-8")).decode(
            "utf-8"
        )
        self.headers = self._authenticate(auth_mode)
        print("Successfully Authenticated user")
        if shared_scope:
            self.shared_drive = SharedDrive(
                *self._authenticate_shared_drive(shared_scope)
            )
            print("Successfully Authenticated Shared Drive")
        self.download_key = "@microsoft.graph.downloadUrl"
        if auth_mode.lower() not in ["userpass", "codeflow"]:
            raise Exception("Not a supported mode")
        self.mode = auth_mode.lower()

    def _authenticate(self, mode: str):
        """
        Login to the ondrive account and return the header file needed for auth
        :param mode: str param to describe authentication mode used. either code flow or username password.
        supported modes are:
        - userpass - for username password
        - codeflow - get access token by visiting /token endpoint
        """
        if mode == "userpass":
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=f"{self.auth_url}/{self.tenant_id}",
                client_credential=self.secret,
            )
            result = app.acquire_token_by_username_password(
                scopes=[self.scope],
                username=self.username,  # already decoded
                password=b64decode(self.config["password"]).decode("utf-8"),
            )

            if "access_token" not in result:
                raise KeyError("No access token found. Check errors pls")

            headers = {"Authorization": f"Bearer {result['access_token']}"}

            return headers

        elif mode == "codeflow":
            url = f"{self.auth_url}/{self.tenant_id}/oauth2/v2.0/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            body = {
                "client_id": self.client_id,
                "scope": self.default_scope,
                "client_secret": self.secret,
                "grant_type": "client_credentials",
            }
            result = requests.post(url, body, params=headers).json()

            if "access_token" not in result:
                raise KeyError(
                    f"Access token not found. Check error message below\n\n{result}"
                )

            headers = {"Authorization": f"Bearer {result['access_token']}"}

            return headers

        else:
            raise ValueError(f"Unsupported Authentication Mode {mode}")

    def download_file(self, path_to_file: str) -> bytes:
        """
        :param path_to_file: Path to the file relative to the root of the drive.
        Can be of 2 types:
        - `folder/subfolder/file.ext` (if downloading from root drive)
        - `shared/folder/subfolder/file.ext` (if downloading from shared drive. Make sure shared drive details are authenticated and `folder` is shared with you)
        :param return: The raw bytes of the file downloaded. Decode it based on the file type requested, using the appropriate library if necessary (like PIL for imgs)
        """
        if self.mode == "userpass":
            if "shared" not in path_to_file:
                url = f"{self.endpoint_me}/root:/{path_to_file}:/content"
                resp = requests.get(url, headers=self.headers)
                return resp.content

            else:
                path = "/".join(path_to_file.split("/")[1:])
                url = f"{self.endpoint}/drives/{self.shared_drive.drive_id}/root:/{path}:/content"
                resp = requests.get(url, headers=self.headers)
                return resp.content
        else:
            if "shared" not in path_to_file:
                url = f"{self.endpoint}/users/{self.username}/drive/root:/{path_to_file}:/content"
                resp = requests.get(url, headers=self.headers)
                return resp.content

            else:
                raise NotImplementedError()

    def upload_file(self, file: object, filepath: str) -> Dict:
        """
        :param file: The file to be uploaded. Its type will be guessed from its extention
        :param filepath: -- Path of the file relative to the root drive folder.
        The path must be of the following 2 formats:
        - `folder/subfolder/file.ext` (for uploading to one's own drive)
        - `shared/folder/subfolder/file.ext` (for uploading to a shared folder. the "folder" should be shared, not private. basically prefix shared/)
        :param return: Dictionary containing the response from the server. Will contain download url to file if successful, or an error message if failed
        """
        headers = deepcopy(self.headers)
        content_type = mimetypes.guess_type(filepath)[0]

        if type is None:
            raise Exception("Cannot determine filetype from extention. RIP")

        headers["Content-Type"] = content_type

        if "shared" not in filepath:
            mypath = f"{self.endpoint_me}/root:/{filepath}:/content"
            resp = requests.put(mypath, headers=headers, data=file)
            return resp.json()
        else:
            path = "/".join(filepath.split("/")[1:])
            try:
                assert (
                    len(path) > 1
                )  # when using shared folder, cannot upload to root directly. Need atleast 1 folder
            except AssertionError as e:
                return {
                    "CustomError": f"{e.args}\nCannot upload to root of shared folder. Provide atleast 1 folder, and make sure its shared with you"
                }

            url = f"{self.endpoint}/drives/{self.shared_drive.drive_id}/root:/{path}:/content"
            resp = requests.put(url, headers=headers, data=file)

            return resp.json()

    def list_shared(self) -> List[DriveItem]:
        """
        List the root of the shared folder
        """
        url = f"{self.endpoint_me}/sharedWithMe"
        resp = requests.get(url, headers=self.headers).json()
        vals = resp["value"]

        temp_output = []
        for entry in vals:
            name = entry["name"]
            idx = entry["id"]
            if "folder" in entry:
                folder = True
                cc = entry["folder"]["childCount"]
            else:
                folder = False
                cc = None
            driveid = entry["remoteItem"]["parentReference"]["driveId"]
            temp_output.append(DriveItem(name, idx, driveid, folder, cc))

        # evaluate and update cache
        if temp_output != self.all_shared_items:
            self.all_shared_items = deepcopy(temp_output)
        return self.all_shared_items

    def list_root(self) -> List[DriveItem]:
        """
        List the root folder of the drive of the user. Return a dict response
        header -- provide the relavant header with authorization token
        """
        if self.mode == "userpass":
            resp = requests.get(
                f"{self.endpoint_me}/root/children", headers=self.headers
            )
            if resp.status_code != 200:
                raise ValueError("Could not list. some auth error")
            resp = resp.json()
            vals = resp["value"]
            temp_output = self._create_driveitems(vals)

            # evaluate and update cache
            if temp_output != self.all_root_items:
                self.all_root_items = deepcopy(temp_output)
            return self.all_root_items
        else:
            # TODO
            pass

    def _create_driveitems(self, vals: list) -> List[DriveItem]:
        temp_output = []
        for entry in vals:
            name = entry["name"]
            idx = entry["id"]
            if "folder" in entry:
                folder = True
                cc = entry["folder"]["childCount"]
            else:
                folder = False
                cc = None
            driveid = entry["parentReference"]["driveId"]
            temp_output.append(DriveItem(name, idx, driveid, folder, cc))
        return temp_output

    def _authenticate_shared_drive(self, shared_scope: Dict) -> Tuple[str, str]:
        shared_children = self.list_shared()
        drive_id = shared_children[0].drive_id
        for item in shared_children:
            if item.name == shared_scope["input_dir"]:
                parent_id = item.id

        return drive_id, parent_id

    def delta(self):
        # WIP
        url = f"{self.endpoint_me}/root/delta?token=latest"
        resp = requests.get(url, headers=self.headers)
        return resp.json()

    def list_folder(self, path_rel_root: str) -> Union[List[DriveItem], Dict]:
        """
        :param path_rel_root: Path relative to root inside onedrive. It should exist
        If folder doesnt exist it will return the error response json. It can be an empty string in which case it will resolve to just the list_root() method
        """
        if path_rel_root == "":
            return self.list_root()

        if self.mode == "userpass":
            resp = requests.get(
                f"{self.endpoint_me}/root:/{path_rel_root}:/children",
                headers=self.headers,
            )
            if "error" in resp.json():
                return resp.json()

            items = self._create_driveitems(resp.json()["value"])

            return items

        else:
            resp = requests.get(
                f"{self.endpoint}/users/{self.username}/drive/root:/{path_rel_root}:/children",
                headers=self.headers,
            )
            if "error" in resp.json():
                return resp.json()

            items = self._create_driveitems(resp.json()["values"])
            print(items)

    def create_folder(self, path: str) -> DriveItem:
        """
        Create a folder under a given path
        :param path: should contain the (sub)folders followed by the folder name to create.
        For example, want to create a folder under Hello
        so `path = "Hello/newfolder". So a folder named newfolder under Hello/ will be created

        :param return: A driveitem containg the information about the uploaded folder
        """
        if not path:
            raise ValueError("Invalid path")

        path = path.split("/")

        headers = deepcopy(self.headers)
        headers.update({"Content-Type": "application/json"})

        body = {
            "name": path[-1],
            "@microsoft.graph.conflictBehavior": "rename",
            "folder": {},
        }

        if len(path) == 1:
            # its the root folder upload
            using_dir = "root"
        else:
            using_dir = f"root:/{'/'.join(path[:-1])}:"

        resp = requests.post(
            f"{self.endpoint_me}/{using_dir}/children", headers=headers, json=body
        )

        if resp.status_code != 201:
            raise Exception(f"Some Error\n\n{resp.json()}")

        return self._create_driveitems([resp.json()])

#%%
if __name__ == '__main__':
    config = json.load(open(os.path.abspath(""), "parameters.json"))
    user = OneDriveUser(config)
    print(user.list_root())