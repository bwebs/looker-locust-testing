from locust import User, between, task  # noqa
import os
from typing import List

import looker_sdk
from looker_sdk import models40
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from lkr.load_test.utils import (
    MAX_SESSION_LENGTH,
    PERMISSIONS,
    format_attributes,
    get_user_id,
)

__all__ = ["DashboardUser"]


class DashboardUser(User):
    abstract = True
    wait_time = between(1000, 2000)
    # This should match your Looker instance's embed domain
    host = os.environ.get("LOOKERSDK_BASE_URL")
    abstract = True  # This is a base class
    cleanup_user: bool = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sdk = None
        self.user_id = get_user_id()
        self.attributes: List[str] = []
        self.dashboard: str = ""
        self.models: List[str] = []
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=chrome_options)

    def on_start(self):
        # Initialize the SDK - make sure to set your environment variables
        self.sdk = looker_sdk.init40()
        attributes = format_attributes(self.attributes)

        sso_url = self.sdk.create_sso_embed_url(
            models40.EmbedSsoParams(
                first_name="Embed",
                last_name=self.user_id,
                external_user_id=self.user_id,
                session_length=MAX_SESSION_LENGTH,  # max seconds
                target_url=f"{os.environ.get('LOOKERSDK_BASE_URL')}/embed/dashboards/{self.dashboard}",
                permissions=PERMISSIONS,
                models=self.models,
                user_attributes=attributes,
            )
        )
        if sso_url and sso_url.url:
            self.driver.get(sso_url.url)
        else:
            raise Exception("Failed to get sso url")

    def on_stop(self):
        self.driver.quit()
        if self.cleanup_user and self.sdk and self.user_id:
            user = self.sdk.user_for_credential("embed", self.user_id, "id")

            if user and user.id:
                self.sdk.delete_user(user.id)
        return

    @task
    def do_nothing(self):
        pass
