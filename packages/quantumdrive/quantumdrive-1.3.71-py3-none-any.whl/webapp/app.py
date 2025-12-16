import os
import sys
import logging
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler
from os.path import exists
from typing import Dict, Optional

import requests
from flask import Flask, Response, make_response, render_template, request, redirect, session, url_for
from langchain.chat_models import init_chat_model
import msal


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print(f"Project root: {project_root}")
sys.path.insert(0, project_root)

from core.utils.app_config import AppConfig
AppConfig.load()

from agentfoundry.utils.config import Config
from agentfoundry.registry.tool_registry import ToolRegistry
from agentfoundry.agents.tool_autonomy_agent import ToolAutonomyAgent
from agentfoundry.utils.logger import get_logger
from core.auth.microsoft_sso import MicrosoftSSO

"""
app.py

A simple Flask web application demo for agentfoundry.
This demo includes:
  - A dashboard overview
  - System details view
  - A task execution form that uses the Tool Autonomy Agent to process tasks
  - A reports view displaying dummy compliance and fairness metrics
"""


app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with a secure key for session management

# MSAL configuration
CLIENT_ID = "36fa3e1c-1eac-4f0d-87ae-9651c81d1f42"  # From Azure AD
TENANT_ID = "317c1c26-22fe-4b7b-abfa-54aa9952946f"  # From Azure AD
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "https://quantumdrive.alphasixdemo.com/callback"  # Must match Azure AD redirect URI

SCOPES = ["User.Read", "User.ReadBasic.All", "Analytics.Read", "Tasks.Read"]  # Permissions requested

# Initialize MSAL
token_cache = msal.SerializableTokenCache()
msal_app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential="GJI8Q~SaMNUHnjSfnMYvSAAKDaU.G.WO7QmJYarf",
    authority=AUTHORITY,
    token_cache=token_cache
)

# Configure logging (optional)
# ── configure a rotating file handler on the root logger
logs_dir = os.path.join(project_root, "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "quantumdrive.log")
rotating_handler = RotatingFileHandler(
    filename=log_file,
    maxBytes=10 * 1024 * 1024,   # rotate after 10 MB
    backupCount=5,               # keep up to 5 old log files
    encoding="utf-8"
)
rotating_handler.setLevel(logging.INFO)
rotating_handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")
)

# attach to the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(rotating_handler)
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('msal').setLevel(logging.INFO)
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

open_api_key = AppConfig.get("OPENAI_API_KEY")
print(f"OpenAI API Key: {open_api_key}")
logger.info(f"OpenAI API Key: {open_api_key}")
os.environ["OPENAI_API_KEY"] = open_api_key

# Instantiate the tool registry.
registry = ToolRegistry()

# Register the registry tool (so the LLM can inspect available tools if needed).
registry_tool = registry.as_langchain_registry_tool()
try:
    registry.register_tool(registry_tool)
except ValueError as e:
    logger.debug(str(e))

# Instantiate the Tool Autonomy Agent with the registry and LLM.
#model = ChatOpenAI(model="gpt-4o", api_key=AppConfig.get("openai_api_key"))
llm = init_chat_model("o3-mini", model_provider="openai")
autonomy_agent = ToolAutonomyAgent(tool_registry=registry, llm=llm)


def refresh_access_token(self):
    """Refresh the access token using the refresh token stored in the session."""
    refresh_token = session.get("refresh_token")
    if not refresh_token:
        self.logger.error("No refresh token available in session")
        return None
    result = msal_app.acquire_token_by_refresh_token(refresh_token, scopes=SCOPES)
    if "access_token" in result:
        session["access_token"] = result["access_token"]
        session["refresh_token"] = result.get("refresh_token", refresh_token)  # Update if new refresh token provided
        return result["access_token"]
    return None


def get_user_info(self) -> Optional[Dict[str, str]]:
    access_token = session.get("access_token")
    if not access_token:
        access_token = self.refresh_access_token()
        if not access_token:
            self.logger.error("No access token available in session and refresh failed")
            return None


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Request URL: {request.url}, f: {f}, Args: {args}, Kwargs: {kwargs}")
        if request.url.startswith("http://localhost:5000"):
            session["account"] = "Account"
            session["access_token"] = "access_token"
            session["refresh_token"] = "refresh_token"
            session["name"] = "Chris Steel"
            session["email"] = "chris.steel@alphsix.com"
            return f(*args, **kwargs)
        account = session.get("account")
        if not account:
            logger.info(f"Account not in session: {session}")
            # Pass the original URL as a query parameter to /login
            login_url = url_for('login', next=request.url, _external=True)
            return redirect(login_url)
        result = msal_app.acquire_token_silent(scopes=SCOPES, account=account)
        if not result:
            logger.info(f"No result from acquire_token_silent: {result}")
            login_url = url_for('login', next=request.url, _external=True)
            return redirect(login_url)
        if "access_token" in result:
            session["access_token"] = result["access_token"]
        else:
            login_url = url_for('login', next=request.url, _external=True)
            return redirect(login_url)
        return f(*args, **kwargs)
    return decorated_function


@app.route("/health")
def health():
    """Health check endpoint for load balancer, no authentication required."""
    return Response("OK", status=200)


@app.route("/login")
def login():
    """Redirect the user to Microsoft's authorization endpoint."""
    # logger.info(f"Session: {session}")
    # Get the 'next' parameter from the query string, default to dashboard
    next_url = request.args.get('next', url_for('dashboard', _external=True))
    logger.info(f"Login next URL from query: {next_url}")
    auth_url = msal_app.get_authorization_request_url(
        SCOPES,
        redirect_uri=REDIRECT_URI,
        state=next_url  # Pass the next URL as the state parameter
    )
    return redirect(auth_url)


@app.route("/callback")
def callback():
    """Handle the redirect from Microsoft and store tokens in the session."""
    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    # Get the state parameter (original URL) from the callback
    next_url = request.args.get("state", url_for('dashboard'))
    logger.info(f"Callback state (redirect final to): {next_url}")

    # Exchange authorization code for tokens
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    # Check if token acquisition was successful
    if "access_token" not in result:
        logger.error(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
        return "Authentication failed", 400

    # Retrieve the account object using get_accounts()
    accounts = msal_app.get_accounts()
    if not accounts:
        return "No accounts found after authentication", 400

    # Store the first account in the session
    session["account"] = accounts[0]
    session["access_token"] = result["access_token"]
    session["refresh_token"] = result.get("refresh_token")
    session["name"] = result["id_token_claims"].get("name", "Unknown")
    session["email"] = result["id_token_claims"].get("preferred_username", "Unknown")

    # Clear the 'next' session variable to avoid reusing it
    session.pop('next', None)

    return redirect(next_url)


@app.template_filter('datetimefilter')
def datetime_filter(value, date_format='%Y'):
    if value == 'now':
        return datetime.now().strftime(date_format)
    return value


@app.route('/directory')
@token_required
def directory():
    # Retrieve the access token from the session
    access_token = session.get("access_token")
    if not access_token:
        return "No access token available", 401

    # Set up headers for the Graph API request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    # Make the request to the Microsoft Graph API to list users
    response = requests.get("https://graph.microsoft.com/v1.0/users", headers=headers)
    if response.status_code == 200:
        # Extract the list of users from the response
        users = response.json().get("value", [])
        return render_template("directory.html", users=users)
    else:
        return f"Failed to fetch users: {response.status_code} {response.text}", 500


@app.route('/analytics')
@token_required
@token_required
def analytics():
    # Retrieve the access token from the session
    access_token = session.get("access_token")
    if not access_token:
        return "No access token available", 401

    # Set up headers for the Graph API request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    # Make the request to the Microsoft Graph API to list users
    analytics_response = requests.get("https://graph.microsoft.com/beta/me/analytics/activitystatistics", headers=headers)
    if analytics_response.status_code == 200:
        # Extract the list of users from the response
        analytics = analytics_response.json().get("value", [])
        # logger.debug(f"Analytics JSON: {analytics}")
        return render_template("analytics.html", analytics=analytics)
    else:
        return f"Failed to fetch my analytics: {analytics_response.status_code} {analytics_response.text}", 500


@app.route("/user_info")
@token_required
def user_info():
    """Retrieve and display the user's ID and email."""
    sso = MicrosoftSSO()  # Initialize your class (add params if needed)
    info = sso.get_user_info()
    if info:
        return f"ID: {info['id']}, Email: {info['email']}"
    return "Failed to get user info", 400


@app.route("/logout")
def logout():
    """Clear the session and log the user out."""
    session.clear()
    return redirect("https://login.microsoftonline.com/common/oauth2/v2.0/logout")


@app.route('/')
@token_required
def dashboard():
    """
    Dashboard overview: lists available systems.
    In a real demo, this might query agentfoundry for connected enterprise systems.
    """
    # Dummy list of systems for demonstration.
    systems = [
        {"id": "ehr_sql", "name": "Local SQL EHR System", "status": "Compliant"},
        {"id": "aws_sagemaker", "name": "AWS SageMaker (AI Model Monitoring)", "status": "Fair"}
    ]
    return render_template('dashboard.html', systems=systems)


@app.route('/system/<system_id>')
@token_required
def system_details(system_id):
    """
    Detailed view for a selected system.
    In a real demo, this would show live metrics and logs for the given system.
    """
    # For demonstration, we create dummy details.
    details = {
        "ehr_sql": {
            "name": "Local SQL EHR System",
            "compliance": "HIPAA Compliant",
            "issues": 0
        },
        "aws_sagemaker": {
            "name": "AWS SageMaker",
            "fairness": "No significant bias detected",
            "issues": 1
        }
    }
    system = details.get(system_id, {"name": "Unknown System", "issues": "N/A"})
    return render_template("system_details.html", system=system)


@app.route('/task', methods=['GET', 'POST'])
@token_required
def task_execution():
    """
    Task execution view: allows the user to enter a natural language task.
    When submitted, the task is processed by a Tool Autonomy Agent that inspects the tool registry
    (which includes the registry tool itself) and—if the task mentions a SQLite database—
    sets up the SQLDatabaseToolkit so the LLM can introspect the database schema, generate an SQL query,
    and execute it.
    """
    logger.info("App task_execution called.")
    # Initialize chat history if missing
    history = session.get('chat_history', [])

    if request.method == 'POST':
        user_msg = request.form['task'].strip()
        if user_msg:
            # 1) append user message
            history.append({'role':'user','content':user_msg})

            # 2) invoke agent
            result = autonomy_agent.run_task(user_msg)
            bot_msg = (result.get('output') if isinstance(result, dict) else str(result))

            # 3) append bot response
            history.append({'role':'bot','content':bot_msg})

            # 4) save back to session
            session['chat_history'] = history

    return render_template('task_execution.html', chat_history=history)


@app.route('/reports')
@token_required
def reports():
    """
    Reports view: displays dummy aggregated compliance and fairness reports.
    """
    reports_data = {
        "compliance": "All systems are currently compliant with healthcare data regulations.",
        "fairness": "No significant AI fairness issues detected across monitored systems."
    }
    return render_template("reports.html", reports=reports_data)


@app.template_filter('datetimefilter')
def datetime_filter():
    return datetime.now().strftime('%Y')


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


if __name__ == '__main__':
    try:
        if not exists("logs"):
            os.makedirs("logs")
        port = AppConfig.get("FLASK_PORT", 5000)
        print(f"Flask app running on port {port}")
        debug = AppConfig.get("FLASK_DEBUG", False)
        app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as ex:
        logger.error(f"Exception executing Flask app: {ex}", exc_info=True)
