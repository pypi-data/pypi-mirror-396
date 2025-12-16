"""
Article Scrapper - A simple library to scrape articles from the web.

This package provides utilities to:
- Scrape article content from a URL
- Search for articles using DuckDuckGo
- Get articles for a search query (combines search + scrape)
"""

from article_scrapper.scrapper import scrape_article
from article_scrapper.search import search_articles
from article_scrapper.pipeline import get_articles_for_query

__version__ = "0.1.0"
__all__ = ["scrape_article", "search_articles", "get_articles_for_query"]
