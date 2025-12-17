from unittest.mock import Mock, patch

import pytest

from telegram_retriever import TelegramRetriever

# --- Constants ---
BOT_TOKEN = "123456:TEST-TOKEN"
TARGET_CHAT_ID = 999999
QUESTION_MSG_ID = 100
VALID_UPDATE_ID = 500


@pytest.fixture
def mock_httpx_client():
    """
    Mocks the internal httpx client.
    Pre-configures the .post() method to return a success
    response to save repetition in tests.
    """
    with patch("telegram_retriever.client.httpx.Client") as mock_client_cls:
        mock_instance = Mock()
        mock_client_cls.return_value = mock_instance

        # Default behavior: successful sendMessage response
        mock_instance.post.return_value.json.return_value = {
            "ok": True,
            "result": {"message_id": QUESTION_MSG_ID, "chat": {"id": TARGET_CHAT_ID}},
        }

        yield mock_instance


@pytest.fixture
def retriever(mock_httpx_client):
    """Initializes the TelegramRetriever with short polling intervals for speed."""
    return TelegramRetriever(
        bot_token=BOT_TOKEN,
        chat_id=str(TARGET_CHAT_ID),
        polling_timeout=2.0,
        polling_interval=0.1,
    )


@pytest.fixture
def create_update():
    """Factory fixture to generate Telegram update dictionaries."""

    def _create(text=None, update_id=VALID_UPDATE_ID, **kwargs):
        message_body = {
            "message_id": 101,
            "chat": {"id": TARGET_CHAT_ID},
            "reply_to_message": {"message_id": QUESTION_MSG_ID},
            "from": {"id": TARGET_CHAT_ID, "username": "tester"},
        }

        if text:
            message_body["text"] = text

        # Merge extra fields (e.g., sticker)
        message_body.update(kwargs)

        return {
            "update_id": update_id,
            "message": message_body,
        }

    return _create


@pytest.fixture
def mock_get_updates(mock_httpx_client):
    """Helper to configure the 'get' (polling) response."""

    def _set_response(updates_list):
        mock_httpx_client.get.return_value.json.return_value = {
            "ok": True,
            "result": updates_list,
        }

    return _set_response


# --- Tests ---


def test_happy_path(retriever, mock_httpx_client, create_update, mock_get_updates):
    """
    Scenario: Synchronous invoke() -> Bot sends query -> User replies text.
    """
    # Arrange
    valid_reply = create_update(text="Yes, proceed.")
    mock_get_updates([valid_reply])

    # Act
    docs = retriever.invoke("Are we ready?")

    # Assert
    assert len(docs) == 1
    assert docs[0].page_content == "Yes, proceed."
    assert docs[0].metadata["source"] == "telegram"

    mock_httpx_client.post.assert_called_once()
    # Verify the question text was actually sent in the JSON payload
    sent_payload = mock_httpx_client.post.call_args[1]["json"]
    assert "Are we ready?" in sent_payload["text"]


@pytest.mark.asyncio
async def test_async_happy_path(
    retriever, mock_httpx_client, create_update, mock_get_updates
):
    """
    Scenario: Asynchronous ainvoke() -> Verifies thread offloading works.
    """
    # Arrange
    valid_reply = create_update(text="Async answer")
    mock_get_updates([valid_reply])

    # Act
    docs = await retriever.ainvoke("Async query?")

    # Assert
    assert docs[0].page_content == "Async answer"

    sent_payload = mock_httpx_client.post.call_args[1]["json"]
    assert "Async query?" in sent_payload["text"]


def test_timeout_error(retriever, mock_httpx_client, mock_get_updates):
    """
    Scenario: Bot polls -> No valid reply -> Time exceeds limit -> Raises TimeoutError.
    """
    # Arrange: Return empty list (no updates) indefinitely
    mock_get_updates([])

    # Act & Assert
    with pytest.raises(TimeoutError) as exc_info:
        retriever.invoke("Hello?")

    assert "Waited" in str(exc_info.value)


def test_garbage_filter(retriever, mock_httpx_client, create_update):
    """
    Scenario: Bot polls -> Receives Sticker (Ignore) -> Receives Text (Accept).
    """
    # Arrange
    sticker_update = create_update(sticker={"file_id": "1234"}, update_id=500)
    text_update = create_update(text="Valid Text Answer", update_id=501)

    # We mock .json() explicitly to return different values on consecutive calls
    mock_httpx_client.get.side_effect = [
        Mock(**{"json.return_value": {"ok": True, "result": [sticker_update]}}),
        Mock(**{"json.return_value": {"ok": True, "result": [text_update]}}),
    ]

    # Act
    docs = retriever.invoke("Send me text only")

    # Assert
    assert docs[0].page_content == "Valid Text Answer"
    assert mock_httpx_client.get.call_count == 2
