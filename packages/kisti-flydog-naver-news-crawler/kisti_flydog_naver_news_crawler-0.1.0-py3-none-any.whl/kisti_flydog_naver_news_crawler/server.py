import requests
from bs4 import BeautifulSoup

from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server
mcp = FastMCP("kisti-flydog-naver-news-crawler")

@mcp.tool()
def get_crawling(keyword: str, numofpages: int) -> list:
    """
    Naver News titles are collected and stored in a list based on the number of news article pages related to the keywords requested by the user..
    
    Args:
        keyword (str): Keywords requested by users for Naver News search.
        numofpages (int): Number of Naver news pages to collect as requested by the user.
    
    Returns:
        list: Collected Naver News Titles.
    """
    
    base_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=' + keyword + '&start='    

    naver_crawling = []
    
    for i in range(1, numofpages * 10, 10) :
        url = base_url + str(i)

        response = requests.get(url, headers={'User-Agent':'Moailla/5.0'})

        soup = BeautifulSoup(response.text, 'html.parser')

        headlines = soup.find_all('span', {'class' : 'sds-comps-text sds-comps-text-ellipsis sds-comps-text-ellipsis-1 sds-comps-text-type-headline1'})

        for headline in headlines:
            title = headline.text
            naver_crawling.append(title)

    return naver_crawling


def main() -> None:
    # Initialize and run the server
    print("Starting Naver News Crawler server...")
    mcp.run(transport='stdio')
    

if __name__ == "__main__":
   main()     