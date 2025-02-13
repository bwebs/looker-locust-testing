import locust  # noqa
import os
import pathlib
import random
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, List, Optional

import looker_sdk
import typer
from dotenv import load_dotenv

from lkr.load_test.locustfile_dashboard import DashboardUser
from lkr.load_test.utils import format_attributes
from lkr.utils.validate_api import validate_api_credentials

from lkr.load_test.locustfile_qid import QueryUser


app = typer.Typer(name="lkr")
state = {"client_id": False}

LOAD_TEST_PATH = pathlib.Path("lkr", "load_test")


class LoadTestType(str, Enum):
    dashboard = "dashboard"
    query = "query"


class DebugType(str, Enum):
    looker = "looker"


@dataclass
class LookerApiCredentials:
    client_id: str
    client_secret: str
    base_url: str


@app.callback()
def main(
    ctx: typer.Context,
    env_file: Annotated[
        Optional[pathlib.Path],
        typer.Option(
            help="Path to the environment file to load",
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
        ),
    ] = pathlib.Path(os.getcwd(), ".env"),
    client_id: Annotated[
        str,
        typer.Option(help="Looker API client ID"),
    ] = None,
    client_secret: Annotated[
        str,
        typer.Option(help="Looker API client secret"),
    ] = None,
    base_url: Annotated[
        str,
        typer.Option(help="Looker API base URL"),
    ] = None,
):
    load_dotenv(dotenv_path=env_file, override=True)
    if ctx.invoked_subcommand in ["load-test", "debug"]:
        validate_api_credentials(
            client_id=client_id, client_secret=client_secret, base_url=base_url
        )


@app.command()
def hello(hidden=True):
    """
    Say hello, world!
    """
    print("Hello, World!")


@app.command()
def debug(
    type: Annotated[
        DebugType,
        typer.Argument(help="Type of debug to run (looker)"),
    ],
):
    """
    Check that the environment variables are set correctly
    """

    if type.value == "looker":
        typer.echo("Looking at the looker environment variables")
        if os.environ.get("LOOKERSDK_CLIENT_ID"):
            typer.echo(f"LOOKERSDK_CLIENT_ID: {os.environ.get('LOOKERSDK_CLIENT_ID')}")
        else:
            typer.echo("LOOKERSDK_CLIENT_ID: Not set")
        if os.environ.get("LOOKERSDK_CLIENT_SECRET"):
            typer.echo("LOOKERSDK_CLIENT_SECRET: *********")
        else:
            typer.echo("LOOKERSDK_CLIENT_SECRET: Not set")
        if os.environ.get("LOOKERSDK_BASE_URL"):
            typer.echo(f"LOOKERSDK_BASE_URL: {os.environ['LOOKERSDK_BASE_URL']}")
        else:
            typer.echo("LOOKERSDK_BASE_URL: Not set")

        typer.echo("\nChecking Looker Credentials\n")
        try:
            looker_client = looker_sdk.init40()
            response = looker_client.me()
            typer.echo(f"Logged in as {response['first_name']} {response.last_name}")
        except Exception as e:
            typer.echo(f"Error logging in to Looker: {str(e)}")


@app.command(name="load-test")
def load_test(
    users: Annotated[
        int, typer.Option(help="Number of users to run the test with", min=1, max=1000)
    ] = 25,
    spawn_rate: Annotated[
        float,
        typer.Option(help="Number of users to spawn per second", min=0, max=100),
    ] = 1,
    run_time: Annotated[
        int,
        typer.Option(help="How many minutes to run the load test for", min=1),
    ] = 5,
    dashboard: Annotated[
        str,
        typer.Option(
            help="Dashboard ID to run the test on. Keeps dashboard open for user, turn on auto-refresh to keep dashboard updated"
        ),
    ] = None,
    qid: Annotated[
        str,
        typer.Option(help="Query ID (from explore url) to run the test on"),
    ] = None,
    model: Annotated[
        List[str],
        typer.Option(
            help="Model to run the test on. Specify multiple models as --model model1 --model model2"
        ),
    ] = None,
    attribute: Annotated[
        List[str],
        typer.Option(
            help="Looker attributes to run the test on. Specify them as attribute:value like --attribute store:value. Excepts multiple arguments --attribute store:acme --attribute team:managers"
        ),
    ] = None,
):
    from locust import events
    from locust.env import Environment

    """
    Run a load test on a dashboard or API query
    """
    if not (dashboard or qid):
        raise typer.BadParameter("Either --dashboard or --qid must be provided")

    if not model:
        raise typer.BadParameter("At least one --model must be provided")

    typer.echo(
        f"Running load test with {users} users, {spawn_rate} spawn rate, and {run_time} minutes"
    )

    # Process attributes into the expected format

    class DashboardUserClass(DashboardUser):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attributes = attribute
            self.dashboard = dashboard
            self.models = model

    class QueryUserClass(QueryUser):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attributes = format_attributes(attribute)
            self.qid = qid
            self.models = model

    env = Environment(
        user_classes=[DashboardUserClass] if dashboard else [QueryUserClass],
        events=events,
    )
    runner = env.create_local_runner()
    # gevent.spawn(stats_printer(env.stats))
    runner.start(user_count=users, spawn_rate=spawn_rate)

    def quit_runner():
        runner.greenlet.kill()
        runner.quit()
        typer.Exit(1)

    runner.spawning_greenlet.spawn_later(run_time * 60, quit_runner)
    runner.greenlet.join()


@app.command(name="test-qid", hidden=True)
def test_qid(
    user_id: Annotated[
        str,
        typer.Argument(help="User ID to run the test on"),
    ],
    qid: Annotated[
        str,
        typer.Argument(help="Query ID (from explore url) to run the test on"),
    ],
):
    from looker_sdk import models40

    from .load_test.utils import PERMISSIONS

    sdk = looker_sdk.init40()
    new_user = sdk.create_embed_user(
        models40.CreateEmbedUserRequest(
            external_user_id=user_id,
        )
    )

    token = sdk.acquire_embed_cookieless_session(
        models40.EmbedCookielessSessionAcquire(
            external_user_id=user_id,
            first_name="test",
            last_name="test",
            session_length=1000,  # max seconds
            models=["az_test"],
            permissions=PERMISSIONS,
        )
    )

    token = sdk.login_user(new_user.id, associative=False)
    sdk.auth.sudo_token.set_token(token)

    q = sdk.query(qid)
    x = sdk.run_query(
        q.id, result_format="csv", cache=False, limit=random.randint(1, 5000)
    )
    print(x)


if __name__ == "__main__":
    typer.run(app)
