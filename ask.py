#!/usr/bin/env python3
"""Ask-anything AI: a terminal chat assistant powered by Claude.

Setup (one time):
    pip install anthropic
    export ANTHROPIC_API_KEY="your-key"   # get one at https://platform.claude.com
                                          # (Windows: setx ANTHROPIC_API_KEY "your-key")

Usage:
    python ask.py                      # interactive chat
    python ask.py "your question"      # ask one question and exit

Commands in chat: /new starts a fresh conversation, /quit exits.
"""

import sys

import anthropic

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = (
    "You are a friendly, knowledgeable assistant who can help with any topic: "
    "science, history, math, coding, writing, cooking, travel, health, money, "
    "and everyday questions. Give clear, accurate answers. Use the web search "
    "tool for current events, prices, or anything that may have changed "
    "recently, and mention your sources when you do. If you are unsure, say so."
)

TOOLS = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}]

client = anthropic.Anthropic()


def ask(messages):
    """Stream Claude's answer to the conversation and append it to messages."""
    while True:
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=64000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            output_config={"effort": "medium"},
            # If a request is declined by a safety classifier, retry it on a
            # fallback model automatically.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            for event in stream:
                if event.type == "content_block_start" and event.content_block.type == "server_tool_use":
                    print("\n[searching the web...]\n", flush=True)
                elif event.type == "text":
                    print(event.text, end="", flush=True)
            response = stream.get_final_message()

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "pause_turn":
            # Long-running web search turn: send it back so Claude can continue.
            continue
        if response.stop_reason == "refusal":
            print("\n[Sorry, I can't help with that one.]")
        elif response.stop_reason == "max_tokens":
            print("\n[Answer was cut off because it hit the length limit.]")
        print()
        return


def main():
    messages = []

    if len(sys.argv) > 1:
        messages.append({"role": "user", "content": " ".join(sys.argv[1:])})
        ask(messages)
        return

    print("Ask me anything! (/new = new chat, /quit = exit)\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question in ("/quit", "/exit"):
            break
        if question == "/new":
            messages = []
            print("Started a new conversation.\n")
            continue

        start = len(messages)
        messages.append({"role": "user", "content": question})
        print("\nAI: ", end="", flush=True)
        try:
            ask(messages)
        except anthropic.AuthenticationError:
            print("\nYour API key is missing or invalid. Set ANTHROPIC_API_KEY and try again.")
            return
        except anthropic.RateLimitError:
            print("\nToo many requests right now; wait a moment and try again.")
            del messages[start:]
        except anthropic.APIStatusError as e:
            print(f"\nAPI error ({e.status_code}): {e.message}")
            del messages[start:]
        except anthropic.APIConnectionError:
            print("\nCouldn't reach the API. Check your internet connection.")
            del messages[start:]
        print()


if __name__ == "__main__":
    main()
