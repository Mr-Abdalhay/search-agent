# News Search Agent

A small Flask app that searches for news articles across multiple sources and can generate an AI-powered summary using Google Gemini.

## Features

- Search news by query and date range
- Include custom article URLs to scrape
- Aggregates results from NewsAPI and popular news RSS feeds
- AI-powered summary (Gemini) of found articles
- Server-side filtering to suppress undesired sources or items

## Requirements

Install dependencies with pip:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to set your API keys (or manage them via environment variables if you prefer):

- `NEWSAPI_KEY` - API key from https://newsapi.org (optional, but recommended)
- `GEMINI_API_KEY` - Google Gemini API key (required for summaries)

Note: `config.py` in this repository may contain example values. Do not commit real secrets to public repos.

## Run the app

```powershell
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Usage

- Enter a search term and the number of days back to search
- (Optional) Add custom URLs using the "Add URL" button; multiple URLs are supported
- Submit the form to see aggregated articles and an AI-generated summary

## Filtering

The server strips out articles that match configured blacklist patterns (by title, source, or URL) before rendering. This helps hide undesired items from end users.

## Troubleshooting

- If the Gemini summarizer fails to initialize, summaries will be disabled but the search results will still display.
- If you hit rate limits on NewsAPI or Gemini, consider increasing the time window between requests or upgrading API plans.

## License

MIT
