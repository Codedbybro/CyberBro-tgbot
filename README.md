# CyberBro

A personal Telegram utility bot built with python-telegram-bot.

## Features
- Weather lookup through wttr.in
- Basic calculator
- Random password generation using Python's secrets module
- IP/domain information lookup through ipwho.is
- Reply-keyboard menu

## Stack
- Python 3.10+
- python-telegram-bot (async API)
- requests
- python-dotenv

## Setup
1. Create a bot with @BotFather and copy its token.
2. Clone this repository and enter its directory.
3. Create and activate a virtual environment: python3 -m venv .venv && source .venv/bin/activate
4. Install dependencies: python -m pip install -r requirements.txt
5. Create a .env file in the project root with BOT_TOKEN=put_your_bot_token_here
6. Start the bot: python bot.py

## Configuration and security
- BOT_TOKEN is loaded from the environment using python-dotenv.
- Keep .env out of Git; the repository .gitignore excludes it.
- If a token is ever committed or shared, revoke it with BotFather and issue a new one.
- Third-party API calls require network access and may be unavailable or rate-limited.

## Checks
GitHub Actions compiles the Python source on pushes and pull requests. The workflow does not contact Telegram or require a bot token.

## Project layout
- .github/workflows/ci.yml — CI workflow
- .gitignore — excludes local secrets and generated files
- bot.py — bot handlers and startup
- requirements.txt — dependencies

## Learning goals
This project is a practical exercise in asynchronous Telegram handlers, environment-based configuration, HTTP requests, Linux deployment, and basic CI. It is a learning project; review and test the handlers before using it as a public production bot.