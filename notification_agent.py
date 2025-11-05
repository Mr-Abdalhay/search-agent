# notification_agent.py
# Handles scheduling and delivery of notifications for new news

import threading
import time
from news_search_agent import NewsSearchAgent
import config

class NotificationAgent:
    def __init__(self):
        self.scheduled_searches = []  # List of dicts: {query, days_back, custom_urls, last_results}

    def schedule_search(self, query, days_back, custom_urls, interval_minutes=60):
        agent = NewsSearchAgent(api_key=config.NEWSAPI_KEY)
        initial_results = agent.search_news(query, days_back=days_back, custom_urls=custom_urls)
        self.scheduled_searches.append({
            'query': query,
            'days_back': days_back,
            'custom_urls': custom_urls,
            'last_results': initial_results,
            'interval_minutes': interval_minutes
        })
        threading.Thread(target=self._delayed_search, args=(len(self.scheduled_searches)-1,), daemon=True).start()

    def _delayed_search(self, idx):
        search_info = self.scheduled_searches[idx]
        time.sleep(search_info['interval_minutes'] * 60)  # Convert minutes to seconds
        search_info = self.scheduled_searches[idx]
        agent = NewsSearchAgent(api_key=config.NEWSAPI_KEY)
        new_results = agent.search_news(search_info['query'], days_back=search_info['days_back'], custom_urls=search_info['custom_urls'])
        old_urls = set(a['url'] for a in search_info['last_results'])
        new_news = [a for a in new_results if a['url'] not in old_urls]
        if new_news:
            self.notify_browser(search_info['query'], new_news)

    def notify_browser(self, query, new_news):
        # In a real app, this would trigger a browser notification via websocket or polling
        # For now, just print to server log
        print(f"🔔 New news found for '{query}': {len(new_news)} articles.")
