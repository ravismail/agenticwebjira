from bs4 import BeautifulSoup
import requests
from googlesearch import search
import re
import json
from logger import get_logger

logger = get_logger("ScraperAgent")

class ScraperAgent:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search_google(self, query, num_results=3):
        """Searches Google and returns a list of URLs."""
        logger.info(f"Searching Google for: {query}")
        urls = []
        try:
            for url in search(query, num_results=num_results):
                urls.append(url)
        except Exception as e:
            logger.error(f"Error searching google: {e}")
        return urls

    def scrape_url(self, url, username=None, token=None):
        """Scrapes a specific URL and returns the text content. Handles Confluence pages via API."""
        logger.info(f"Scraping URL: {url}")
        
        # Check for Confluence URL
        confluence_match = re.search(r'/wiki/.*pages/(\d+)', url)
        if confluence_match and username and token:
            page_id = confluence_match.group(1)
            # Construct API URL (assuming cloud domain)
            # Extract base url
            base_url_match = re.search(r'(https://[^/]+)', url)
            if base_url_match:
                base_url = base_url_match.group(1)
                api_url = f"{base_url}/wiki/rest/api/content/{page_id}?expand=body.storage"
                print(f"Detected Confluence Page {page_id}. Using API: {api_url}")
                try:
                    response = requests.get(api_url, auth=(username, token), timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        html_content = data.get('body', {}).get('storage', {}).get('value', '')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        return soup.get_text(separator='\n')
                    else:
                        print(f"Confluence API failed: {response.status_code} - {response.text}")
                        # Fallback to standard scrape (likely fail but worth a shot?)
                        # standard scrape might fail on auth, let's try auth there too
                        pass 
                except Exception as e:
                    print(f"Confluence API error: {e}")

        # Standard Scrape
        try:
            auth = (username, token) if username and token else None
            # Only use auth if it looks like the same domain or explicitly requested? 
            # For now, simplistic approach: if we have auth and it's not a generic google search result, maybe use it?
            # Actually, passing auth to random sites is bad. 
            # Only pass auth if it matches the jira domain.
            
            use_auth = None
            if username and token and "atlassian.net" in url:
                use_auth = auth

            response = requests.get(url, headers=self.headers, auth=use_auth, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find common content areas of 'minutes' or 'confluence'
                # Generic fallback: get all paragraphs
                # A more robust scraper would use specialized extractors (e.g. newspaper3k or readability)
                # but bs4 is fine for this task.
                
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.decompose()
                    
                text = soup.get_text(separator='\n')
                
                # Cleanup whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text[:10000] # Limit content size for LLM context
            else:
                print(f"Failed to fetch {url}, status: {response.status_code}")
                return ""
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return ""

if __name__ == "__main__":
    scraper = ScraperAgent()
    # Test
    # print(scraper.search_google("project meeting minutes sample"))
