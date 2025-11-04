"""
News Search Agent - Searches and collects news articles about specific topics
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from bs4 import BeautifulSoup
import time


class NewsSearchAgent:
    """
    An AI agent that searches the web for news articles about specific topics.
    Supports filtering by date to get fresh/recent news.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the news search agent.

        Args:
            api_key: Optional API key for NewsAPI (get from https://newsapi.org)
        """
        self.api_key = api_key
        self.news_api_url = "https://newsapi.org/v2/everything"
        self.results = []

    def search_news(self,
                   query: str,
                   days_back: int = 1,
                   language: str = "en",
                   sort_by: str = "publishedAt",
                   custom_urls: Optional[List[str]] = None) -> List[Dict]:
        """
        Search for news articles about a specific topic.

        Args:
            query: Search keyword (e.g., "Sudan")
            days_back: How many days back to search (default: 1 for today's news)
            language: Language code (default: "en" for English)
            sort_by: Sort results by "publishedAt", "relevancy", or "popularity"
            custom_urls: A list of custom URLs to scrape for news
        Returns:
            List of news articles with title, description, URL, source, and date
        """
        self.results = []

        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)

        print(f"\n🔍 Searching for news about '{query}'...")
        print(f"📅 Date range: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}\n")

        # Try NewsAPI if API key is provided
        if self.api_key:
            api_results = self._search_with_newsapi(query, from_date, to_date, language, sort_by)
            self.results.extend(api_results)
        else:
            print("⚠️  No NewsAPI key provided. Add API key for better results.")
            print("   Get free API key from: https://newsapi.org\n")
        
        # Search from custom URLs if provided
        if custom_urls:
            for url in custom_urls:
                print(f"🔍 Scraping custom URL: {url}")
                custom_results = self._search_generic_url(query, days_back, url)
                self.results.extend(custom_results)

        # Search from multiple news sources

        # Google News RSS
        google_results = self._search_google_news(query, days_back)
        self.results.extend(google_results)

        # Al Jazeera
        aljazeera_results = self._search_aljazeera(query, days_back)
        self.results.extend(aljazeera_results)

        # BBC News
        bbc_results = self._search_bbc(query, days_back)
        self.results.extend(bbc_results)

        # Reuters
        reuters_results = self._search_reuters(query, days_back)
        self.results.extend(reuters_results)

        # CNN
        cnn_results = self._search_cnn(query, days_back)
        self.results.extend(cnn_results)

        # The Guardian
        guardian_results = self._search_guardian(query, days_back)
        self.results.extend(guardian_results)

        # Remove duplicates based on title
        self.results = self._remove_duplicates(self.results)

        # Sort by date (most recent first)
        self.results.sort(key=lambda x: x.get('published_at', ''), reverse=True)

        return self.results

    def _search_generic_url(self, query: str, days_back: int, url: str) -> List[Dict]:
        """A generic scraper for a custom URL."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all('article') # Common tag for articles
                if not articles:
                    articles = soup.find_all('div', class_=lambda c: c and 'article' in c)

                results = []
                query_lower = query.lower()
                for article in articles:
                    try:
                        title_tag = article.find(['h1', 'h2', 'h3'])
                        title = title_tag.text.strip() if title_tag else 'No title'
                        
                        description_tag = article.find('p')
                        description = description_tag.text.strip() if description_tag else 'No description'
                        
                        if query_lower not in title.lower() and query_lower not in description.lower():
                            continue

                        link_tag = article.find('a')
                        article_url = link_tag['href'] if link_tag else url

                        results.append({
                            'title': title,
                            'description': description,
                            'url': article_url,
                            'source': url.split('/')[2], # Domain name as source
                            'author': 'Unknown',
                            'published_at': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'), # Default to now
                            'content': '',
                            'image_url': ''
                        })
                    except:
                        continue
                return results
            return []
        except Exception as e:
            print(f"⚠️  Failed to scrape {url}: {str(e)}")
            return []


    def _search_with_newsapi(self,
                            query: str,
                            from_date: datetime,
                            to_date: datetime,
                            language: str,
                            sort_by: str) -> List[Dict]:
        """Search using NewsAPI."""
        try:
            params = {
                'q': query,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'language': language,
                'sortBy': sort_by,
                'apiKey': self.api_key,
                'pageSize': 100
            }

            response = requests.get(self.news_api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])

                return [
                    {
                        'title': article.get('title', 'No title'),
                        'description': article.get('description', 'No description'),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'author': article.get('author', 'Unknown'),
                        'published_at': article.get('publishedAt', ''),
                        'content': article.get('content', ''),
                        'image_url': article.get('urlToImage', '')
                    }
                    for article in articles
                ]
            else:
                print(f"⚠️  NewsAPI returned status code: {response.status_code}")
                if response.status_code == 401:
                    print("   Invalid API key. Check your NewsAPI key.")
                elif response.status_code == 426:
                    print("   API key upgrade required or rate limit exceeded.")
                return []

        except Exception as e:
            print(f"⚠️  NewsAPI search failed: {str(e)}")
            return []

    def _search_google_news(self, query: str, days_back: int) -> List[Dict]:
        """Search using Google News RSS feed."""
        try:
            url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')

                results = []
                for item in items:
                    try:
                        pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                        if pub_date:
                            article_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                            cutoff_date = datetime.now() - timedelta(days=days_back)
                            if article_date < cutoff_date:
                                continue

                        results.append({
                            'title': item.find('title').text if item.find('title') else 'No title',
                            'description': item.find('description').text if item.find('description') else 'No description',
                            'url': item.find('link').text if item.find('link') else '',
                            'source': item.find('source').text if item.find('source') else 'Google News',
                            'author': 'Unknown',
                            'published_at': pub_date,
                            'content': '',
                            'image_url': ''
                        })
                    except:
                        continue
                return results
            return []
        except Exception as e:
            print(f"⚠️  Google News failed: {str(e)}")
            return []

    def _search_aljazeera(self, query: str, days_back: int) -> List[Dict]:
        """Search Al Jazeera RSS feed."""
        try:
            url = f"https://www.aljazeera.com/xml/rss/all.xml"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')

                results = []
                query_lower = query.lower()
                for item in items:
                    try:
                        title = item.find('title').text if item.find('title') else ''
                        description = item.find('description').text if item.find('description') else ''

                        # Filter by query
                        if query_lower not in title.lower() and query_lower not in description.lower():
                            continue

                        pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                        if pub_date:
                            article_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                            cutoff_date = datetime.now() - timedelta(days=days_back)
                            if article_date < cutoff_date:
                                continue

                        results.append({
                            'title': title,
                            'description': description,
                            'url': item.find('link').text if item.find('link') else '',
                            'source': 'Al Jazeera',
                            'author': 'Al Jazeera',
                            'published_at': pub_date,
                            'content': '',
                            'image_url': ''
                        })
                    except:
                        continue

                return results
            return []
        except Exception as e:
            print(f"⚠️  Al Jazeera failed: {str(e)}")
            return []

    def _search_bbc(self, query: str, days_back: int) -> List[Dict]:
        """Search BBC News RSS feed."""
        try:
            url = "http://feeds.bbci.co.uk/news/world/rss.xml"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')

                results = []
                query_lower = query.lower()
                for item in items:
                    try:
                        title = item.find('title').text if item.find('title') else ''
                        description = item.find('description').text if item.find('description') else ''

                        # Filter by query
                        if query_lower not in title.lower() and query_lower not in description.lower():
                            continue

                        pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                        if pub_date:
                            article_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                            cutoff_date = datetime.now() - timedelta(days=days_back)
                            if article_date < cutoff_date:
                                continue

                        results.append({
                            'title': title,
                            'description': description,
                            'url': item.find('link').text if item.find('link') else '',
                            'source': 'BBC News',
                            'author': 'BBC',
                            'published_at': pub_date,
                            'content': '',
                            'image_url': ''
                        })
                    except:
                        continue

                return results
            return []
        except Exception as e:
            print(f"⚠️  BBC News failed: {str(e)}")
            return []

    def _search_reuters(self, query: str, days_back: int) -> List[Dict]:
        """Search Reuters RSS feed."""
        try:
            url = "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')

                results = []
                query_lower = query.lower()
                for item in items:
                    try:
                        title = item.find('title').text if item.find('title') else ''
                        description = item.find('description').text if item.find('description') else ''

                        # Filter by query
                        if query_lower not in title.lower() and query_lower not in description.lower():
                            continue

                        pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                        if pub_date:
                            article_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                            cutoff_date = datetime.now() - timedelta(days=days_back)
                            if article_date < cutoff_date:
                                continue

                        results.append({
                            'title': title,
                            'description': description,
                            'url': item.find('link').text if item.find('link') else '',
                            'source': 'Reuters',
                            'author': 'Reuters',
                            'published_at': pub_date,
                            'content': '',
                            'image_url': ''
                        })
                    except:
                        continue

                return results
            return []
        except Exception as e:
            print(f"⚠️  Reuters failed: {str(e)}")
            return []

    def _search_cnn(self, query: str, days_back: int) -> List[Dict]:
        """Search CNN RSS feed."""
        try:
            url = "http://rss.cnn.com/rss/edition_world.rss"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')

                results = []
                query_lower = query.lower()
                for item in items:
                    try:
                        title = item.find('title').text if item.find('title') else ''
                        description = item.find('description').text if item.find('description') else ''

                        # Filter by query
                        if query_lower not in title.lower() and query_lower not in description.lower():
                            continue

                        pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                        if pub_date:
                            article_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                            cutoff_date = datetime.now() - timedelta(days=days_back)
                            if article_date < cutoff_date:
                                continue

                        results.append({
                            'title': title,
                            'description': description,
                            'url': item.find('link').text if item.find('link') else '',
                            'source': 'CNN',
                            'author': 'CNN',
                            'published_at': pub_date,
                            'content': '',
                            'image_url': ''
                        })
                    except:
                        continue

                return results
            return []
        except Exception as e:
            print(f"⚠️  CNN failed: {str(e)}")
            return []

    def _search_guardian(self, query: str, days_back: int) -> List[Dict]:
        """Search The Guardian RSS feed."""
        try:
            url = "https://www.theguardian.com/world/rss"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')

                results = []
                query_lower = query.lower()
                for item in items:
                    try:
                        title = item.find('title').text if item.find('title') else ''
                        description = item.find('description').text if item.find('description') else ''

                        # Filter by query
                        if query_lower not in title.lower() and query_lower not in description.lower():
                            continue

                        pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                        if pub_date:
                            article_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                            cutoff_date = datetime.now() - timedelta(days=days_back)
                            if article_date < cutoff_date:
                                continue

                        results.append({
                            'title': title,
                            'description': description,
                            'url': item.find('link').text if item.find('link') else '',
                            'source': 'The Guardian',
                            'author': 'The Guardian',
                            'published_at': pub_date,
                            'content': '',
                            'image_url': ''
                        })
                    except:
                        continue

                return results
            return []
        except Exception as e:
            print(f"⚠️  The Guardian failed: {str(e)}")
            return []

    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity."""
        seen_titles = set()
        unique_articles = []

        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)

        return unique_articles

    def display_results(self, max_results: Optional[int] = None):
        """
        Display search results in a formatted way.

        Args:
            max_results: Maximum number of results to display (None for all)
        """
        if not self.results:
            print("❌ No results found.")
            return

        results_to_show = self.results[:max_results] if max_results else self.results

        print(f"\n{'='*80}")
        print(f"📰 FOUND {len(self.results)} NEWS ARTICLES")
        print(f"{'='*80}\n")

        for idx, article in enumerate(results_to_show, 1):
            print(f"\n[{idx}] {article['title']}")
            print(f"    📍 Source: {article['source']}")
            print(f"    👤 Author: {article['author']}")
            print(f"    📅 Published: {article['published_at']}")
            print(f"    🔗 URL: {article['url']}")
            if article['description']:
                desc = article['description'][:200] + "..." if len(article['description']) > 200 else article['description']
                print(f"    📝 {desc}")
            print(f"    {'-'*76}")

        if max_results and len(self.results) > max_results:
            print(f"\n... and {len(self.results) - max_results} more articles")

    def save_to_json(self, filename: str = "news_results.json"):
        """
        Save search results to a JSON file.

        Args:
            filename: Output filename (default: "news_results.json")
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_results': len(self.results),
                    'timestamp': datetime.now().isoformat(),
                    'articles': self.results
                }, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")

    def save_to_text(self, filename: str = "news_results.txt"):
        """
        Save search results to a text file.

        Args:
            filename: Output filename (default: "news_results.txt")
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"NEWS SEARCH RESULTS\n")
                f.write(f"{'='*80}\n")
                f.write(f"Total Results: {len(self.results)}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")

                for idx, article in enumerate(self.results, 1):
                    f.write(f"\n[{idx}] {article['title']}\n")
                    f.write(f"Source: {article['source']}\n")
                    f.write(f"Author: {article['author']}\n")
                    f.write(f"Published: {article['published_at']}\n")
                    f.write(f"URL: {article['url']}\n")
                    f.write(f"Description: {article['description']}\n")
                    f.write(f"{'-'*80}\n")

            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Create agent (add your NewsAPI key for better results)
    # Get free API key from: https://newsapi.org
    agent = NewsSearchAgent(api_key=None)  # Replace None with your API key

    # Search for today's news about Sudan
    print("Example: Searching for today's news about Sudan...")
    results = agent.search_news(
        query="Sudan",
        days_back=1,  # Today's news (last 24 hours)
        language="en",
        sort_by="publishedAt"
    )

    # Display results (show first 10)
    agent.display_results(max_results=10)

    # Save results
    agent.save_to_json("sudan_news.json")
    agent.save_to_text("sudan_news.txt")
