import os
import sys

import httpx
import pytest

# Ensure we can import the package
sys.path.insert(0, os.getcwd())

import codeforcespy
from codeforcespy import AsyncClient
from codeforcespy import CodeForcesAPI
from codeforcespy import SyncClient


class TestImports:
    def test_top_level_imports(self):
        """Verify that top-level imports work correctly."""
        assert hasattr(codeforcespy, "CodeForcesAPI")
        assert hasattr(codeforcespy, "AsyncClient")
        assert hasattr(codeforcespy, "SyncClient")

    def test_abc_imports(self):
        """Verify that abc submodule imports are available."""
        from codeforcespy.abc.objects import Contest
        from codeforcespy.abc.objects import User

        assert User is not None
        assert Contest is not None


class TestCodeForcesAPI:
    def setup_method(self):
        self.api = CodeForcesAPI()

    def test_url_generation(self):
        """Verify correct URL generation for endpoints."""
        assert (
            self.api.user_info("test_user")
            == "https://codeforces.com/api/user.info?handles=test_user&checkHistoricHandles=True"
        )
        assert (
            self.api.contest_standings(566)
            == "https://codeforces.com/api/contest.standings?contestId=566&asManager=False&from=1&count=5&showUnofficial=True"
        )


class TestAsyncClient:
    @pytest.mark.asyncio
    async def test_async_client_initialization(self):
        """Verify AsyncClient initializes correctly."""
        async with AsyncClient() as client:
            assert isinstance(client, httpx.AsyncClient)


class TestSyncClient:
    def test_sync_client_initialization(self):
        """Verify SyncClient initializes correctly."""
        with SyncClient() as client:
            assert isinstance(client, httpx.Client)
