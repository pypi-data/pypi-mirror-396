"""Article search functionality using DuckDuckGo."""

from ddgs import DDGS


def search_articles(query: str, max_results: int = 5) -> list[str]:
    """
    Search for articles using DuckDuckGo.

    Args:
        query: The search query string.
        max_results: Maximum number of URLs to return (default: 5).

    Returns:
        A list of URLs matching the search query.
    """
    urls = []
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
        for r in results:
            if "href" in r:
                urls.append(r["href"])
    return urls
