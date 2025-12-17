# Copyright 2025 Clivern
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
from dataclasses import dataclass
from urllib.parse import urlencode
from veee.platform.integration import Integration


@dataclass
class LinkedinPost:
    """
    Linkedin Post Message
    """

    text: str
    visibility: str

    def as_dict(self):
        """
        Convert the Linkedin Post to a dictionary

        Returns:
            dict: The Linkedin Post as a dictionary
        """
        return {
            "text": self.text,
            "visibility": self.visibility.upper(),
        }


class Linkedin(Integration):
    """
    LinkedIn Platform
    """

    VERSION = "0.0.1"
    TYPE = "linkedin"

    def __init__(self, config: dict):
        """
        Initialize the LinkedIn platform

        Args:
            config (dict): The configuration
        """
        self._client_id = config.get("client_id")
        self._client_secret = config.get("client_secret")
        self._app_redirect_uri = config.get("app_redirect_uri")
        self._app_scope = config.get(
            "app_scope",
            "openid profile w_member_social r_basicprofile rw_organization_admin w_organization_social r_organization_social",
        )
        self._api_url = config.get("api_url", "https://api.linkedin.com/v2")
        self._oauth_url = config.get("oauth_url", "https://www.linkedin.com/oauth/v2")

    def get_oauth_redirect_url(self, data: dict) -> str:
        """
        Get the OAuth redirect URL

        Args:
            data (dict): The data to be used to generate the OAuth redirect URL

        Returns:
            str: The OAuth redirect URL
        """
        state = data.get("state", "")

        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": self._app_redirect_uri,
            "state": state,
            "scope": self._app_scope,
        }

        return f"{self._oauth_url}/authorization?{urlencode(params)}"

    def get_access_tokens(self, data: dict) -> dict:
        """
        Get the access tokens (access_token, refresh_token, expires_in)

        Args:
            data (dict): The data to be used to get the access tokens

        Returns:
            dict: The access tokens
        """
        code = data.get("code", "")

        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._app_redirect_uri,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

        response = requests.post(
            f"{self._oauth_url}/accessToken",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=token_data,
        )
        response.raise_for_status()
        return response.json()

    def get_user_info(self, access_token: str) -> dict:
        """
        Get the user info

        Args:
            access_token (str): The access token

        Returns:
            dict: The user info
        """
        # Get userinfo
        userinfo_response = requests.get(
            f"{self._api_url}/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()

        # Get profile for vanity name
        profile_response = requests.get(
            f"{self._api_url}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_response.raise_for_status()
        profile_info = profile_response.json()

        return {
            "id": user_info.get("sub"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture", ""),
            "username": profile_info.get("vanityName", ""),
        }

    def rotate_access_tokens(self, refresh_token: str) -> dict:
        """
        Rotate the access tokens

        Args:
            refresh_token (str): The refresh token

        Returns:
            dict: The access tokens
        """
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

        response = requests.post(
            f"{self._oauth_url}/accessToken",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=token_data,
        )
        response.raise_for_status()
        return response.json()

    def post(self, access_token: str, message: dict) -> dict:
        """
        Post to LinkedIn

        Args:
            access_token (str): The access token
            message (dict): The message to be posted
                {
                    "text": "Post text",
                    "visibility": "PUBLIC" or "CONNECTIONS"
                }

        Returns:
            dict: The response from LinkedIn
        """
        # Get user's person URN
        profile_response = requests.get(
            f"{self._api_url}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_response.raise_for_status()
        profile_info = profile_response.json()
        author_urn = f"urn:li:person:{profile_info.get('id')}"

        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": message.get("text", ""),
                    },
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": message.get(
                    "visibility", "PUBLIC"
                ),
            },
        }

        response = requests.post(
            f"{self._api_url}/ugcPosts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            json=post_data,
        )
        response.raise_for_status()
        return response.json()

    def get_account_analytics(self, access_token: str, options: dict = {}) -> list:
        """
        Get the account analytics of the integration

        Args:
            access_token (str): The access token
            options (dict, optional): Options dictionary for analytics query

        Returns:
            list: The account analytics
        """
        pass

    def get_post_analytics(
        self, access_token: str, post_id: str, options: dict = {}
    ) -> list:
        """
        Get the post analytics of the integration

        Args:
            access_token (str): The access token
            post_id (str): The post ID
            options (dict, optional): Options dictionary for analytics query

        Returns:
            list: The post analytics
        """
        pass

    def version(self) -> str:
        return self.VERSION

    def get_type(self) -> str:
        return self.TYPE
