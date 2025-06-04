import base64
import json
import random
import re
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import structlog
import typer
from looker_sdk.sdk.api40 import models as models40

logger = structlog.get_logger()


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


def invalid_attribute_format(attr: str):
    typer.echo(f"Invalid attribute: {attr}")


def check_random_int_format(val: str) -> Tuple[bool, str | None]:
    if re.match(r"^random\.randint\(\d+,\d+\)$", val):
        # check if #  random.randint(0, 1000000) 0 and 100000 are integers
        numbers = re.findall(r"\d+", val.split("(")[1])
        if len(numbers) == 2:
            return True, str(
                random.randint(
                    int(numbers[0]),
                    int(numbers[1]),
                )
            )
        else:
            return False, None
    else:
        return False, None


def format_attributes(
    attributes: List[str] = [], seperator: str = ":"
) -> Dict[str, str]:
    formatted_attributes: Dict[str, str] = {}
    if attributes:
        for attr in attributes:
            valid = True
            split_attr = [x.strip() for x in attr.split(seperator) if x.strip()]
            if len(split_attr) == 2:
                val = split_attr[1]
                # regex to check if for string random.randint(0,1000000)
                is_valid, new_val = check_random_int_format(val)
                if is_valid and new_val is not None:
                    split_attr[1] = new_val
                    formatted_attributes[split_attr[0]] = split_attr[1]
                else:
                    valid = False
            else:
                valid = False
            if valid:
                formatted_attributes[split_attr[0]] = split_attr[1]
            else:
                invalid_attribute_format(attr)

    return formatted_attributes


def now():
    return datetime.now(timezone.utc)


def ms_diff(start: datetime, end: datetime | None = None):
    if end is None:
        end = now()
    return int((end - start).total_seconds() * 1000)


def extract_looker_user_id_from_token(
    response: models40.EmbedCookielessSessionAcquireResponse,
) -> int | None:
    if not (response and response.authentication_token):
        logger.error("No authentication token found")
        return None
    try:
        payload = response.authentication_token.split(".")[1]
        payload_bytes = base64.b64decode(payload)
        payload_json = json.loads(payload_bytes)
        credentials = json.loads(payload_json.get("credentials"))
        if not credentials:
            logger.error("No credentials found in authentication token")
            return None
        return int(credentials.get("user_id"))
    except Exception as e:
        logger.error("Failed to extract looker user id from token", error=e)
        return None
