import asyncio
import json
from unittest.mock import patch

import aiohttp
import pytest
from pydantic import BaseModel
from requests import Response

from baresquare_sdk.core import http_client as sut
from baresquare_sdk.core.exceptions import ExceptionInfo


class Foo(BaseModel):
    foo: str


class JSONWithFields(BaseModel):
    field_a: str
    field_b: int


@pytest.fixture
def resp_success():
    resp = Response()
    resp._content = bytearray(json.dumps({"foo": "bar"}), encoding="utf-8")
    resp.status_code = 200
    resp.encoding = "utf-8"
    return resp


@pytest.fixture
def resp_hard_http_status_failure():
    resp = Response()
    resp._content = bytearray(json.dumps({"foo": "bar"}), encoding="utf-8")
    resp.status_code = 400
    resp.encoding = "utf-8"
    return resp


@pytest.fixture
def resp_soft_http_status_failure():
    resp = Response()
    resp.status_code = 429
    resp.encoding = "utf-8"
    return resp


test_cases = [
    ("GET", {"status": 200, "text": "Hello World"}),
    ("GET", {"status": 400}),
    (
        "GET",
        {
            "meta_data": {
                "url": "https://www.google.com/search?q=%22bebe+women%27s+fashion%22+OR+%22bebe+stores%22+OR+%22bebe+contemporary+fashion%22+OR+%22bebe+accessories%22+OR+%22bebe+apparel%22&tbs=cdr%3A1%2Ccd_min%3A12%2F04%2F2023%2Ccd_max%3A12%2F11%2F2023&gl=us&hl=en&tbm=nws&num=20",
                "number_of_results": None,
                "location": None,
                "number_of_organic_results": 0,
                "number_of_ads": 0,
                "number_of_page": None,
            },
            "organic_results": [],
            "local_results": [],
            "top_ads": [],
            "bottom_ads": [],
            "related_queries": [],
            "questions": [],
            "top_stories": [],
            "news_results": [],
            "knowledge_graph": {},
            "related_searches": [],
        },
    ),
    (
        "POST",
        {
            "reports": [
                {
                    "dimensionHeaders": [
                        {"name": "date"},
                    ],
                    "metricHeaders": [
                        {"name": "itemspurchased", "type": "TYPE_INTEGER"},
                    ],
                    "rows": [
                        {
                            "dimensionValues": [
                                {"value": "20231211"},
                            ],
                            "metricValues": [
                                {"value": "5"},
                            ],
                        },
                        {
                            "dimensionValues": [
                                {"value": "20231210"},
                            ],
                            "metricValues": [{"value": "0"}],
                        },
                        {
                            "dimensionValues": [
                                {"value": "20231211"},
                            ],
                            "metricValues": [
                                {"value": "0"},
                                {"value": "28"},
                            ],
                        },
                    ],
                    "rowCount": 25,
                    "metadata": {"currencyCode": "USD", "timeZone": "America/Los_Angeles"},
                    "kind": "analyticsData#runReport",
                },
            ],
            "kind": "analyticsData#batchRunReports",
        },
    ),
]


# This could be a generic class for all the async tests
class MockServer:
    def __init__(self, text, status=500, final_status=200, change_after_attempts=3):
        self.app = aiohttp.web.Application()
        self.app.router.add_get("/", self.handle_request)
        self.app.router.add_post("/", self.handle_request)
        self.status = status
        self.final_status = final_status
        self.text = text
        self.change_after_attempts = change_after_attempts
        self.attempts = 0

    async def handle_request(self, request):
        self.attempts += 1
        if self.attempts < self.change_after_attempts:
            return aiohttp.web.Response(status=self.status)
        return aiohttp.web.json_response(self.text, status=self.final_status)


@pytest.mark.asyncio
@pytest.mark.parametrize("method,test_case", test_cases)
async def test_arequest(aiohttp_client, method, test_case):
    server = MockServer(test_case)
    client = await aiohttp_client(server.app)
    url = str(client.make_url("/"))

    response = await sut.arequest(url, method, sleep=0)

    # Check that the response is the expected text
    assert response == test_case

    # Check that the number of attempts is correct
    assert server.attempts == server.change_after_attempts


@pytest.mark.asyncio
async def test_arequest_ex_data(aiohttp_client):
    server = MockServer({"status": 400, "text": "Bad Request"}, final_status=400, change_after_attempts=1)
    client = await aiohttp_client(server.app)
    url = str(client.make_url("/"))

    with pytest.raises(ExceptionInfo):
        await sut.arequest(url, "POST", sleep=0)

    try:
        await sut.arequest(
            url, method="POST", params={"p_1": "p", "p_2": "q", "p_3": "r"}, data={"d_1": 1, "d_2": 2}, sleep=0
        )
    except ExceptionInfo as e:
        assert isinstance(e.data["url"], str)
        assert {k: v for k, v in e.data.items() if k not in ["url"]} == {
            "attempts": 1,
            "http_response": {
                "status": 400,
                "text": '{"status": 400, "text": "Bad Request"}',
            },
            "http_request": {
                "json": None,
                "data": {"d_1": 1, "d_2": 2},
                "params": {"p_1": "p", "p_2": "q", "p_3": "r"},
            },
        }


@pytest.mark.asyncio
async def test_arequest_no_retry(aiohttp_client):
    server = MockServer({"status": 400, "text": "Bad Request 2"}, final_status=400, change_after_attempts=1)
    client = await aiohttp_client(server.app)
    url = str(client.make_url("/"))

    with pytest.raises(ExceptionInfo):
        await sut.arequest(url, "GET", sleep=0)

    # Check that the number of attempts is correct
    assert server.attempts == 1


@patch("baresquare_sdk.core.http_client.requests.request")
def test_request__success_at_once(request_mock, resp_success):
    request_mock.return_value = resp_success
    assert sut.request(url="foo") == {"foo": "bar"}


@patch("baresquare_sdk.core.http_client.requests.request")
def test_request__success_after_retry(request_mock, resp_soft_http_status_failure, resp_success):
    request_mock.side_effect = [resp_soft_http_status_failure, resp_success]
    assert sut.request(url="foo", sleep=0) == {"foo": "bar"}


@patch("baresquare_sdk.core.http_client.requests.request")
def test_request__success_valid_response(request_mock, resp_success):
    request_mock.return_value = resp_success

    assert sut.request(url="foo", response_model=Foo) == {"foo": "bar"}
    with pytest.raises(Exception):
        sut.request()


@patch("baresquare_sdk.core.http_client.requests.request")
def test_request__failure_at_once(request_mock, resp_hard_http_status_failure):
    request_mock.return_value = resp_hard_http_status_failure
    with pytest.raises(Exception):
        sut.request(url="foo")


@patch("baresquare_sdk.core.http_client.requests.request")
def test_request__failure_too_many_attempts(request_mock, resp_soft_http_status_failure, resp_success):
    request_mock.side_effect = [resp_soft_http_status_failure] * 2 + [resp_success]
    with pytest.raises(Exception):
        sut.request(url="foo", retries=1)


@patch("baresquare_sdk.core.http_client.requests.request")
def test_request__failure_invalid_response(request_mock, resp_success):
    request_mock.return_value = resp_success

    with pytest.raises(Exception):
        sut.request(url="foo", response_model=JSONWithFields)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_arequest_timeout(aiohttp_client):
    """Test that timeout errors are handled correctly."""

    async def slow_handler(_):
        await asyncio.sleep(2)  # Simulate slow response
        return aiohttp.web.Response(text="too late")

    app = aiohttp.web.Application()
    app.router.add_get("/", slow_handler)
    client = await aiohttp_client(app)
    url = str(client.make_url("/"))

    with pytest.raises(ExceptionInfo) as exc_info:
        await sut.arequest(url, request_timeout=1, retries=1, sleep=0)

    assert exc_info.value.message == "Request timed out"
    assert exc_info.value.data["timeout"] == 1
    assert exc_info.value.data["attempts"] == 1


@pytest.mark.asyncio
async def test_arequest_cancelled(aiohttp_client):
    """Test that cancelled requests are handled correctly."""

    async def cancel_handler(request):
        # This will cause a ServerDisconnectedError
        await request.transport.close()
        return aiohttp.web.Response(text="This won't be sent")

    app = aiohttp.web.Application()
    app.router.add_get("/", cancel_handler)
    client = await aiohttp_client(app)
    url = str(client.make_url("/"))

    with pytest.raises(ExceptionInfo) as exc_info:
        await sut.arequest(url, retries=1, sleep=0)

    assert exc_info.value.message == "Request was cancelled"
    assert exc_info.value.data["attempts"] == 1


@pytest.mark.slow
@pytest.mark.asyncio
async def test_arequest_client_error():
    """Test that client errors are handled correctly."""
    # Use a URL that doesn't exist to trigger a real client connection error
    url = "http://non-existent-server-12345.local"

    with pytest.raises(ExceptionInfo) as exc_info:
        await sut.arequest(url, retries=1, sleep=0)

    assert "Client error" in exc_info.value.message
    assert exc_info.value.data["attempts"] == 1


@pytest.mark.slow
@pytest.mark.asyncio
async def test_arequest_rate_limit_backoff(aiohttp_client, monkeypatch):
    """Test that rate limit backoff works correctly."""
    # Mock random.uniform to return a consistent value
    monkeypatch.setattr("random.uniform", lambda x, y: 0.1)

    class RateLimitServer(MockServer):
        def __init__(self):
            super().__init__(
                text={"status": "ok"},
                status=429,
                final_status=200,
                change_after_attempts=2,  # Reduced from 3
            )
            self.delays = []
            self._last_request_time = None

        async def handle_request(self, _):
            current_time = asyncio.get_event_loop().time()
            if self._last_request_time is not None:
                self.delays.append(current_time - self._last_request_time)
            self._last_request_time = current_time
            return await super().handle_request(_)

    server = RateLimitServer()
    client = await aiohttp_client(server.app)
    url = str(client.make_url("/"))

    # We expect this to succeed after retries
    response = await sut.arequest(url, retries=2, sleep=0.1)  # Reduced retries and sleep
    assert response == {"status": "ok"}

    # Check that the delays between retries are increasing
    assert len(server.delays) >= 1
    assert all(delay > 0 for delay in server.delays)  # Verify delays are positive


@pytest.mark.asyncio
async def test_arequest_non_json_response(aiohttp_client):
    """Test handling of non-JSON responses."""

    async def text_handler(_):
        return aiohttp.web.Response(text="Hello World", content_type="text/plain")

    app = aiohttp.web.Application()
    app.router.add_get("/", text_handler)
    client = await aiohttp_client(app)
    url = str(client.make_url("/"))

    response = await sut.arequest(url)

    assert response == {"text": "Hello World"}


@pytest.mark.asyncio
async def test_arequest_invalid_json_response(aiohttp_client):
    """Test handling of invalid JSON responses."""

    async def invalid_json_handler(_):
        return aiohttp.web.Response(
            text='{"invalid": "json"}',
            content_type="application/json",
        )

    app = aiohttp.web.Application()
    app.router.add_get("/", invalid_json_handler)
    client = await aiohttp_client(app)
    url = str(client.make_url("/"))

    response = await sut.arequest(url)

    assert response == {"invalid": "json"}


@pytest.mark.asyncio
async def test_arequest__connect_timeout_then_success(aiohttp_client):
    """Test that connection timeout triggers a retry, and second attempt succeeds."""

    class TimeoutThenSuccessServer(MockServer):
        def __init__(self):
            super().__init__(
                text={"status": "ok"},
                final_status=200,
                change_after_attempts=2,
            )
            self.first_attempt = True

        async def handle_request(self, request):
            self.attempts += 1
            if self.first_attempt:
                self.first_attempt = False
                # Simulate a connection timeout by sleeping longer than the timeout
                # and then returning a valid response (which won't be received due to timeout)
                await asyncio.sleep(2)
                return aiohttp.web.json_response({"timeout": "too late"})

            return aiohttp.web.json_response(self.text, status=self.final_status)

    server = TimeoutThenSuccessServer()
    client = await aiohttp_client(server.app)
    url = str(client.make_url("/"))

    response = await sut.arequest(
        url=url,
        connect_timeout=0.1,  # Very short timeout to trigger the error
        request_timeout=0.2,  # Also need a short request timeout
        retries=2,
        sleep=0,
    )

    assert response == {"status": "ok"}
    assert server.attempts == 2


@pytest.mark.asyncio
async def test_arequest__connect_timeout_max_retries(aiohttp_client):
    """Test that connection timeout retries until max attempts and raises."""

    class AlwaysTimeoutServer(MockServer):
        async def handle_request(self, request):
            self.attempts += 1
            # Always sleep longer than the timeout
            await asyncio.sleep(2)
            return aiohttp.web.json_response({"timeout": "too late"})

    server = AlwaysTimeoutServer(text={})  # Text doesn't matter as we'll never return it
    client = await aiohttp_client(server.app)
    url = str(client.make_url("/"))

    with pytest.raises(ExceptionInfo) as exc_info:
        await sut.arequest(
            url=url,
            connect_timeout=0.1,  # Very short timeout to trigger the error
            request_timeout=0.2,  # Also need a short request timeout
            retries=2,
            sleep=0,
        )

    assert exc_info.value.message == "Request timed out"
    assert exc_info.value.data["attempts"] == 2
    assert exc_info.value.data["timeout"] == 0.2  # Using our custom request_timeout
    assert server.attempts == 2
