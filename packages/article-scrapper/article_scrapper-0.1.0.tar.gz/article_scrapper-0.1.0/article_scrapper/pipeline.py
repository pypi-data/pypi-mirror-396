"""Pipeline for searching and scraping articles."""

from article_scrapper.search import search_articles
from article_scrapper.scrapper import scrape_article


def get_articles_for_query(query: str, max_results: int = 5) -> list[dict]:
    """
    Search for articles and scrape their content.

    This function combines search and scraping: it first searches for articles
    matching the query, then scrapes the content of each result.

    Args:
        query: The search query string.
        max_results: Maximum number of articles to retrieve (default: 5).

    Returns:
        A list of dictionaries, each containing article data:
            - url: The article URL
            - title: The article title
            - text: The full article text
            - authors: List of article authors
            - publish_date: The publication date as a string

    Note:
        Articles that fail to scrape or have empty text are silently skipped.
    """
    urls = search_articles(query, max_results)
    articles = []

    for url in urls:
        try:
            article = scrape_article(url)
            if article["text"].strip():
                articles.append(article)
        except Exception as e:
            print(f"Skipping {url}: {e}")

    return articles
