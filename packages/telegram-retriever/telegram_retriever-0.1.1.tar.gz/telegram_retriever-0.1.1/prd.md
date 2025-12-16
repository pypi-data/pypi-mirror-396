### Product Requirements Document (PRD)
**Project Name:** telegram-retriever

**Date:** 2025-12-13

**Version:** 1.0

---

## 1. Executive Summary:`telegram-retriever` is a lightweight Python library designed to integrate "Human-in-the-Loop" capabilities into LangChain and LangGraph workflows.

Unlike standard retrievers that search databases, this tool allows an LLM agent to **pause execution**, send a query to a specific Telegram user, and **synchronously wait** for a text-based reply. The user's reply is then returned to the agent as the retrieved context. The project will be released as open source under the MIT License.

It prioritizes simplicity and strict interaction logic: it relies on the standard **Telegram Bot API (HTTP)** and enforces that the retrieved context comes strictly from a **direct reply** to the agent's question.

## 2. Objectives & Scope
### 2.1 Goals* **Interactive Retrieval**: The `invoke()` method must block (wait) until a human replies on Telegram.
* **Strict Threading**: The retriever must verify that the incoming message is an explicit "Reply To" the specific question sent by the bot. Unrelated messages in the chat must be ignored.
* **Text-Only Constraint**: The system must only accept text messages. Photos, voice notes, files, or stickers must be ignored to ensure clean input for the LLM.
* **Simplest Auth**: Use standard Bot API Tokens (from @BotFather). No "Sessions", "API Hash", or "OTP" required.
* **Zero Infrastructure**: No webhooks, public IPs, or databases required. Uses "Long Polling" to catch replies.

### 2.2 Non-Goals* **Multimedia Handling**: This tool does not process images, audio, or documents.
* **History Search**: This tool does not look at past messages. It only cares about the reply to the *current* prompt.
* **Async Concurrency**: While it handles async calls, the logic is inherently sequential (Question -> Wait -> Answer).

## 3. Functional Requirements
### 3.1 Configuration (Input Variables)Configuration is passed directly via the class constructor using Pydantic models.

* `bot_token` (SecretStr): The token from @BotFather (e.g., `123456:ABC-DEF...`).
* `chat_id` (str | int): The target user ID or group ID who will answer the questions.
* `polling_timeout` (float): How long to wait for a reply before giving up (default: 600s).
* `polling_interval` (float): Frequency of checks in seconds (default: 2s).

### 3.2 The Retriever (Core Component)* **Class Name**: `TelegramRetriever`
* **Inheritance**: `langchain_core.retrievers.BaseRetriever`

* **Invocation Logic (`invoke(query)`)**
    1. **Send**: Formats the `query` (e.g., "🤖 AI Question: {query}") and sends it to `chat_id`.
    2. **Record**: Saves the `message_id` of the sent question in a local variable.
    3. **Block & Poll**: Enters a loop checking for updates via the `getUpdates` API.
    4. **Strict Validation**: Every incoming message is checked against the following rules. **All** must pass:

        | Criterion | Requirement |
        | --- | --- |
        | **Target Match** | Message comes from the configured `chat_id`. |
        | **Reply Match** | Message is a "Reply To" the specific `message_id` recorded in step 2. |
        | **Content Match** | Message contains `text`. Photos, stickers, or voice notes are ignored. |

    5. **Return**: Once a message passes all validation, return a `Document` with the text answer.
    6. **Timeout**: If `polling_timeout` expires, raise `TimeoutError`.

### 3.3 The "No Memory" ImplementationTo satisfy the "no external memory" requirement:

* The "Context" is strictly the **Message ID** of the current question.
* This ID is held in the local Python variable stack during the `invoke()` call.
* Once the function returns, the ID is forgotten. No databases or files are touched.

## 4. Technical Architecture
### 4.1 Flow Diagram
```text
[LLM Agent]
    |
    |  1. invoke("Do we have budget approval?")
    v
[TelegramRetriever] --(HTTP POST)--> [Telegram Server]
    |                                            |
    | (Pauses & Polls...)                        |--> User's Phone: "Do we have budget approval?"
    |                                            |
    |                               User Actions:
    |                               (A) Sends Sticker -> [Ignored by Retriever]
    |                               (B) Replies "Yes" -> [Accepted by Retriever]
    |                                            |
    | <--(HTTP Response)-- [Telegram Server] <---|
    |
    | (Validates: Is Text? YES. Is Reply? YES.)
    v
[Result: Document(page_content="Yes")]

```

### 4.2 Tech Stack* **Language**: Python 3.9+
* **Core Dependencies**:
* `langchain-core`: For `BaseRetriever` interface.
* `pydantic`: For data validation.
* `requests` or `httpx`: For simple HTTP calls to the Bot API.


* **Packaging**: `hatchling` or `poetry-core` (PEP 517).

## 5. API Specification###5.1 Usage Example
```python
from telegram_retriever import TelegramRetriever

# Simple Config - No Sessions or Phone Login required!
retriever = TelegramRetriever(
    bot_token="123456:ABC-DEF...",
    chat_id="987654321",
    polling_timeout=120
)

print("Ask the telegram...")

# The script will PAUSE here until you reply on your phone
docs = retriever.invoke("Is the production server ready?")

print(docs[0].page_content) 
# Output: "Yes, it is ready."

```

### 5.2 Error & Logic Handling
| Scenario | Behavior |
| --- | --- |
| **Timeout** | Raises `TimeoutError` if the user does not reply within `polling_timeout`. |
| **Non-Reply Message** | Ignores any message that is not a direct "Reply" to the bot's question (e.g., user sends a new message instead of swiping to reply). |
| **Media/Non-Text** | Ignores photos, stickers, voice notes, or documents, even if they are replies. Continues polling for text. |
| **Wrong User** | Ignores replies from `chat_id`s that do not match the configuration. |
| **Network Fail** | Retries polling on transient HTTP errors (5xx), fails on Auth errors (401). |

## 6. Project Structure (PyPI Ready)
```text
telegram-retriever/
├── LICENSE
├── pyproject.toml       # Build definition
├── README.md            # Documentation
├── src/
│   └── telegram_retriever/
│       ├── __init__.py
│       ├── retriever.py  # Main Logic (Loop, Poll, Validate)
│       └── client.py     # Simple HTTP Wrapper for Bot API
└── tests/
    ├── __init__.py
    └── test_telegram.py     # Mocked unit tests
```