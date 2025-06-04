import datetime
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, List

import looker_sdk
from locust import User, between, task  # noqa
from looker_sdk import models40
from looker_sdk.sdk.api40.methods import Looker40SDK
from structlog import get_logger

from lkr.load_test.utils import (
    MAX_SESSION_LENGTH,
    PERMISSIONS,
    extract_looker_user_id_from_token,
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
        if self.init_sdk and self.start:
            out["init_sdk"] = (self.init_sdk - self.start).total_seconds()
        if self.lookup_query and (self.init_sdk or self.start):
            base = self.init_sdk if self.init_sdk else self.start
            if base:
                out["lookup_query"] = (self.lookup_query - base).total_seconds()
        if self.task and (self.lookup_query or self.init_sdk or self.start):
            base = self.lookup_query or self.init_sdk or self.start
            if base:
                out["task"] = (self.task - base).total_seconds()
        if self.finish_task and self.task:
            out["finish_task"] = (self.finish_task - self.task).total_seconds()
        if self.run_query:
            base = (
                self.finish_task
                or self.task
                or self.lookup_query
                or self.init_sdk
                or self.start
            )
            if base:
                out["run_query"] = (self.run_query - base).total_seconds()
        return out


__all__ = ["QueryUser"]


def authenticate(sdk: Looker40SDK, user_id: str):
    # login_user expects an int sudo_id, so get the user object first
    user = sdk.user_for_credential("embed", user_id)
    if not user or not user.id or not isinstance(user.id, int):
        raise Exception("User not found or id is not an int")
    sdk.auth.login_user(user.id)
    token = sdk.auth._get_token(transport_options={"timeout": 60 * 5})
    # Do not call set_token here: _get_token returns AuthToken, but set_token expects AccessToken.
    # This is a no-op to avoid type errors.


class QueryUser(User):
    abstract = True
    wait_time = between(1, 15)
    # This should match your Looker instance's embed domain
    host = os.environ.get("LOOKERSDK_BASE_URL")
    abstract = True  # This is a base class
    cleanup_user: bool = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sdk: Looker40SDK | None = None
        self.user_id = get_user_id()
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
        embed_session = sdk.acquire_embed_cookieless_session(
            models40.EmbedCookielessSessionAcquire(
                first_name="Embed",
                last_name=self.user_id,
                external_user_id=self.user_id,
                session_length=MAX_SESSION_LENGTH,  # max seconds
                permissions=PERMISSIONS,
                models=self.models,
                user_attributes=attributes,
            )
        )
        looker_user_id = extract_looker_user_id_from_token(embed_session)
        if not looker_user_id:
            embed_user = sdk.user_for_credential("embed", self.user_id)
            if not embed_user or not embed_user.id:
                raise Exception("Failed to create embed user")
            looker_user_id = int(embed_user.id)
        if not looker_user_id:
            raise Exception("Failed to extract looker user id from token")
        sdk.auth.login_user(looker_user_id)
        return sdk

    def on_start(self):
        # Initialize the SDK - make sure to set your environment variables
        if self.sticky_sessions:
            self.sdk = self._init_sdk()

    def on_stop(self):
        if self.cleanup_user and self.sdk and self.user_id:
            user = self.sdk.user_for_credential("embed", self.user_id, "id")
            if user and user.id:
                self.sdk.delete_user(user.id)

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
            query_obj = self.queries[query]
            if not query_obj or not query_obj.id:
                raise Exception("Query object or its id is None")
            # Use the correct ResultFormat enum if available, else raise
            if hasattr(models40, "ResultFormat"):
                try:
                    result_format = models40.ResultFormat(self.result_format)
                except Exception:
                    raise Exception(f"Invalid result_format: {self.result_format}")
            else:
                raise Exception("models40.ResultFormat not available")
            task = sdk.create_query_task(
                models40.WriteCreateQueryTask(
                    query_id=query_obj.id,
                    result_format=result_format,
                ),
                cache=False,
            )
            ts.task = datetime.datetime.now()
            if (
                not task
                or not getattr(task, "id", None)
                or not isinstance(task.id, str)
            ):
                raise Exception("Query task or its id is None or not a string")
            for _i in range(self.async_bail_out):
                finish_task = sdk.query_task_results(task.id)
                if isinstance(finish_task, dict):
                    if "rows" in finish_task:
                        break
                    errors = finish_task.get("errors")
                    if errors is not None:
                        raise Exception(str(errors))
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
