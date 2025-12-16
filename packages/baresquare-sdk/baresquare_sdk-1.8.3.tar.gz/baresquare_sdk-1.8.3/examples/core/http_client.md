# HTTP Client Examples

This document provides simple examples of using the HTTP client functions from `baresquare_sdk.core.http_client`.

## Basic Usage

### Simple GET Request

```python
from baresquare_sdk.core.http_client import request

# Basic GET request
response = request(url="https://jsonplaceholder.typicode.com/users/1", method="GET")
print("GET Response:", response)
```

### GET Request with Query Parameters

```python
# GET request with query parameters
response = request(url="https://jsonplaceholder.typicode.com/posts", method="GET", params={"userId": 1, "_limit": 3})
print(f"Found {len(response)} posts")
```

### POST Request with JSON Data

```python
# POST request with JSON payload
new_post = {
    "title": "My Test Post",
    "body": "This is a test post created with baresquare_sdk HTTP client.",
    "userId": 1,
}

response = request(url="https://jsonplaceholder.typicode.com/posts", method="POST", payload=new_post)
print(f"Created post with ID: {response['id']}")
```

## Asynchronous Requests

### Basic Async GET Request

```python
import asyncio
from baresquare_sdk.core.http_client import arequest

async def fetch_user():
    response = await arequest(url="https://jsonplaceholder.typicode.com/users/2", method="GET")
    return response

user = asyncio.run(fetch_user())
print("Async GET Response:", user["name"])
```

### Async POST Request

```python
import asyncio
from baresquare_sdk.core.http_client import arequest

async def create_comment():
    comment_data = {"postId": 1, "name": "Test Comment", "email": "test@example.com", "body": "This is a test comment."}

    response = await arequest(url="https://jsonplaceholder.typicode.com/comments", method="POST", payload=comment_data)
    return response

comment = asyncio.run(create_comment())
print(f"Created comment with ID: {comment['id']}")
```

### Multiple Concurrent Async Requests

```python
import asyncio
from baresquare_sdk.core.http_client import arequest

async def fetch_multiple_posts():
    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/posts/3",
    ]

    tasks = [arequest(url=url, method="GET") for url in urls]
    posts = await asyncio.gather(*tasks)
    return posts

posts = asyncio.run(fetch_multiple_posts())
print(f"Fetched {len(posts)} posts concurrently")
for i, post in enumerate(posts, 1):
    print(f"Post {i}: {post['title']}")
```

## Advanced Features

### Custom Timeout Settings

```python
import asyncio
from baresquare_sdk.core.http_client import arequest

async def fetch_with_timeout():
    response = await arequest(
        url="https://jsonplaceholder.typicode.com/posts/1",
        method="GET",
        request_timeout=30,    # Total request timeout
        connect_timeout=10,    # Connection timeout
        sock_read_timeout=15   # Socket read timeout
    )
    return response

data = asyncio.run(fetch_with_timeout())
```
