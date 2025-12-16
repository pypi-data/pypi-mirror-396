"""Tests for asynchronous client."""

import pytest
import respx
from httpx import Response

from codeforcespy.processors import AsyncMethod


@pytest.fixture
def handles() -> str:
    return "Fefer_Ivan;DmitriyH"


@pytest.fixture
def client() -> AsyncMethod:
    """Fixture providing an AsyncMethod instance."""
    return AsyncMethod()


@pytest.fixture
def mock_user_response() -> dict[str, object]:
    """Mock response for user.info."""
    return {
        "status": "OK",
        "result": [
            {
                "handle": "Fefer_Ivan",
                "email": "ivan.fefer@gmail.com",
                "vkId": "1656860",
                "openId": "http://fefer-ivan.myopenid.com/",
                "firstName": "Ivan",
                "lastName": "Fefer",
                "country": "Russia",
                "city": "Saratov",
                "organization": "Saratov State University",
                "contribution": 0,
                "rank": "international master",
                "rating": 2345,
                "maxRank": "international grandmaster",
                "maxRating": 2635,
                "lastOnlineTimeSeconds": 1729352932,
                "registrationTimeSeconds": 1269784323,
                "friendOfCount": 2220,
                "avatar": "https://userpic.codeforces.org/no-avatar.jpg",
                "titlePhoto": "https://userpic.codeforces.org/no-title.jpg",
            },
            {
                "handle": "DmitriyH",
                "email": "dmitriy.khlopmov@gmail.com",
                "vkId": "55734360",
                "firstName": "Dmitriy",
                "lastName": "Khlopmov",
                "country": "Russia",
                "city": "Moscow",
                "organization": "Unknown",
                "contribution": 0,
                "rank": "candidate master",
                "rating": 2045,
                "maxRank": "international master",
                "maxRating": 2340,
                "lastOnlineTimeSeconds": 1729352932,
                "registrationTimeSeconds": 1269784323,
                "friendOfCount": 201,
                "avatar": "https://userpic.codeforces.org/no-avatar.jpg",
                "titlePhoto": "https://userpic.codeforces.org/no-title.jpg",
            },
        ],
    }


@pytest.mark.asyncio
async def test_get_user_async(
    respx_mock: respx.MockRouter, handles: str, mock_user_response: dict[str, object]
) -> None:
    """Test get_user method asynchronously."""
    _ = respx_mock.get(
        "/user.info",
        params={"handles": handles, "checkHistoricHandles": "True"},
    ).mock(return_value=Response(200, json=mock_user_response))

    client = AsyncMethod()
    users = await client.get_user(handles)

    assert len(users) == 2
    assert users[0].handle == "Fefer_Ivan"
    assert users[1].handle == "DmitriyH"
    await client.close()


@pytest.mark.asyncio
async def test_get_contest_list_async(respx_mock: respx.MockRouter) -> None:
    """Test get_contest_list method asynchronously."""
    mock_response = {
        "status": "OK",
        "result": [
            {
                "id": 1,
                "name": "Codeforces Beta Round #1",
                "type": "CF",
                "phase": "FINISHED",
                "frozen": False,
                "durationSeconds": 7200,
                "startTimeSeconds": 1266588000,
                "relativeTimeSeconds": 12345678,
            }
        ],
    }
    _ = respx_mock.get("/contest.list", params={"gym": "False"}).mock(
        return_value=Response(200, json=mock_response)
    )

    client = AsyncMethod()
    contests = await client.get_contest_list()

    assert len(contests) == 1
    assert contests[0].id == 1
    assert contests[0].name == "Codeforces Beta Round #1"
    await client.close()


@pytest.mark.asyncio
async def test_error_handling_async(respx_mock: respx.MockRouter) -> None:
    """Test error handling when API returns FAILED asynchronously."""
    mock_response = {"status": "FAILED", "comment": "handle: User not found"}
    _ = respx_mock.get("/user.info").mock(
        return_value=Response(200, json=mock_response)
    )

    client = AsyncMethod()
    with pytest.raises(Exception, match="handle: User not found"):
        _ = await client.get_user(handles="invalid_handle")
    await client.close()
