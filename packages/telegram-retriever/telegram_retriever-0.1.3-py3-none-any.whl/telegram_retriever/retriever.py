import asyncio
import logging
import time
from typing import List, Optional

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field, PrivateAttr, SecretStr, model_validator

from .client import TelegramClient

logger = logging.getLogger(__name__)


class TelegramRetriever(BaseRetriever):
    """
    A Human-in-the-Loop retriever that pauses execution to ask a user a question
    via Telegram.

    It blocks (or awaits) until a valid text reply is received or a timeout occurs.
    """

    bot_token: SecretStr = Field(..., description="Telegram Bot API Token")
    chat_id: str = Field(..., description="Target Chat ID (User or Group)")
    polling_timeout: float = Field(
        default=600.0, description="Max wait time for a reply in seconds"
    )
    polling_interval: float = Field(default=2.0, description="Sleep time between polls")

    _client: TelegramClient = PrivateAttr()

    @model_validator(mode="after")
    def initialize_client(self) -> "TelegramRetriever":
        """
        Initializes the TelegramClient after Pydantic has validated
        that bot_token is present and correct.
        """
        token = self.bot_token.get_secret_value()
        self._client = TelegramClient(bot_token=token)
        return self

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        """
        Synchronous blocking call that sends a question and polls for a reply.
        """
        try:
            formatted_query = f"🤖 AI Question: {query}"
            send_response = self._client.send_message(self.chat_id, formatted_query)

            # Ensure we actually got a message ID back
            if not send_response or "result" not in send_response:
                logger.error("Failed to send Telegram message.")
                return []

            question_message_id = send_response["result"]["message_id"]

            # Use monotonic time for robust duration calculation
            start_time = time.monotonic()
            last_update_id: Optional[int] = None

            logger.info(
                f"Question sent (ID: {question_message_id}). Waiting for reply..."
            )

            while True:
                # 1. Check Timeout
                if (time.monotonic() - start_time) > self.polling_timeout:
                    error_msg = f"Waited {self.polling_timeout}s but received no reply."
                    logger.error(error_msg)
                    raise TimeoutError(error_msg)

                # 2. Poll Updates
                try:
                    updates_response = self._client.get_updates(offset=last_update_id)
                    updates = updates_response.get("result", [])
                except Exception as e:
                    logger.warning(f"Telegram polling error: {e}")
                    time.sleep(self.polling_interval)
                    continue

                # 3. Process Updates
                for update in updates:
                    # Advance the offset to avoid reprocessing
                    last_update_id = update["update_id"] + 1

                    result_doc = self._parse_valid_reply(
                        update.get("message"), question_message_id
                    )

                    if result_doc:
                        logger.info("Valid reply received via Telegram.")
                        return [result_doc]

                # 4. Wait before next poll
                time.sleep(self.polling_interval)

        except Exception as e:
            logger.exception("Unexpected error in TelegramRetriever")
            raise e

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        """
        Asynchronous wrapper.

        Since the underlying TelegramClient and polling logic is blocking/synchronous,
        we run the synchronous method in a separate thread to avoid blocking the
        async event loop.
        """
        return await asyncio.get_running_loop().run_in_executor(
            None,
            self._get_relevant_documents,
            query,
            # We pass run_manager kwarg explicitly, though run_in_executor
            # argument unpacking can be tricky, passing as positional or via lambda is
            # safer
            # if the signature gets complex. Here, simpler is better:
        )

    def _parse_valid_reply(
        self, message: Optional[dict], question_msg_id: int
    ) -> Optional[Document]:
        """
        Validates a message dictionary and returns a Document if it matches
        the criteria (reply to the specific question, from the correct chat).
        """
        if not message:
            return None

        # Validate Chat ID
        if str(message.get("chat", {}).get("id")) != str(self.chat_id):
            return None

        # Validate it is a Reply to our specific bot message
        reply_to = message.get("reply_to_message")
        if not reply_to or reply_to.get("message_id") != question_msg_id:
            return None

        # Validate Content
        text_content = message.get("text")
        if not text_content:
            logger.debug("Received non-text reply (photo/sticker). Ignoring.")
            return None

        return Document(
            page_content=text_content,
            metadata={
                "source": "telegram",
                "user_id": message.get("from", {}).get("id"),
                "username": message.get("from", {}).get("username"),
                "reply_to_msg_id": question_msg_id,
            },
        )
