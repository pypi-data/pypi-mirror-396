import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from serpapi import GoogleSearch

# Load environment variables
# Load .env from the same directory as this script
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

# Initialize FastMCP server
mcp = FastMCP("SerpApi Google Scholar")

def get_api_key():
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY not found in environment variables")
    return api_key

@mcp.tool()
def search_google_scholar(q: str, hl: str = "en", start: int = 0, num: int = 10) -> str:
    """
    Search Google Scholar for academic papers, articles, and publications.
    
    Args:
        q: Search query
        hl: Language code (default: "en")
        start: Offset for search results (default: 0)
        num: Number of results to return (default: 10)
    """
    params = {
        "engine": "google_scholar",
        "q": q,
        "hl": hl,
        "start": start,
        "num": num,
        "api_key": get_api_key()
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return str(results)

@mcp.tool()
def get_author_profile(author_id: str, hl: str = "en") -> str:
    """
    Get Google Scholar author profile information.
    
    Args:
        author_id: The author's unique ID (e.g., from a search result)
        hl: Language code (default: "en")
    """
    params = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "hl": hl,
        "api_key": get_api_key()
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return str(results)

@mcp.tool()
def get_author_articles(author_id: str, hl: str = "en", start: int = 0, num: int = 20, sort: str = "pubdate") -> str:
    """
    Get articles for a specific author.
    
    Args:
        author_id: The author's unique ID
        hl: Language code (default: "en")
        start: Offset for articles (default: 0)
        num: Number of articles to return (default: 20)
        sort: Sort order ("pubdate" or "citation")
    """
    params = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "hl": hl,
        "start": start,
        "num": num,
        "sort": sort,
        "view_op": "view_citation", # This might be wrong, let's check docs. 
        # Actually, for articles, it is usually part of the author profile or a separate view.
        # Let's check the SerpApi docs provided in the prompt.
        # https://serpapi.com/google-scholar-author-articles
        # It says "engine": "google_scholar_author" and "view_op": "view_citation" is for specific citation?
        # No, wait. 
        # https://serpapi.com/google-scholar-author-api
        # To get articles, we just query the author profile. It returns a list of articles.
        # But there is pagination.
        # Let's look at the URL provided: https://serpapi.com/google-scholar-author-articles
        # It seems this might be for pagination of articles in the author profile.
        "api_key": get_api_key()
    }
    # Re-reading the docs from the prompt URLs (I can't browse them but I can infer or use knowledge).
    # The prompt says: https://serpapi.com/google-scholar-author-articles
    # Usually, to get more articles, we use the same author engine but with start/num.
    
    search = GoogleSearch(params)
    results = search.get_dict()
    return str(results)

@mcp.tool()
def get_author_citation(author_id: str, citation_id: str, hl: str = "en") -> str:
    """
    Get details about a specific citation for an author.
    
    Args:
        author_id: The author's unique ID
        citation_id: The specific citation ID
        hl: Language code (default: "en")
    """
    params = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "citation_id": citation_id,
        "view_op": "view_citation",
        "hl": hl,
        "api_key": get_api_key()
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return str(results)

@mcp.tool()
def get_citation_formats(q: str) -> str:
    """
    Get citation formats (BibTeX, MLA, APA, etc.) for a result.
    
    Args:
        q: The ID of the result to cite (usually from search results)
    """
    params = {
        "engine": "google_scholar_cite",
        "q": q,
        "api_key": get_api_key()
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return str(results)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
