import os
import random
from typing import List

import looker_sdk
from locust import User, between, task  # noqa
from looker_sdk import models40

from lkr.load_test.utils import MAX_SESSION_LENGTH, PERMISSIONS, get_user_id

__all__ = ["QueryUser"]


class QueryUser(User):
    abstract = True
    wait_time = between(1, 15)
    # This should match your Looker instance's embed domain
    host = os.environ.get("LOOKERSDK_BASE_URL")
    abstract = True  # This is a base class

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sdk = None
        self.user_id = get_user_id()
        self.attributes: List[List[str]] = []
        self.qid: str = ""
        self.models: List[str] = []

    def on_start(self):
        # Initialize the SDK - make sure to set your environment variables
        self.sdk = looker_sdk.init40()
        new_user = self.sdk.create_embed_user(
            models40.CreateEmbedUserRequest(
                external_user_id=self.user_id,
            )
        )
        self.sdk.acquire_embed_cookieless_session(
            models40.EmbedCookielessSessionAcquire(
                external_user_id=self.user_id,
                session_length=MAX_SESSION_LENGTH,  # max seconds
                user_attributes={attr[0]: attr[1] for attr in self.attributes},
                models=self.models,
                permissions=PERMISSIONS,
            )
        )
        token = self.sdk.login_user(new_user.id, associative=True)
        self.sdk.auth.sudo_token.set_token(token)

    def on_stop(self):
        self.driver.quit()

    @task
    def run_query(self):
        q = self.sdk.query(self.qid)
        self.sdk.run_query(
            q.id, result_format="csv", cache=False, limit=random.randint(1, 5000)
        )
