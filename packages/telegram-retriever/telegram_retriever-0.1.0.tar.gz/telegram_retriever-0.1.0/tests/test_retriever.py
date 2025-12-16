from unittest.mock import MagicMock, Mock, patch

import pytest

from telegram_retriever import TelegramRetriever

# Constants for Mocking
BOT_TOKEN = "123456:TEST-TOKEN"
TARGET_CHAT_ID = "999999"
QUESTION_MSG_ID = 100
VALID_UPDATE_ID = 500


@pytest.fixture
def mock_httpx_client():
    """Mocks the internal httpx client used by TelegramClient."""
    with patch("telegram_retriever.client.httpx.Client") as mock_client_cls:
        mock_instance = Mock()
        mock_client_cls.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def retriever(mock_httpx_client):
    """Initializes a retriever instance with short timeouts for testing."""
    return TelegramRetriever(
        bot_token=BOT_TOKEN,
        chat_id=TARGET_CHAT_ID,
        polling_timeout=2.0,  # Short timeout for fast tests
        polling_interval=0.1,  # Fast polling
    )


def mock_send_response():
    """Helper to generate a successful sendMessage response."""
    return {
        "ok": True,
        "result": {"message_id": QUESTION_MSG_ID, "chat": {"id": int(TARGET_CHAT_ID)}},
    }


def mock_update_response(updates_list):
    """Helper to generate a getUpdates response with a list of updates."""
    return {"ok": True, "result": updates_list}


# --- Test Cases ---


def test_happy_path(retriever, mock_httpx_client):
    """
    Scenario: Bot sends query -> User replies text -> Returns Document.
    """
    # 1. Setup Mock Responses
    # Call 1: sendMessage (The Question)
    # Call 2: getUpdates (The Answer)

    mock_httpx_client.post.return_value.json.return_value = mock_send_response()

    valid_reply = {
        "update_id": VALID_UPDATE_ID,
        "message": {
            "message_id": 101,
            "chat": {"id": int(TARGET_CHAT_ID)},
            "reply_to_message": {"message_id": QUESTION_MSG_ID},
            "text": "Yes, proceed.",
            "from": {"id": int(TARGET_CHAT_ID), "username": "tester"},
        },
    }

    mock_httpx_client.get.return_value.json.return_value = mock_update_response(
        [valid_reply]
    )

    # 2. Execute
    docs = retriever.invoke("Are we ready?")

    # 3. Verify
    assert len(docs) == 1
    assert docs[0].page_content == "Yes, proceed."
    assert docs[0].metadata["source"] == "telegram"

    # Ensure sendMessage was called correctly
    mock_httpx_client.post.assert_called_once()
    args, kwargs = mock_httpx_client.post.call_args
    assert kwargs["json"]["chat_id"] == TARGET_CHAT_ID
    assert "Are we ready?" in kwargs["json"]["text"]


def test_timeout_error(retriever, mock_httpx_client):
    """
    Scenario: Bot waits -> Time exceeds limit -> Raises TimeoutError.
    """
    # 1. Setup Mock Responses
    mock_httpx_client.post.return_value.json.return_value = mock_send_response()

    # Always return empty updates (simulating silence)
    mock_httpx_client.get.return_value.json.return_value = mock_update_response([])

    # 2. Execute & Verify
    with pytest.raises(TimeoutError) as exc_info:
        retriever.invoke("Hello?")

    assert "Waited" in str(exc_info.value)


def test_garbage_filter(retriever, mock_httpx_client):
    """
    Scenario: Bot polls -> Receives Sticker -> Ignores
    -> Receives Text -> Returns Document.
    """
    # 1. Setup Mock Responses
    mock_httpx_client.post.return_value.json.return_value = mock_send_response()

    sticker_update = {
        "update_id": VALID_UPDATE_ID,
        "message": {
            "message_id": 101,
            "chat": {"id": int(TARGET_CHAT_ID)},
            "reply_to_message": {"message_id": QUESTION_MSG_ID},
            "sticker": {"file_id": "1234"},  # No 'text' field
        },
    }

    valid_text_update = {
        "update_id": VALID_UPDATE_ID + 1,
        "message": {
            "message_id": 102,
            "chat": {"id": int(TARGET_CHAT_ID)},
            "reply_to_message": {"message_id": QUESTION_MSG_ID},
            "text": "Valid Text Answer",
        },
    }

    # Simulation:
    # First poll returns a sticker (should be ignored)
    # Second poll returns valid text (should be accepted)
    mock_httpx_client.get.side_effect = [
        MagicMock(json=MagicMock(return_value=mock_update_response([sticker_update]))),
        MagicMock(
            json=MagicMock(return_value=mock_update_response([valid_text_update]))
        ),
    ]

    # 2. Execute
    docs = retriever.invoke("Send me text only")

    # 3. Verify
    assert docs[0].page_content == "Valid Text Answer"
    assert mock_httpx_client.get.call_count == 2  # Proves it looped once


def test_wrong_user_and_threading(retriever, mock_httpx_client):
    """
    Scenario:
    1. Stranger replies (Ignore)
    2. Correct user replies but NOT a reply-to (Ignore)
    3. Correct user replies correctly (Accept)
    """
    mock_httpx_client.post.return_value.json.return_value = mock_send_response()

    # Update 1: Wrong User (Stranger)
    stranger_update = {
        "update_id": 1,
        "message": {
            "chat": {"id": 12345},  # Wrong Chat ID
            "reply_to_message": {"message_id": QUESTION_MSG_ID},
            "text": "I am a hacker",
        },
    }

    # Update 2: Correct User, but NOT a reply (random message in chat)
    random_msg_update = {
        "update_id": 2,
        "message": {
            "chat": {"id": int(TARGET_CHAT_ID)},
            # Missing "reply_to_message"
            "text": "Just chatting...",
        },
    }

    # Update 3: Correct User, Correct Reply
    correct_update = {
        "update_id": 3,
        "message": {
            "chat": {"id": int(TARGET_CHAT_ID)},
            "reply_to_message": {"message_id": QUESTION_MSG_ID},
            "text": "The Real Answer",
        },
    }

    # Chain the responses
    mock_httpx_client.get.side_effect = [
        MagicMock(json=MagicMock(return_value=mock_update_response([stranger_update]))),
        MagicMock(
            json=MagicMock(return_value=mock_update_response([random_msg_update]))
        ),
        MagicMock(json=MagicMock(return_value=mock_update_response([correct_update]))),
    ]

    docs = retriever.invoke("Who are you?")

    assert docs[0].page_content == "The Real Answer"
    assert mock_httpx_client.get.call_count == 3
