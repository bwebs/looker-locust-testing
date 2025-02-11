import random
from locust import HttpUser, task, between
import looker_sdk
from looker_sdk import models40
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DASHBOARD_ID = "1"


class LookerUser(HttpUser):
    wait_time = between(1000, 2000)
    # This should match your Looker instance's embed domain
    host = os.environ.get("LOOKERSDK_BASE_URL")
    abstract = True  # This is a base class

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sdk = None
        self.user_id = "embed-" + str(random.randint(1000000000, 9999999999))
        self.store_id = random.randint(1, 7000)

    def on_start(self):
        # Initialize the SDK - make sure to set your environment variables
        self.sdk = looker_sdk.init40()
        sso_url = self.sdk.create_sso_embed_url(
            models40.EmbedSsoParams(
                external_user_id=self.user_id,
                session_length=2592000, # max seconds
                target_url=f"{os.environ.get('LOOKERSDK_BASE_URL')}/embed/dashboards/{DASHBOARD_ID}",
                permissions=[
                    "access_data",
                    "see_user_dashboards",
                    "see_lookml_dashboards",
                ],
                models=["az_load_test"],
                user_attributes={"store": self.store_id},
            )
        )

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(sso_url.url)

    def on_stop(self):
        self.driver.quit()


class DashboardUser(LookerUser):
    @task
    def get_dashboard_sso_url(self):
        # do nothing
        pass
