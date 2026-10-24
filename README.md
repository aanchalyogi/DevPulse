# DevPulse — AI-Powered API Testing & Debugging Tool

DevPulse is a web-based API testing and debugging tool built with Flask and Python. It allows developers to send HTTP requests, inspect API responses, validate response conditions, and understand errors using Google's Gemini AI with a local troubleshooting knowledge base.

## Features

- **HTTP Request Testing:** Supports GET, POST, PUT, and DELETE requests.
- **Response Inspection:** Displays status codes, response times, response bodies, and headers.
- **Automated Assertions:** Validates expected status codes, maximum response time, and required response fields.
- **AI-Powered Debugging:** Uses the Gemini API to explain API errors and suggest troubleshooting steps.
- **Retrieval-Augmented Generation (RAG):** Retrieves relevant HTTP troubleshooting guidance from a local JSON knowledge base and provides it to the AI.
- **Request History:** Saves previous requests and allows users to rerun them.
- **Input Validation:** Validates request URLs and handles invalid inputs.
- **Automated Testing:** Includes tests for important application behavior using pytest.

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **AI Integration:** Google Gemini API
- **Knowledge Base:** JSON-based troubleshooting data
- **Testing:** pytest
- **HTTP Requests:** Python Requests library

## How It Works

1. Enter an API URL and select an HTTP method.
2. Add headers or a JSON request body when required.
3. Send the request and inspect the response.
4. Configure assertions to validate the response.
5. Use AI-powered explanations to understand errors.
6. View or rerun previous requests from the request history.

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd DevPulse
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your own Gemini API key. Never commit your `.env` file or expose your API key publicly.

### 5. Run the application

```powershell
python app.py
```

Open the local URL displayed in the terminal in your browser.

## Testing

Run the automated tests using:

```powershell
python -m pytest -v
```

## Learning Outcomes

- Building a full-stack web application with Flask
- Working with HTTP methods and REST API responses
- Implementing response validation and automated assertions
- Integrating a generative AI API
- Applying basic RAG using a structured local knowledge base
- Writing automated tests and handling errors

## Future Improvements

- Add semantic retrieval for troubleshooting knowledge
- Expand API test collections and reporting
- Improve request organization and debugging workflows
- Add exportable test reports

## Author

**Aanchal Yogi**

Built as a software development project to explore API testing, debugging, and AI-assisted developer tools.
