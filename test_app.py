
import pytest
from app import app
from unittest.mock import Mock, patch

@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_invalid_method_is_rejected(client):
    response = client.post(
        "/",
        data={
            "method": "INVALID",
            "url": "https://jsonplaceholder.typicode.com/users/1"
        }
    )

    assert response.status_code == 200
    assert b"Invalid HTTP method" in response.data


def test_missing_url_is_rejected(client):
    response = client.post(
        "/",
        data={
            "method": "GET",
            "url": ""
        }
    )

    assert response.status_code == 200
    assert b"valid URL" in response.data


def test_invalid_expected_status_is_rejected(client):
    response = client.post(
        "/",
        data={
            "method": "GET",
            "url": "https://jsonplaceholder.typicode.com/users/1",
            "expected_status": "99"
        }
    )

    assert response.status_code == 200
    assert b"Expected status code must be a number" in response.data


def test_invalid_response_time_is_rejected(client):
    response = client.post(
        "/",
        data={
            "method": "GET",
            "url": "https://jsonplaceholder.typicode.com/users/1",
            "max_response_time": "0"
        }
    )

    assert response.status_code == 200
    assert b"Maximum response time must be greater than 0" in response.data

def test_required_field_assertion_fails_when_field_is_missing(client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.elapsed.total_seconds.return_value = 0.05
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": 1, "name": "Test User"}
    mock_response.text = '{"id": 1, "name": "Test User"}'

    with patch("app.is_public_url", return_value=True), \
         patch("app.requests.request", return_value=mock_response):
        response = client.post(
            "/",
            data={
                "method": "GET",
                "url": "https://jsonplaceholder.typicode.com/users/1",
                "required_field": "unknown_field",
            },
        )

    assert response.status_code == 200
    print(response.data.decode("utf-8")[:3000])
    assert b"Required Field Assertion" in response.data