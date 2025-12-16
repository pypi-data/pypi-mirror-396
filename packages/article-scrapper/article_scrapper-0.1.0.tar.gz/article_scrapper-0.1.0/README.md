# Article Scrapper

A simple Python library to scrape articles from the web.

## Installation

```bash
pip install article_scrapper
```

## Features

- **Scrape articles**: Extract title, text, authors, and publication date from any article URL
- **Search articles**: Find articles using DuckDuckGo search
- **Pipeline**: Combine search and scrape to get article content for any query

## Usage

### Scrape a single article

```python
from article_scrapper import scrape_article

article = scrape_article("https://example.com/article")
print(article["title"])
print(article["text"])
print(article["authors"])
print(article["publish_date"])
```

### Search for articles

```python
from article_scrapper import search_articles

urls = search_articles("python programming", max_results=5)
for url in urls:
    print(url)
```

### Search and scrape articles

```python
from article_scrapper import get_articles_for_query

articles = get_articles_for_query("artificial intelligence news", max_results=5)
for article in articles:
    print(f"Title: {article['title']}")
    print(f"URL: {article['url']}")
    print(f"Text: {article['text'][:200]}...")
    print("---")
```

## API Reference

### `scrape_article(url: str) -> dict`

Scrape an article from a given URL.

**Parameters:**
- `url`: The URL of the article to scrape

**Returns:**
A dictionary containing:
- `url`: The original URL
- `title`: The article title
- `text`: The full article text
- `authors`: List of article authors
- `publish_date`: The publication date as a string

### `search_articles(query: str, max_results: int = 5) -> list[str]`

Search for articles using DuckDuckGo.

**Parameters:**
- `query`: The search query string
- `max_results`: Maximum number of URLs to return (default: 5)

**Returns:**
A list of URLs matching the search query.

### `get_articles_for_query(query: str, max_results: int = 5) -> list[dict]`

Search for articles and scrape their content.

**Parameters:**
- `query`: The search query string
- `max_results`: Maximum number of articles to retrieve (default: 5)

**Returns:**
A list of article dictionaries (same format as `scrape_article`).

## Dependencies

- [newspaper3k](https://github.com/codelucas/newspaper) - Article scraping
- [ddgs](https://github.com/deedy5/duckduckgo_search) - DuckDuckGo search
- [lxml-html-clean](https://github.com/lxml/lxml-html-clean) - HTML cleaning

## License

MIT License
