from langchain_core.tools import tool
from ddgs import DDGS


def _web_search(query: str, max_results: int = 4) -> str:
    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(query, max_results=max_results)
            for item in search_results:
                title = item.get("title", "")
                body = item.get("body", "")
                if body:
                    snippet = f"{title}: {body}" if title else body
                    results.append(snippet)
    except Exception as exc:
        return f"Web search unavailable ({exc})."

    if not results:
        return "No live search results found."

    return "\n\n".join(results)


@tool
def search_attractions(destination: str) -> str:
    """Search the web for top attractions, landmarks and must-see places."""
    query = f"Top attractions landmarks must-see places in {destination}"
    return _web_search(query)


@tool
def search_food(destination: str) -> str:
    """Search the web for local food, restaurants and dining recommendations."""
    query = f"Best local food restaurants dining in {destination}"
    return _web_search(query)


@tool
def search_transport(destination: str) -> str:
    """Search the web for transport, getting around and travel logistics."""
    query = f"Transport getting around travel tips budget in {destination}"
    return _web_search(query)
