# telegram-retriever

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**telegram-retriever** is a lightweight Python library designed to integrate "Human-in-the-Loop" capabilities into LangChain workflows. 

Unlike standard retrievers that search databases, this tool allows an LLM agent to **pause execution**, send a query to a specific Telegram user, and **synchronously wait** for a text-based reply. The user's reply is returned to the agent as the retrieved context.

## Key Features

- **Interactive Retrieval:** The `invoke()` method blocks until a human replies.
- **Strict Threading:** Validates that the incoming message is an explicit "Reply To" the bot's question.
- **Zero Infrastructure:** Uses Long Polling. No webhooks, public IPs, or databases required.
- **Text-Only:** Filters out stickers, photos, and voice notes to ensure clean LLM input.

## Installation

```bash
pip install telegram-retriever