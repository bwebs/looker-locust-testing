import os


def validate_api_credentials(
    *,
    client_id: str | None = None,
    client_secret: str | None = None,
    base_url: str | None = None,
):
    os.environ["LOOKERSDK_CLIENT_ID"] = (
        client_id if client_id else os.environ.get("LOOKERSDK_CLIENT_ID", "")
    )
    os.environ["LOOKERSDK_CLIENT_SECRET"] = (
        client_secret
        if client_secret
        else os.environ.get("LOOKERSDK_CLIENT_SECRET", "")
    )
    os.environ["LOOKERSDK_BASE_URL"] = (
        base_url if base_url else os.environ.get("LOOKERSDK_BASE_URL", "")
    )
    if not os.environ.get("LOOKERSDK_CLIENT_ID"):
        raise ValueError("LOOKERSDK_CLIENT_ID is not set")
    if not os.environ.get("LOOKERSDK_CLIENT_SECRET"):
        raise ValueError("LOOKERSDK_CLIENT_SECRET is not set")
    if not os.environ.get("LOOKERSDK_BASE_URL"):
        raise ValueError("LOOKERSDK_BASE_URL is not set")
