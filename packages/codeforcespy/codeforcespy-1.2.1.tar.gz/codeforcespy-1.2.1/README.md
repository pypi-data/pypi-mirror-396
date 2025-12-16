# codeforcespy

[![PyPI](https://img.shields.io/pypi/v/codeforcespy?color=blue)](https://pypi.org/project/codeforcespy/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[![Type Safe](https://img.shields.io/badge/typing-strict-brightgreen.svg)](https://github.com/microsoft/pyright)

A fast, type-safe Python wrapper for the Codeforces API with sync and async support.

<p align="center">
  <img src="./assets/codeforcespy_banner.png" alt="codeforcespy" width="600">
</p>

## Features

- **Sync & Async** - Full support for both blocking and non-blocking clients
- **Type Safe** - 100% typed, no `Any`, passes strict pyright
- **Fast** - Built on `httpx` and `msgspec` for high performance
- **Complete** - Covers all public Codeforces API endpoints

## Installation

```bash
pip install codeforcespy
```

## Quick Start

### Async Client (Recommended)

```python
import asyncio
import codeforcespy.processors

async def main():
    client = codeforcespy.processors.AsyncMethod()
    
    try:
        # Get user info
        users = await client.get_user(handles="tourist")
        print(f"{users[0].handle}: {users[0].rating}")
        
        # Get recent contests
        contests = await client.get_contest_list()
        print(f"Found {len(contests)} contests")
    finally:
        await client.close()

asyncio.run(main())
```

### Sync Client

```python
import codeforcespy.processors

client = codeforcespy.processors.SyncMethod()

try:
    users = client.get_user(handles="tourist")
    print(f"{users[0].handle}: {users[0].rating}")
finally:
    client.close()
```

## API Methods

### User

| Method | Description |
|--------|-------------|
| `get_user(handles)` | Get user profile(s) by handle |
| `get_user_rating(handle)` | Get rating history |
| `get_user_status(handle, count)` | Get recent submissions |
| `get_user_friends(only_online)` | Get friends list (auth required) |
| `get_user_blog_entries(handle)` | Get user's blog posts |
| `get_user_rated_list(...)` | Get rated users list |

### Contest

| Method | Description |
|--------|-------------|
| `get_contest_list(of_gym)` | List all contests |
| `get_contest_standings(...)` | Get contest standings |
| `get_contest_status(contest_id)` | Get contest submissions |
| `get_contest_hacks(contest_id)` | Get contest hacks |
| `get_contest_rating_changes(contest_id)` | Get rating changes |

### Problemset

| Method | Description |
|--------|-------------|
| `get_problemset_problems(tags)` | Get problems by tags |
| `get_problemset_recent_status(count)` | Get recent submissions |

### Blog & Recent

| Method | Description |
|--------|-------------|
| `get_blog_entry_view(blog_entry_id)` | Get blog post |
| `get_blog_entry_comments(blog_entry_id)` | Get blog comments |
| `get_recent_actions(max_count)` | Get recent platform activity |

## Authentication

For authenticated endpoints (friends, private data):

```python
client = codeforcespy.processors.AsyncMethod(
    enable_auth=True,
    auth_key="YOUR_API_KEY",
    secret="YOUR_API_SECRET",
)
```

Get your API key at [codeforces.com/settings/api](https://codeforces.com/settings/api).

## Error Handling

```python
import codeforcespy.errors
import codeforcespy.processors

client = codeforcespy.processors.SyncMethod()

try:
    users = client.get_user(handles="nonexistent_user_12345")
except codeforcespy.errors.APIError as e:
    print(f"API error: {e.message}")
except codeforcespy.errors.CodeforcesPyError as e:
    print(f"Library error: {e.message}")
```

## Examples

See the [examples/](examples/) directory for complete working examples:
- `sync_example.py` - Synchronous client usage
- `async_example.py` - Asynchronous client with concurrent requests

## License

GPL-3.0 License - see [LICENSE](LICENSE) for details.
