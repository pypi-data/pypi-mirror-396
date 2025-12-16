"""Article scraping functionality."""

from newspaper import Article


def scrape_article(url: str) -> dict:
    """
    Scrape an article from a given URL.

    Args:
        url: The URL of the article to scrape.

    Returns:
        A dictionary containing:
            - url: The original URL
            - title: The article title
            - text: The full article text
            - authors: List of article authors
            - publish_date: The publication date as a string

    Raises:
        Exception: If the article cannot be downloaded or parsed.
    """
    article = Article(url)
    article.download()
    article.parse()

    return {
        "url": url,
        "title": article.title,
        "text": article.text,
        "authors": article.authors,
        "publish_date": str(article.publish_date),
    }
