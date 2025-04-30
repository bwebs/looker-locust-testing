import os
import urllib.parse
from datetime import datetime
from typing import List
from uuid import uuid4

import looker_sdk
import structlog
from locust import User, between, task  # noqa
from looker_sdk import models40
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from lkr.load_test.utils import (
    MAX_SESSION_LENGTH,
    PERMISSIONS,
    format_attributes,
    get_user_id,
    log_event,
    ms_diff,
    now,
)

logger = structlog.get_logger()

__all__ = ["DashboardUserObservability"]


class DashboardUserObservability(User):
    abstract = True
    wait_time = between(1000, 2000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sdk = None
        self.user_id = get_user_id()
        self.attributes: List[str] = []
        self.dashboard: str = ""
        self.models: List[str] = []
        self.task_start_time = None
        self.completion_timeout = 120
        self.embed_domain = "http://localhost:3000"
        self.log_event_prefix = "looker-embed-observability"
        self.do_not_open_url = False

    def get_sso_url(self):
        attributes = format_attributes(self.attributes)

        sso_url = self.sdk.create_sso_embed_url(
            models40.EmbedSsoParams(
                first_name="Embed",
                last_name=self.user_id,
                external_user_id=self.user_id,
                session_length=MAX_SESSION_LENGTH,  # max seconds
                target_url=f"{os.environ.get('LOOKERSDK_BASE_URL')}/embed/dashboards/{self.dashboard}?embed_domain={self.embed_domain}",
                permissions=PERMISSIONS,
                models=self.models,
                user_attributes=attributes,
                embed_domain=self.embed_domain,
            )
        )
        return sso_url

    def on_start(self):
        # Initialize the SDK - make sure to set your environment variables
        self.sdk = looker_sdk.init40()

    def on_stop(self):
        pass

    @task
    def open_embed_dashboard(self):
        task_id = str(uuid4())
        task_start_time = now()
        common_log_kwargs = {
            "user_id": self.user_id,
            "dashboard": self.dashboard,
            "task_start_time": task_start_time.isoformat(),
            "task_id": task_id,
        }
        log_event(
            "user_task_start",
            self.log_event_prefix,
            duration_ms=ms_diff(task_start_time),
            **common_log_kwargs,
        )
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=chrome_options)
        driver_loaded_time = log_event(
            "user_task_chromium_driver_loaded",
            self.log_event_prefix,
            duration_ms=ms_diff(task_start_time),
            **common_log_kwargs,
        )
        sso_url = self.get_sso_url()
        sso_url_generated_time = log_event(
            "user_task_sso_url_generated",
            self.log_event_prefix,
            duration_ms=ms_diff(task_start_time),
            **common_log_kwargs,
            **driver_loaded_time.make_previous(),
        )
        quoted_url = urllib.parse.quote(sso_url.url, safe="")
        # Open the local embed container with the SSO URL as a parameter
        embed_url = f"{self.embed_domain}/?iframe_url={quoted_url}&dashboard_id={self.dashboard}&user_id={self.user_id}&task_id={task_id}"
        if not self.do_not_open_url:
            driver.get(embed_url)
        else:
            logger.info(
                f"{self.log_event_prefix}:looker_embed_task_not_opening_url",
                user_id=self.user_id,
                dashboard=self.dashboard,
                embed_url=sso_url.url,
                observability_url=embed_url,
            )
        chromium_get = log_event(
            "user_task_embed_chromium_get",
            self.log_event_prefix,
            embed_url=embed_url,
            **common_log_kwargs,
            **sso_url_generated_time.make_previous(),
        )
        # Store task start time

        # Wait for the completion indicator to appear (with a timeout)
        try:
            WebDriverWait(driver, self.completion_timeout).until(
                EC.presence_of_element_located((By.ID, "completion-indicator"))
            )

            # Log completion
            logger.info(
                f"{self.log_event_prefix}:looker_embed_task_complete",
                user_id=self.user_id,
                dashboard=self.dashboard,
                timestamp=datetime.now().isoformat(),
                duration_ms=int(
                    (now() - task_start_time).total_seconds() * 1000
                ),
                **chromium_get.make_previous(),
            )

        except TimeoutException:
            logger.error(
                f"{self.log_event_prefix}:looker_embed_task_timeout",
                user_id=self.user_id,
                dashboard=self.dashboard,
                timestamp=now().isoformat(),
                timeout=self.completion_timeout,
                duration_ms=ms_diff(task_start_time),
            )
        except Exception as e:
            logger.error(
                f"{self.log_event_prefix}:looker_embed_task_error",
                user_id=self.user_id,
                dashboard=self.dashboard,
                error=e,
            )
        finally:
            driver.quit()
