import asyncio
import json
import logging
import random
from typing import Literal, Optional

import aiohttp
import requests
from pydantic import BaseModel
from requests import JSONDecodeError
from tenacity import (
    RetryError,
    before_sleep_log,
    retry,
    retry_if_result,
    stop_after_attempt,
    wait_random,
)

from baresquare_sdk.core import logger
from baresquare_sdk.core.exceptions import ExceptionInfo


def is_retriable_http_status_code(response):
    return response.status_code >= 400 and response.status_code not in [400, 403, 404]


def request(
    url: str,
    method: Optional[Literal["GET"] | Literal["POST"]] = "GET",
    headers: Optional[dict[str, str]] = None,
    params: Optional[dict[str, str | int]] = None,
    data: Optional[dict[str, str | int]] = None,
    payload: Optional[dict[str, str | int]] = None,
    response_model: Optional[type[BaseModel]] = None,
    retries: int = 5,
    sleep: Optional[float] = 3,
    connect_timeout: float = 6.05,
    read_timeout: float = 200.0,
    **_,
) -> dict:
    """Execute an HTTP request synchronously.

    Args:
        url: The URL to send the request to.
        method: The HTTP method to use. Must be either 'GET' or 'POST'.
        headers: Optional; A dictionary of HTTP headers to send with the request.
        params: Optional; A dictionary of query parameters to send with the request.
        data: Optional; A dictionary of data to send with the request.
        response_model: Optional; A subclass of BaseModel to validate the response against
        retries: Optional; The number of times to retry the request if it fails.
        sleep: Optional; The number of seconds to wait between retries.
        connect_timeout: Optional; The timeout in seconds for establishing a connection (default: 6.05).
        read_timeout: Optional; The timeout in seconds for reading data from the server (default: 200.0).

    Returns:
        The response from the server. If the response is actual JSON or JSON
        serializable, it is returned as a dictionary. Otherwise, it is added as
        is under the "text" key.

    Raises:
        ValueError: If an unsupported HTTP method is used.
        aiohttp.ClientError: If the request fails for any reason.

    """

    @retry(
        retry=retry_if_result(is_retriable_http_status_code),
        stop=stop_after_attempt(retries),
        wait=wait_random(0, sleep),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def unreliable_http_request():
        return requests.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data,
            json=payload,
            timeout=(connect_timeout, read_timeout),
        )

    if method not in {"GET", "POST"}:
        raise ValueError("Unsupported HTTP method. Use 'GET' or 'POST'.")

    try:
        response = unreliable_http_request()
    except RetryError as e:
        last_result = e.last_attempt.result()
        cause = f"{last_result.status_code}: {last_result.reason}"
        msg = f"Request to {url} failed after {retries} retries. Last attempt's exception: '{cause}'"
        raise ExceptionInfo(
            msg,
            data={
                "error_message": msg,
                "retries": retries,
                "last_status_code": last_result.status_code,
                "last_response_text": last_result.text,
                "last_reason": last_result.reason,
            },
            cause=cause,
        )

    if not response.ok:
        raise ExceptionInfo(
            f"Request to {url} failed with status code {response.status_code}. The payload is {json.dumps(payload)}",
            data={
                "url": url,
                "http_request": {"params": params, "data": data, "json": payload},
                "http_response": {
                    "status": response.status_code,
                    "text": response.text,
                },
            },
        )
    try:
        response = response.json()
    except JSONDecodeError:
        resp_text = response.text
        try:
            response = json.loads(resp_text)
        except BaseException:
            logger.warning('response is not JSON serializable, returning as raw string under "text" key')
            response = {"text": resp_text}
    if response_model:
        response_model.model_validate(response)
    return response


async def arequest(
    url: str,
    method: Optional[Literal["GET"] | Literal["POST"]] = "GET",
    headers: Optional[dict[str, str]] = None,
    params: Optional[dict[str, str | int]] = None,
    data: Optional[dict[str, str | int]] = None,
    payload: Optional[dict[str, str | int]] = None,
    response_model: Optional[type[BaseModel]] = None,
    retries: int = 5,
    sleep: Optional[float] = 3,
    request_timeout: int = 240,
    connect_timeout: int = 60,
    sock_read_timeout: int = 60,
    **_,
) -> dict:
    """Execute an HTTP request asynchronously.



    Args:

        url: The URL to send the request to.

        method: The HTTP method to use. Must be either 'GET' or 'POST'.

        headers: Optional; A dictionary of HTTP headers to send with the request.

        params: Optional; A dictionary of query parameters to send with the request.

        data: Optional; A dictionary of data to send with the request.

        retries: Optional; The number of times to retry the request if it fails.

        sleep: Optional; The number of seconds to wait between retries.

        request_timeout: Optional; The timeout in seconds for the entire request operation.



    Returns:

        The response from the server. If the response is JSON, it is returned as a

        dictionary. Otherwise, it is returned as a string.



    Raises:

        ValueError: If an unsupported HTTP method is used.

        ExceptionInfo: If the request fails after all retries.

    """
    if method not in {"GET", "POST"}:
        raise ValueError("Unsupported HTTP method. Use 'GET' or 'POST'.")

    req = {
        "params": params,
        "data": data,
        "json": payload,
    }

    async def _make_request(attempt: int) -> dict:
        try:
            client_timeout = aiohttp.ClientTimeout(
                total=request_timeout,
                connect=connect_timeout,
                sock_read=sock_read_timeout,
            )

            async with aiohttp.ClientSession(timeout=client_timeout) as session:  # noqa: SIM117
                async with session.request(method, url, headers=headers, **req) as response:
                    if not response.ok:
                        logger.warning(f"Request failed in attempt {attempt + 1}. Status: {response.status}")

                        raise ExceptionInfo(
                            msg=f"Request failed with status {response.status}",
                            data={
                                "attempts": attempt + 1,
                                "url": url,
                                "http_request": req,
                                "http_response": {
                                    "status": response.status,
                                    "text": await response.text(),
                                },
                            },
                        )

                    try:
                        return await response.json()

                    except aiohttp.ContentTypeError:
                        resp_text = await response.text()

                        try:
                            return json.loads(resp_text)

                        except json.JSONDecodeError:
                            logger.warning(
                                'Response is not JSON serializable, returning as raw string under "text" key',
                            )

                            return {"text": resp_text}

        except asyncio.TimeoutError:
            data = {
                "attempts": attempt + 1,
                "url": url,
                "timeout": request_timeout,
                "request": req,
            }

            logger.warning(
                msg=f"Request timed out in attempt {attempt + 1}",
                extra=data,
            )

            raise ExceptionInfo(
                msg="Request timed out",
                data=data,
            )

        except (asyncio.CancelledError, aiohttp.ServerDisconnectedError):
            # Handle both CancelledError and ServerDisconnectedError as cancellation

            data = {
                "attempts": attempt + 1,
                "url": url,
                "request": req,
            }

            logger.warning(f"Request was cancelled in attempt {attempt + 1}", extra=data)

            raise ExceptionInfo(
                msg="Request was cancelled",
                data=data,
            )

        except aiohttp.ClientError as e:
            data = {
                "attempts": attempt + 1,
                "url": url,
                "error": str(e),
                "request": req,
            }

            logger.warning(f"Client error in attempt {attempt + 1}: {str(e)}", extra=data)

            raise ExceptionInfo(
                msg=f"Client error: {str(e)}",
                data=data,
            )

    last_error = None

    for attempt in range(retries):
        try:
            response_dict = await _make_request(attempt)

            if response_model:
                response_model.model_validate(response_dict)

            return response_dict

        except ExceptionInfo as e:
            last_error = e

            if isinstance(e.data.get("http_response", {}).get("status"), int):
                status = e.data["http_response"]["status"]

                if status in [400, 403, 404]:
                    raise  # Don't retry client errors

                if status == 429:  # Rate limit - use exponential backoff
                    delay = min(30, (2**attempt) + random.uniform(0, 1))

                else:
                    delay = sleep

            else:
                # Only propagate cancellation errors immediately

                if e.message == "Request was cancelled":
                    raise

                # For timeouts and client errors, continue with retry logic

                delay = sleep

            if attempt < retries - 1:  # Don't sleep on the last attempt
                await asyncio.sleep(delay)

            continue

    # If we get here, we've exhausted all retries

    raise (
        last_error
        if last_error
        else ExceptionInfo(
            msg=f"Request failed after {retries} attempts",
            data={
                "url": url,
                "last_error": last_error.data if last_error else None,
                "retries": retries,
            },
        )
    )
