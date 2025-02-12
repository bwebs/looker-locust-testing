import random
from typing import List

import typer

MAX_SESSION_LENGTH = 2592000

PERMISSIONS = [
    "access_data",
    "see_user_dashboards",
    "see_lookml_dashboards",
    "see_looks",
    "explore",
]


def get_user_id() -> str:
    return "embed-" + str(random.randint(1000000000, 9999999999))


def format_attributes(attributes: List[str] = []) -> List[List[str]]:
    formatted_attributes: List[List[str]] = []
    if attributes:
        for attr in attributes:
            split_attr = [x.strip() for x in attr.split(":") if x.strip()]
            if len(split_attr) == 2:
                formatted_attributes.append(split_attr)
            else:
                typer.echo(f"Invalid attribute: {attr}")

    return formatted_attributes
