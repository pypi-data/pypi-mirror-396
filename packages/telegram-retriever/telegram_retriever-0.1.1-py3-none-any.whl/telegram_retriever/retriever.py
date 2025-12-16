import time
from typing import List, Optional

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field, PrivateAttr, SecretStr

from .client import TelegramClient


class TelegramRetriever(BaseRetriever):
    """
    A Human-in-the-Loop retriever that pauses execution to ask a user a question
    via Telegram.

    It blocks until a valid text reply is received.
    """

    bot_token: SecretStr = Field(..., description="Telegram Bot API Token")
    chat_id: str = Field(..., description="Target Chat ID (User or Group)")
    polling_timeout: float = Field(
        default=600.0, description="Max wait time for a reply in seconds"
    )
    polling_interval: float = Field(default=2.0, description="Sleep time between polls")

    # Private attributes (not part of the Pydantic schema for serialization)
    _client: TelegramClient = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize the HTTP client with the plain text token
        self._client = TelegramClient(bot_token=self.bot_token.get_secret_value())

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        """
        Synchronous blocking call that sends a question and waits for a reply.
        """

        # 1. SEND: Format and send the question
        formatted_query = f"🤖 AI Question: {query}"
        send_response = self._client.send_message(self.chat_id, formatted_query)

        # 2. RECORD: Capture the Message ID of the question we just sent
        question_message_id = send_response["result"]["message_id"]

        # 3. BLOCK & POLL: Wait for the specific reply
        start_time = time.time()
        last_update_id: Optional[int] = None

        while True:
            # Check for timeout
            if (time.time() - start_time) > self.polling_timeout:
                raise TimeoutError(
                    f"Waited {self.polling_timeout}s for a reply on Telegram "
                    "but received none."
                )

            # Poll for updates
            try:
                updates_response = self._client.get_updates(offset=last_update_id)
                updates = updates_response.get("result", [])
            except Exception as e:
                # Log error or print warning, then retry loop
                print(f"Polling error: {e}")
                time.sleep(self.polling_interval)
                continue

            for update in updates:
                # Update offset to acknowledge processing
                last_update_id = update["update_id"] + 1

                message = update.get("message")
                if not message:
                    continue

                # 4. STRICT VALIDATION

                # A. Target Match: Must be from the configured chat_id
                # Note: telegram API returns chat IDs as integers usually
                if str(message["chat"]["id"]) != str(self.chat_id):
                    continue

                # B. Reply Match: Must be a reply to OUR question
                reply_to = message.get("reply_to_message")
                if not reply_to or reply_to["message_id"] != question_message_id:
                    continue

                # C. Content Match: Must contain text (no stickers, photos)
                text_content = message.get("text")
                if not text_content:
                    # Logic: We see the reply, but it's invalid content.
                    # We ignore it and keep waiting for text.
                    print("Received non-text reply. Ignoring...")
                    continue

                # 5. RETURN: If we get here, we have a valid answer.
                return [
                    Document(
                        page_content=text_content,
                        metadata={
                            "source": "telegram",
                            "user_id": message.get("from", {}).get("id"),
                            "username": message.get("from", {}).get("username"),
                            "reply_to_msg_id": question_message_id,
                        },
                    )
                ]

            # Sleep briefly to prevent tight looping if network is fast/mocked
            time.sleep(self.polling_interval)

    # Async implementation is required by BaseRetriever, but we wrap the sync logic
    # because the nature of this tool is blocking/sequential.
    async def _aget_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        return self._get_relevant_documents(query, run_manager=run_manager)
