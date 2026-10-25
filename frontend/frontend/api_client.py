"""Small JSON client for requests to the Xano API."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_json(
    method: str,
    url: str,
    payload: dict[str, object] | None = None,
    token: str = "",
) -> tuple[int, dict[str, object]]:
    """Send one JSON request and return its HTTP status and decoded object."""
    status, data = _request_json(method, url, payload, token)
    if isinstance(data, dict):
        return status, data
    return status, {"message": "A API retornou uma resposta inválida."}


def request_json_list(
    method: str,
    url: str,
    payload: dict[str, object] | None = None,
    token: str = "",
) -> tuple[int, dict[str, object] | list[object]]:
    """Send one JSON request that may return a JSON array."""
    return _request_json(method, url, payload, token)


def _request_json(
    method: str,
    url: str,
    payload: dict[str, object] | None = None,
    token: str = "",
) -> tuple[int, dict[str, object] | list[object]]:
    headers = {"Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=15) as response:
            status = response.status
            response_body = response.read()
    except HTTPError as error:
        status = error.code
        response_body = error.read()
    except (URLError, TimeoutError) as error:
        reason = getattr(error, "reason", error)
        return 0, {"message": f"Não foi possível conectar à API: {reason}"}

    if not response_body:
        return status, {}

    try:
        data = json.loads(response_body)
    except json.JSONDecodeError:
        return status, {"message": "A API retornou uma resposta inválida."}

    if not isinstance(data, (dict, list)):
        return status, {"message": "A API retornou uma resposta inválida."}
    return status, data
