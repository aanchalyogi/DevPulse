
from flask import Flask, render_template, request, redirect
import requests
import json
from urllib.parse import urlparse
import ipaddress
import socket
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
HISTORY_FILE = "history.json"

KNOWLEDGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base.json")


def retrieve_guidance(status):
    try:
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
            knowledge = json.load(file)

        for item in knowledge:
            if str(item.get("status")) == str(status):
                steps = "\n".join(
                    f"- {step}" for step in item.get("steps", [])
                )
                return (
                    f"HTTP {item['status']}: {item['title']}\n"
                    f"Common causes: {item['causes']}\n"
                    f"Recommended debugging steps:\n{steps}"
                )

        return "No matching HTTP status guidance found in the knowledge base."

    except (OSError, json.JSONDecodeError, TypeError) as error:
        app.logger.warning("Could not load RAG knowledge base: %s", error)
        return "Troubleshooting knowledge base is currently unavailable."

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)
app.config["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

client = (
    genai.Client(api_key=app.config["GEMINI_API_KEY"])
    if app.config["GEMINI_API_KEY"]
    else None
)

ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE"}


def is_public_url(url):
    """Reject local and private network destinations."""
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False

    host = parsed.hostname.lower()

    if host == "localhost" or host.endswith(".localhost"):
        return False

    try:
        addresses = socket.getaddrinfo(host, None)
        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                return False
    except (socket.gaierror, ValueError):
        return False

    return True


@app.route("/", methods=["GET", "POST"])
def home():
    response_data = None
    error = None

    if request.method == "POST":
        expected_status = request.form.get("expected_status", "").strip()
        max_response_time = request.form.get("max_response_time", "").strip()
        required_field = request.form.get("required_field", "").strip()

        if expected_status:
            if (
                not expected_status.isdigit()
                or not 100 <= int(expected_status) <= 599
            ):
                error = "Expected status code must be a number between 100 and 599."

        if max_response_time:
            try:
                if float(max_response_time) <= 0:
                    error = "Maximum response time must be greater than 0."
            except ValueError:
                error = "Maximum response time must be a valid number."

        method = request.form.get("method", "GET").upper()
        url = request.form.get("url", "").strip()
        headers_text = request.form.get("headers", "").strip()
        body_text = request.form.get("body", "").strip()

        headers = {}
        body = None

        if error:
            pass

        elif method not in ALLOWED_METHODS:
            error = "Invalid HTTP method."

        elif not is_public_url(url):
            error = "Enter a valid URL pointing to a public server."

        else:
            try:
                if headers_text:
                    headers = json.loads(headers_text)

                    if not isinstance(headers, dict):
                        raise ValueError("Headers must be a JSON object.")

                    if not all(
                        isinstance(k, str) and isinstance(v, str)
                        for k, v in headers.items()
                    ):
                        raise ValueError(
                            "Header names and values must be strings."
                        )

                if body_text:
                    body = json.loads(body_text)

            except (json.JSONDecodeError, ValueError) as exc:
                error = f"Invalid input: {exc}"

        if not error:
            try:
                api_response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body if method in {"POST", "PUT"} else None,
                    timeout=10,
                    allow_redirects=False
                )

                response_data = {
                    "status": api_response.status_code,
                    "time": round(
                        api_response.elapsed.total_seconds() * 1000, 2
                    ),
                   "body": json.dumps(api_response.json(), indent=4) 
                   if "application/json" in api_response.headers.get("Content-Type", "")
                    else api_response.text[:10000],
                    "headers": dict(api_response.headers)
                }
                if required_field:
                    try:
                        response_json = api_response.json()
                        response_data["field_test_passed"] = (
                            required_field in response_json
                            if isinstance(response_json, dict)
                            else False
                        )
                    except ValueError:
                        response_data["field_test_passed"] = False

                    response_data["required_field"] = required_field
                else:
                    response_data["field_test_passed"] = None
                    response_data["required_field"] = None
                if expected_status:
                    response_data["test_passed"] = (
                        int(expected_status) == response_data["status"]
                    )
                    response_data["expected_status"] = int(expected_status)
                else:
                    response_data["test_passed"] = None
                    response_data["expected_status"] = None
                if max_response_time:
                    response_data["time_test_passed"] = (
                        response_data["time"] <= float(max_response_time)
                    )
                    response_data["max_response_time"] = float(max_response_time)
                else:
                    response_data["time_test_passed"] = None
                    response_data["max_response_time"] = None

                history = load_history()

                history.append({
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "body": body if method in ("POST", "PUT") else None,
                    "status": response_data["status"],
                    "time": response_data["time"]
                })

                save_history(history)

            except requests.RequestException as exc:
                error = f"Request failed: {exc}"

    return render_template(
            "index.html",
            response_data=response_data,
             error=error,
             history=load_history()
        )
    
@app.route("/explain", methods=["POST"])
def explain_error():
    if client is None:
        return {
            "explanation": "Gemini API key is missing. Check your .env file."
        }, 500

    data = request.get_json(silent=True) or {}

    status = data.get("status")
    body = str(data.get("body", ""))[:4000]
    method = str(data.get("method", "GET"))[:10]
    url = str(data.get("url", ""))[:500]
    guidance = retrieve_guidance(status)
    

   
    prompt = f"""
You are DevPulse, an API debugging assistant.

Explain the API response in simple language.
Use the retrieved troubleshooting guidance when relevant.
Treat it as general guidance, not proof of the exact cause.
Suggest practical debugging steps.
Do not claim certainty when the evidence is insufficient.

HTTP method: {method}
Request URL: {url}
Status code: {status}

Retrieved troubleshooting knowledge:
{guidance}

Actual response body:
{body}
"""


    try:
        result = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return {"explanation": result.text or "No explanation returned."}

    except Exception as e:
        app.logger.exception("Gemini API request failed")

        error_message = str(e)

        if "503" in error_message or "UNAVAILABLE" in error_message:
            return {
                "explanation": (
                    "Gemini is temporarily busy. "
                    "Please wait a few seconds and try again."
                )
            }, 503

        return {
            "explanation": "Gemini request failed. Check the server terminal."
        }, 502

@app.route("/clear-history", methods=["POST"])
def clear_history():
    save_history([])
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
