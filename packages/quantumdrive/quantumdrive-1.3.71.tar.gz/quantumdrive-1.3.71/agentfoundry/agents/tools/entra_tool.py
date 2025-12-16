# entra_tool.py

import json
import logging
from threading import Lock

import msal
import requests
from pydantic import BaseModel, Field

from agentfoundry.utils.config import Config

# -------------------------------------------------------------------
# Logging setup
# -------------------------------------------------------------------
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

# Load configuration for Microsoft Graph credentials
CONFIG = Config()
CLIENT_ID = CONFIG.get("MS.CLIENT_ID", None)
TENANT_ID = CONFIG.get("MS.TENANT_ID", None)
# Determine if credentials are missing (tool will be disabled if so)
config_missing = not CLIENT_ID or not TENANT_ID

# Delegated scopes for reading mail & calendar
SCOPES = ["Mail.Read", "Calendars.Read"]

# Warn if credentials are missing (tool functionality will error on invocation)
if config_missing:
    logger.info("MS.CLIENT_ID and MS.TENANT_ID not set in configuration; entra_tool disabled.")
# Initialize MSAL cache and placeholders for lazy client initialization
_cache = msal.SerializableTokenCache()
_app = None
_lock = Lock()


def get_delegated_token() -> str:
    """
    Acquire or reuse an access token via device code flow.
    Blocks on first call to have user sign in; then uses cache.
    """
    # Ensure credentials are available and initialize MSAL client lazily
    if config_missing:
        raise RuntimeError("MS.CLIENT_ID and MS.TENANT_ID must be set in your configuration.")
    global _app
    if _app is None:
        _app = msal.PublicClientApplication(
            client_id=CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{TENANT_ID}",
            token_cache=_cache
        )
    with _lock:
        # Try silent first
        accounts = _app.get_accounts()
        if accounts:
            logger.debug(f"Attempting silent token acquisition for {accounts[0]['username']}")
            result = _app.acquire_token_silent(SCOPES, account=accounts[0])
            if result and "access_token" in result:
                logger.info(f"Reused token for {accounts[0]['username']}")
                return result["access_token"]

        # No cached token: start device code flow
        logger.info(f"Starting device code flow for scopes: {SCOPES}")
        flow = _app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            logger.error(f"Device flow initiation failed: {flow}")
            raise RuntimeError(f"Device flow error: {flow}")
        print(flow["message"])  # instruct user
        # Wait up to flow['expires_in'] seconds, polling internally
        result = _app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            logger.error(f"Device flow token error: {result}")
            raise RuntimeError(f"Device flow token error: {result.get('error_description', result)}")
        user = result.get("id_token_claims", {}).get("preferred_username", "<unknown>")
        logger.info(f"Acquired new token for {user}")
        return result["access_token"]

# -------------------------------------------------------------------
# Input model
# -------------------------------------------------------------------
class EntraInput(BaseModel):
    method: str = Field(..., description="HTTP method: GET, POST, etc.")
    path: str = Field(..., description="Graph API path, e.g. 'me/messages'")
    query_params: dict = Field(default_factory=dict)
    body: dict = Field(default_factory=dict)

# -------------------------------------------------------------------
# Core request
# -------------------------------------------------------------------
def make_entra_request(raw_input) -> dict:
    """
    Execute a delegated Graph request under /me.
    Accepts EntraInput or JSON/dict/string.
    """
    logger.info("make_entra_request invoked")
    # 1) Normalize input
    if isinstance(raw_input, EntraInput):
        inp = raw_input
        logger.debug(f"Using passed EntraInput: {inp}")
    else:
        try:
            # If it's a simple string GET path, wrap it
            if isinstance(raw_input, str) and not raw_input.strip().startswith("{"):
                method = "GET"
                path = raw_input.strip()
                inp = EntraInput(method=method, path=path)
                logger.debug(f"Wrapped raw string into EntraInput: {inp}")
            else:
                data = json.loads(raw_input) if isinstance(raw_input, str) else raw_input
                inp = EntraInput(**data)
                logger.debug(f"Parsed JSON into EntraInput: {data}")
        except Exception as e:
            logger.error(f"Failed to parse input: {e}", exc_info=True)
            return {"error": f"Invalid input for EntraInput: {e}"}

    method = inp.method.upper()
    if method not in {"GET","POST","PUT","PATCH","DELETE"}:
        logger.error(f"Unsupported HTTP method: {method}")
        return {"error": f"Unsupported HTTP method: {method}"}

    # 2) Force /me prefix
    raw_path = inp.path.lstrip("/")
    if raw_path.startswith("users/") or raw_path.startswith("https://"):
        # Strip users/{UPN} or full URL
        # e.g. users/alice@mail/...  → remove prefix up to /v1.0/
        parts = raw_path.split("/v1.0/",1)
        raw_path = parts[-1]
        logger.debug(f"Stripped full users path to: {raw_path}")
    if not raw_path.startswith("me/"):
        raw_path = f"me/{raw_path}"
        logger.debug(f"Prefixed path with 'me/': {raw_path}")

    url = f"https://graph.microsoft.com/v1.0/{raw_path}"
    logger.info(f"Prepared URL: {method} {url}")

    # 3) Get token
    try:
        token = get_delegated_token()
        logger.debug(f"Token length: {len(token)}")
    except Exception as e:
        return {"error": f"Token acquisition error: {e}"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json"
    }

    # 4) Perform HTTP call
    logger.debug(f"Headers: {headers}")
    logger.debug(f"Query params: {inp.query_params}, Body: {inp.body}")
    resp = None
    try:
        resp = requests.request(
            method,
            url,
            headers=headers,
            params=inp.query_params or None,
            json=inp.body or None,
            timeout=15
        )
        logger.info(f"HTTP {method} → status {resp.status_code}")
        resp.raise_for_status()
        if resp.status_code == 204:
            return {"message": "Success − no content"}
        data = resp.json()
        logger.debug(f"Response JSON: {data}")
        return data
    except requests.exceptions.HTTPError as e:
        if resp:
            message = resp.text
        else:
            message = "No response body"
        logger.error(f"Graph API error: {e}: response: ({message})")
        return {"error": str(e), "status": resp.status_code, "body": resp.text}
    except Exception as e:
        logger.exception("Unexpected error")
        return {"error": str(e)}

# -------------------------------------------------------------------
# LangChain tool export
# -------------------------------------------------------------------
if not config_missing:
    from langchain_core.tools import Tool

    entra_tool = Tool(
        name="entra_tool",
        func=make_entra_request,
        description="Calls Microsoft Graph under /me using delegated device-code authentication"
    )
