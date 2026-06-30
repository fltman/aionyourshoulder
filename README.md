# AI on Your Shoulder

[![Support me on Patreon](https://img.shields.io/badge/Patreon-Support%20my%20work-FF424D?style=flat&logo=patreon&logoColor=white)](https://www.patreon.com/AndersBjarby)

A little companion that watches what you're doing and talks to you about it. Every 30 seconds it takes a screenshot, sends it to GPT-4o for a quick look, and speaks the feedback aloud — delivered, by default, as a slightly drunk Scottish medieval mad sorcerer with a heavy Monty Python accent.

## How it works

- Captures the screen on a loop (macOS `screencapture`, with a `pyautogui` fallback)
- Sends each screenshot to GPT-4o for short, casual feedback
- Speaks the response with ElevenLabs and plays it via pygame
- Cleans up old screenshots and audio files automatically

## Setup

Requires `OPENAI_API_KEY` and `ELEVENLABS_API_KEY` in a `.env` file.

```bash
pip install pyautogui pillow requests python-dotenv pygame openai
python screenshot_analyzer.py
```

Press Ctrl+C to stop. Edit the system prompt in `screenshot_analyzer.py` to change the persona.

## Tech

Python, OpenAI (GPT-4o vision), ElevenLabs TTS, pygame, Pillow.
