# server.py


from mcp.server.fastmcp import FastMCP
import worldnewsapi
import os
from dotenv import load_dotenv
# Create an MCP server
mcp = FastMCP("Demo")

# Load environment variables from .env file
load_dotenv()

# Get the weather API key from environment variables
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Initial SDK configuration
newsapi_configuration = worldnewsapi.Configuration(api_key={'apiKey': WEATHER_API_KEY})


@mcp.tool()
def fetch_news_articles(
    query_text='politics',
    earliest_date='2025-04-17',
    latest_date='2025-04-23',
    max_results=5
)->dict:
    """
    Fetches news articles from the WorldNewsAPI based on specified parameters
    and returns them as a list of dictionaries.
    
    Args:
        query_text (str): The text to search for in news articles
        earliest_date (str): Earliest publication date in YYYY-MM-DD format
        latest_date (str): Latest publication date in YYYY-MM-DD format
        max_results (int): Maximum number of results to return
        
    Returns:
        list: A list of dictionaries containing article details
    """
    try:
        newsapi_instance = worldnewsapi.NewsApi(worldnewsapi.ApiClient(newsapi_configuration))
        
        offset = 0
        all_results = []
        max_results = int(max_results)  # Ensure max_results is an integer
        
        while len(all_results) < max_results:
            request_count = min(100, max_results - len(all_results))  # request 100 or the remaining number of articles
            
            response = newsapi_instance.search_news(
                text=query_text,
                earliest_publish_date=earliest_date,
                latest_publish_date=latest_date,
                sort="publish-time",
                sort_direction="desc",
                # min_sentiment=-0.8,  # Ensuring this is a float
                # max_sentiment=0.8,   # Ensuring this is a float
                offset=offset,
                number=request_count)
            
            #print(f"Retrieved {len(response.news)} articles. Offset: {offset}/{max_results}. "
                #   f"Total available: {response.available}.")
            
            if len(response.news) == 0:
                break
            
            all_results.extend(response.news)
            offset += 100
        
        # Convert API response objects to dictionaries
        articles_list = []
        for article in all_results[:max_results]:  # Use max_results here
            article_dict = {
                "title": article.title,
                "author": article.authors,
                "url": article.url,
                "text_preview": article.text[:80] + "..." if article.text else "",
                "full_text": article.text,
                "publish_date": article.publish_date,
            }
            articles_list.append(article_dict)
        
        return {"all_data" : articles_list}
        
    except worldnewsapi.ApiException as e:
        #print(f"Exception when calling NewsApi->search_news: {e}")
        return {"error": str(e)}
    
    

# Example usage:
# articles = fetch_news_articles()
# for article in articles:
#     print(f"\nTitle: {article['title']}")
#     print(f"Author: {article['author']}")
#     print(f"URL: {article['url']}")
#     print(f"Sentiment: {article['sentiment']}")
#     print(f"Text: {article['text_preview']}")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def get_weather(city:str) -> int:
    """it gets and retuns the weather of the city"""
    return 45


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


mcp.run(transport="stdio")