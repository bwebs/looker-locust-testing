import datetime
import os
import time
from typing import List

import looker_sdk
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


class RenderUser(User):
    abstract = True  # This is a base class
    wait_time = between(1, 15)
    host = os.environ.get("LOOKERSDK_BASE_URL")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sdk: Looker40SDK | None = None
        self.user_id = get_user_id()
        self.attributes: List[str] = []
        self.dashboard: str = ""
        self.models: List[str] = []
        self.result_format: str = "pdf"
        self._task_executed: bool = False
        self.render_bail_out: int = 120

    def _init_sdk(self):
        sdk = looker_sdk.init40()
        attributes = format_attributes(self.attributes)
        embed_session = sdk.acquire_embed_cookieless_session(
            models40.EmbedCookielessSessionAcquire(
                first_name="Embed",
                last_name=self.user_id,
                external_user_id=self.user_id,
                permissions=PERMISSIONS,
                models=self.models,
                user_attributes=attributes,
            )
        )
        looker_user = sdk.user_for_credential("embed",self.user_id)
        if not (looker_user and looker_user.id):
            raise Exception("Failed to create embed user")

        sdk.auth._sudo_id = looker_user.id

        return sdk

    def on_start(self):
        self.sdk = self._init_sdk()

    @task
    def render_dashboard(self):
        # Check if this user is configured to run its task only once and if it has already been executed.
        if hasattr(self, 'run_once') and self.run_once:
            if self._task_executed:
                return
            self._task_executed = True

        start_time = datetime.datetime.now()

        # Create render task
        render_task = self.sdk.create_dashboard_render_task(
            dashboard_id=self.dashboard,
            result_format=self.result_format,
            width=1920,
            height=1080,
            body=models40.CreateDashboardRenderTask(dashboard_style='tiled'),
            pdf_paper_size="a4",
            pdf_landscape=False,
            long_tables=True
        )

        # Poll for completion
        for _ in range(self.render_bail_out):
            task_status = self.sdk.render_task(render_task.id)
            if task_status.status == "success":
                break
            elif task_status.status == "failure":
                raise Exception(f"Render task failed detail: {task_status.status_detail}")
            time.sleep(1)

        complete_render_task = self.sdk.render_task(render_task.id)

        # TODO: optional flag to retrieve/process result
        # Get the results
        # results = self.sdk.render_task_results(render_task.id)

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(
            "render_dashboard",
            dashboard_id=self.dashboard,
            task_id=render_task.id,
            duration=duration,
            task_runtime=getattr(complete_render_task, 'runtime', None),
            task_render_runtime=getattr(complete_render_task, 'render_runtime', None),
            task_query_runtime=getattr(complete_render_task, 'query_runtime', None),
            status=task_status.status,
        )
