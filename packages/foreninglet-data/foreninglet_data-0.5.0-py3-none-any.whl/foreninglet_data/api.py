"""Class for connecting to ForeningLet API and retrieve users"""

import json
from functools import lru_cache
from os import environ

import requests
from dotenv import load_dotenv
from retry.api import retry_call

from foreninglet_data.activities import Activities

# Load environment variables from .env file
load_dotenv()

if environ.get("TEST_ENVIRONMENT"):
    from vcr import use_cassette
else:
    # Define a no-op decorator for production
    def use_cassette(*args, **kwargs):
        """Mocking decorator for production environment"""

        def decorator(func):
            return func

        return decorator


class ForeningLet:
    """
    Interface to the ForeningLet API
    Will take the following from environment variables:
    API_PASSWORD = The password for the ForeningLet API
    API_USERNAME = The username for the ForeningLet API
    API_BASE_URL = Base URL for the ForeningLet API
    API_MEMBERS_API = The endpoint for the ForeningLet Member API
    API_VERSION = The version of the ForeningLet Member API
    API_RESIGNED_MEMBERS_API = The endpoint for the ForeningLet Resigned Member API
    """

    api_username = ""
    api_password = ""
    api_base_url = ""
    api_members_path = ""
    api_activities_path = ""
    api_version = ""
    api_members_url = ""
    api_activities_url = ""
    api_resigned_members_url = ""
    membership_keywords = ""

    def __init__(self) -> None:
        self.api_password = environ.get("API_PASSWORD")
        self.api_username = environ.get("API_USERNAME")
        self.api_base_url = environ.get("API_BASE_URL")
        self.api_members_path = environ.get("API_MEMBERS_API")
        self.api_activities_path = environ.get("API_ACTIVITIES_API")
        self.api_version = environ.get("API_VERSION")
        self.api_resigned_members_path = environ.get("API_RESIGNED_MEMBERS_API")
        self.api_members_url = (
            f"{self.api_base_url}{self.api_members_path}?{self.api_version}"
        )
        self.api_resigned_members_url = (
            f"{self.api_base_url}{self.api_resigned_members_path}?{self.api_version}"
        )
        self.api_activities_url = (
            f"{self.api_base_url}{self.api_activities_path}?{self.api_version}"
        )
        self.membership_keywords = environ.get("MEMBERSHIP_KEYWORDS").split(",")

    def fl_api_get(self, url):
        """
        Retrieves data from an api endpoint
        authenticates with the class api_username and api_password
        """

        def _make_request():
            response = requests.get(
                url, auth=(self.api_username, self.api_password), timeout=60
            )
            response.raise_for_status()
            return response

        try:
            resp = retry_call(
                _make_request,
                exceptions=(
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.HTTPError,
                ),
                tries=3,
                delay=1,
                backoff=2,
                max_delay=10,
            )
        except Exception as e:
            print(f"Error connecting to API: {e}")
            raise
        return resp

    def check_api_responds(self):
        """Helper method to check the api endpoint responds"""
        resp = self.fl_api_get(self.api_members_url)
        return resp.status_code

    def get_memberlist(self):
        """Retrieves members from the member API endpoint"""
        resp = self.fl_api_get(self.api_members_url)
        return json.loads(resp.text)

    @use_cassette("tests/cassettes/test_data_fl_api_activities_anon.yaml")
    @lru_cache(maxsize=1280)
    def get_activities(self):
        """Retrieves all activities from the activities API endpoint"""
        resp = self.fl_api_get(self.api_activities_url)
        resp_dict = json.loads(resp.text)
        return resp_dict

    def get_resigned_members(self):
        """Retrieves resigned members from the resigned members API endpoint"""
        resp = self.fl_api_get(self.api_resigned_members_url)
        resp_dict = json.loads(resp.text)
        return resp_dict

    def get_memberships(self):
        """Returns a dictionary of memberships based on keywords identifying memberships"""
        activity_list = self.get_activities()
        activities = Activities(activity_list)
        membership_keywords = self.membership_keywords
        memberships = activities.identify_memberships(tuple(membership_keywords))
        return memberships
