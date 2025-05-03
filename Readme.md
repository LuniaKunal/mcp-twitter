# Twitter MCP Server

Welcome to the Twitter MCP (Multi-Channel Platform) Server! This application helps you manage your Twitter account programmatically with a variety of powerful features.

## Features
- **Get Timeline:** Retrieve your Twitter home timeline.
- **Get Any User's Tweets:** Fetch tweets from any public Twitter user.
- **Hashtag Search:** Search for tweets containing any hashtag (e.g., `#AI`).
- **Get Replies & Summaries:** Retrieve replies to tweets and get summarized insights.
- **User Direct Messages:** Send and receive Twitter DMs.
- **Create Post:** Programmatically create new tweets.
- **Delete Post:** Delete your tweets through the API.
- **And much more...**


[![Twitter MCP Server](https://github.com/user-attachments/assets/1a05ab8f-75b3-4fec-b91d-402f65d41544)](https://smithery.ai/server/@LuniaKunal/mcp-twitter)

![Twitter MCP Server](image.png)

## Getting Started

### Prerequisites
- Python 3.11+
- [uvicorn](https://www.uvicorn.org/) (for running the server)
- Twitter API credentials (set in `.env` file)

### Installation
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file with your Twitter API credentials (see `.env.example`).

### Running the Application

To start the server, run:
```bash
uv run --with twikit --with mcp Path\\src\\tweet_service.py
```

```
{
  "mcpServers": {
  "twitter-mcp": {
    "command": "uv",
    "args": [
      "--directory",
      "Path\\src\\",
      "run",
      "--with",
      "twikit",
      "--with",
      "mcp",
      "tweet_service.py"
    ],
    "env": {
      "COOKIES_PATH": "Path\\cookies.json",
      "ENV_FILE": ".env"  
    }
  }

}
}
```

---

Feel free to contribute or suggest new features!
