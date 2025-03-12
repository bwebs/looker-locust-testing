import datetime
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, List

import looker_sdk
import requests
from locust import User, between, task  # noqa
from looker_sdk import models40
from looker_sdk.sdk.api40.methods import Looker40SDK
from structlog import get_logger

from lkr.load_test.utils import (
    MAX_SESSION_LENGTH,
    PERMISSIONS,
    format_attributes,
    get_user_id,
)

logger = get_logger(__name__)


@dataclass
class TimingStats:
    start: datetime.datetime | None = None
    init_sdk: datetime.datetime | None = None
    lookup_query: datetime.datetime | None = None
    query: datetime.datetime | None = None
    task: datetime.datetime | None = None
    finish_task: datetime.datetime | None = None
    run_query: datetime.datetime | None = None
    end: datetime.datetime | None = None

    def log_steps(self) -> Dict[str, float]:
        out = {}
        if self.init_sdk:
            out["init_sdk"] = (self.init_sdk - self.start).total_seconds()
        if self.lookup_query:
            out["lookup_query"] = (
                self.lookup_query - (self.init_sdk or self.start)
            ).total_seconds()
        if self.task:
            out["task"] = (
                self.task - (self.lookup_query or self.init_sdk or self.start)
            ).total_seconds()
        if self.finish_task:
            out["finish_task"] = (self.finish_task - self.task).total_seconds()
        if self.run_query:
            out["run_query"] = (
                self.run_query
                - (
                    self.finish_task
                    or self.task
                    or self.lookup_query
                    or self.init_sdk
                    or self.start
                )
            ).total_seconds()
        return out


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
        self.sticky_sessions: bool = False

    def _init_sdk(self):
        sdk = looker_sdk.init40()
        attributes = format_attributes(self.attributes)
        sso_url = sdk.create_sso_embed_url(
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
        new_user = sdk.user_for_credential("embed", self.user_id)
        if not (new_user and new_user.id):
            raise Exception("Failed to create embed user")

        sdk.auth._sudo_id = new_user.id
        return sdk

    def on_start(self):
        # Initialize the SDK - make sure to set your environment variables
        if self.sticky_sessions:
            self.sdk = self._init_sdk()

    @task
    def run_query(self):
        ts: TimingStats = TimingStats()
        ts.start = datetime.datetime.now()
        if not self.sdk:
            sdk = self._init_sdk()
            ts.init_sdk = datetime.datetime.now()
        else:
            sdk = self.sdk
        query = random.choice(self.qid)

        if self.query_async:
            if query not in self.queries:
                try:
                    x = sdk.query_for_slug(query)
                    self.queries[query] = x
                    ts.lookup_query = datetime.datetime.now()
                except Exception as e:
                    print(e)

            task = sdk.create_query_task(
                models40.WriteCreateQueryTask(
                    query_id=self.queries[query].id,
                    result_format=self.result_format,
                ),
                cache=False,
            )
            ts.task = datetime.datetime.now()
            for _i in range(self.async_bail_out):
                finish_task = sdk.query_task_results(task.id)
                if "rows" in finish_task:
                    break
                elif "errors" in finish_task:
                    raise Exception(finish_task["errors"])
                else:
                    time.sleep(1)
            ts.finish_task = datetime.datetime.now()

        else:
            sdk.run_query(query, result_format=self.result_format, cache=False)
            ts.run_query = datetime.datetime.now()
        ts.end = datetime.datetime.now()
        logger.info(
            "run_query",
            time_taken=(ts.end - ts.start).total_seconds(),
            steps=ts.log_steps(),
        )
