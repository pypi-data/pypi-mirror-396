# telegram-retriever

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**telegram-retriever** is a lightweight Python library designed to integrate "Human-in-the-Loop" capabilities into LangChain workflows. 

Unlike standard retrievers that search databases, this tool allows an LLM agent to **pause execution**, send a query to a specific Telegram user, and **synchronously wait** for a text-based reply. The user's reply is returned to the agent as the retrieved context.

## Key Features

- **Interactive Retrieval:** The `invoke()` method blocks execution until a human replies.
- **Strict Threading:** Validates that the incoming message is an explicit "Reply To" the bot's question.
- **Zero Infrastructure:** Uses Long Polling. No webhooks, public IPs, or databases required.
- **Async Support:** Fully supports `ainvoke()` for non-blocking execution in web apps (FastAPI/LangServe).
- **Text-Only:** Filters out stickers, photos, and voice notes to ensure clean LLM input.

## Installation

```bash
pip install telegram-retriever

```

## Quick Start
### 1. Synchronous Usage (Scripts & CLI)This is the simplest way to test. The script will pause and wait for your reply on Telegram.

> **Note:** For security, avoid hardcoding tokens. Use `os.getenv` or `getpass`.

```python
import os
from telegram_retriever import TelegramRetriever

# Initialize the retriever
# Pro-tip: Store your token in an environment variable named 'TELEGRAM_BOT_TOKEN'
retriever = TelegramRetriever(
    bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "YOUR-BOT-TOKEN-HERE"),
    chat_id="..."  # The target User ID
)

print("🤖 Sending question to Telegram...")

# This BLOCKS until you reply to the bot on your phone
result = retriever.invoke("Is the production server ready for deployment?")

# result is a List[Document]
print(f"📩 Received: {result[0].page_content}")
# Output: "Yes, proceed immediately."

```

### 2. Asynchronous Usage (FastAPI / Web Apps)Use `ainvoke` to run the retriever without freezing your entire application server. This runs the polling loop in a background thread.

```python
import asyncio
from telegram_retriever import TelegramRetriever

async def main():
    retriever = TelegramRetriever(
        bot_token="...",
        chat_id="..."
    )
    
    print("🤖 AI is asking...")
    
    # Does not block the main event loop
    docs = await retriever.ainvoke("Do you approve this budget?")
    
    print(f"User Replied: {docs[0].page_content}")

if __name__ == "__main__":
    asyncio.run(main())

```

## How It Works
1. **Send:** The retriever sends your query as a message: `🤖 AI Question: {query}`.
2. **Wait:** It enters a polling loop, checking for updates every 2 seconds.
3. **Validate:** It ignores unrelated messages. It only accepts a message if:
    * It comes from the correct `chat_id`.
    * It is a **Reply** to the specific question asked.
    * It contains **Text** (not stickers or photos).
4. **Return:** The text content is wrapped in a LangChain `Document` and returned.

## Configuration Reference
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `bot_token` | `str` | **Required** | Your Telegram Bot API Token (from @BotFather). |
| `chat_id` | `str` | **Required** | The target User ID or Group ID to ask. |
| `polling_timeout` | `float` | `600.0` | Max time (in seconds) to wait for a reply before raising `TimeoutError`. |
| `polling_interval` | `float` | `2.0` | Time (in seconds) to sleep between polling checks. |

## DevelopmentTo run the test suite (requires `pytest` and `pytest-asyncio`):

```bash
# Install test dependencies
pip install .[test]

# Run tests
pytest

```