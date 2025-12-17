from typing import Any, Dict, Optional

import httpx


class TelegramClient:
    """
    A lightweight synchronous wrapper around the Telegram Bot API.
    """

    def __init__(self, bot_token: str, base_url: str = "https://api.telegram.org"):
        self.bot_token = bot_token
        self.api_url = f"{base_url}/bot{bot_token}"
        self.client = httpx.Client(
            timeout=None
        )  # Disable default timeout for long polling

    def send_message(self, chat_id: str, text: str) -> Dict[str, Any]:
        """
        Sends a text message to the specified chat_id.
        Returns the raw JSON response from Telegram.
        """
        url = f"{self.api_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}

        response = self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_updates(
        self, offset: Optional[int] = None, timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Fetches new updates using Long Polling.

        :param offset: Identifier of the first update to be returned.
        :param timeout: Timeout in seconds for long polling
        (wait time at Telegram server).
        """
        url = f"{self.api_url}/getUpdates"
        params = {
            "timeout": timeout,
            "allowed_updates": ["message"],  # We only care about messages
        }
        if offset is not None:
            params["offset"] = offset

        # We set the read timeout slightly higher than the poll timeout
        # to ensure we don't cut the connection prematurely.
        response = self.client.get(url, params=params, timeout=timeout + 5)
        response.raise_for_status()
        return response.json()
