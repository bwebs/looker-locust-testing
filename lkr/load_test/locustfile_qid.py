import os
import random
import time
from typing import Dict, List

import looker_sdk
import requests
from locust import User, between, task  # noqa
from looker_sdk import models40
from looker_sdk.sdk.api40.methods import Looker40SDK

from lkr.load_test.utils import (
    MAX_SESSION_LENGTH,
    PERMISSIONS,
    format_attributes,
    get_user_id,
)

__all__ = ["QueryUser"]


def authenticate(sdk: Looker40SDK, user_id: str):
    sdk.auth.login_user(user_id, associative=False)
    token = sdk.auth._get_token(transport_options={"timeout": 60 * 5}).access_token
    sdk.auth.token.set_token(token)


class QueryUser(User):
    abstract = True
    wait_time = between(1, 15)
    # This should match your Looker instance's embed domain
    host = os.environ.get("LOOKERSDK_BASE_URL")
    abstract = True  # This is a base class

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sdk: Looker40SDK | None = None
        self.user_id = get_user_id()
        self.attributes: List[List[str]] = []
        self.qid: List[str] = []
        self.models: List[str] = []
        self.queries: Dict[str, models40.Query] = {}
        self.result_format: str = "json_bi"
        self.query_async: bool = False
        self.attributes: List[str] = []
        self.async_bail_out: int = 120

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
                target_url=f"{os.environ.get('LOOKERSDK_BASE_URL')}/browse",
                permissions=PERMISSIONS,
                models=self.models,
                user_attributes=attributes,
            )
        )
        # create the embed user with the credentials by hitting the URL
        _open_url = requests.get(sso_url.url)
        new_user = self.sdk.user_for_credential("embed", self.user_id)
        if not (new_user and new_user.id):
            raise Exception("Failed to create embed user")

        self.sdk.auth._sudo_id = new_user.id

    @task
    def run_query(self):
        query = random.choice(self.qid)
        if query not in self.queries:
            try:
                x = self.sdk.query_for_slug(query)
                self.queries[query] = x
            except Exception as e:
                print(e)
        if self.query_async:
            task = self.sdk.create_query_task(
                models40.WriteCreateQueryTask(
                    query_id=self.queries[query].id,
                    result_format=self.result_format,
                ),
                cache=False,
            )
            for _i in range(self.async_bail_out):
                check_task = self.sdk.query_task_results(task.id)
                print(check_task)
                if "rows" in check_task:
                    break
                elif "errors" in check_task:
                    raise Exception(check_task["errors"])
                else:
                    time.sleep(1)

        else:
            self.sdk.run_query(
                self.queries[query].id, result_format=self.result_format, cache=False
            )
