"""
🔌 **HTTP Client Transports**.
=============================

Provides the underlying HTTP client wrappers for Codeforces API interaction.

✨ **Components**
-----------------
- 🔄 **SyncClient**: Wrapper around `httpx.Client` for synchronous calls.
- ⚡ **AsyncClient**: Wrapper around `httpx.AsyncClient` for asynchronous calls.

📝 **Compliance**
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""

import httpx


class AsyncClient(httpx.AsyncClient):
    pass


class SyncClient(httpx.Client):
    pass
