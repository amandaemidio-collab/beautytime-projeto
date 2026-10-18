"""Central configuration for the Xano API groups used by the frontend."""

API_BASE_URLS = {
    "authentication": "https://x8ki-letl-twmt.n7.xano.io/api:2v0zlfeT",
    "members_accounts": "https://x8ki-letl-twmt.n7.xano.io/api:EYm7vjJ1",
}


def api_url(api_group: str, path: str) -> str:
    """Build a URL for an endpoint in a configured Xano API group."""
    return f"{API_BASE_URLS[api_group].rstrip('/')}/{path.lstrip('/')}"
