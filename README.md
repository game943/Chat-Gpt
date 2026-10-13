# Ask-Anything AI

A terminal chat assistant powered by Claude that can answer questions on any topic. It searches the web for current information when it needs to and remembers the conversation so you can ask follow-ups.

## Setup

1. Install Python 3.10+.
2. Install the dependency:
   ```bash
   pip install -r requirements.txt
   ```
3. Get an API key from https://platform.claude.com and set it:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"     # macOS/Linux
   setx ANTHROPIC_API_KEY "your-key-here"       # Windows (then open a new terminal)
   ```

## Use it

```bash
python ask.py                        # chat
python ask.py "Why is the sky blue?" # one question
```

In chat, type `/new` to start a new conversation or `/quit` to exit.
