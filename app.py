# from flask import Flask, render_template, request
# from news_search_agent import NewsSearchAgent
# import config

# app = Flask(__name__)

# # Instantiate the NewsSearchAgent with your API key
# agent = NewsSearchAgent(api_key=config.NEWSAPI_KEY)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/search', methods=['POST'])
# def search():
#     query = request.form['query']
#     days_back = int(request.form['days_back'])
    
#     results = agent.search_news(query, days_back=days_back)
    
#     return render_template('results.html', results=results, query=query)

# if __name__ == "__main__":
#     app.run(debug=True)
from flask import Flask, render_template, request
from news_search_agent import NewsSearchAgent
from gemini_summarizer import GeminiSummarizer # 1. Import the new class
from notification_agent import NotificationAgent
import config

app = Flask(__name__)

# Instantiate the NewsSearchAgent with your NewsAPI key
agent = NewsSearchAgent(api_key=config.NEWSAPI_KEY)

# Instantiate the GeminiSummarizer with your Gemini API key
summarizer = GeminiSummarizer(api_key=config.GEMINI_API_KEY)

# Instantiate the NotificationAgent
notification_agent = NotificationAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    days_back = int(request.form['days_back'])
    
    # Get custom URLs from the form
    custom_urls = request.form.getlist('custom_urls[]')
    # Filter out empty URLs
    custom_urls = [url for url in custom_urls if url.strip()]

    # Check if user opted in for notification
    notify_new_news = request.form.get('notify_new_news') == '1'
    
    # Get the search results from the news agent
    results = agent.search_news(
        query=query,
        days_back=days_back,
        language='ar',
        custom_urls=custom_urls if custom_urls else None
    )

    # If notification is requested, schedule a re-search with custom interval
    if notify_new_news:
        interval_minutes = int(request.form.get('notification_interval', 60))  # Default to 60 minutes if not specified
        notification_agent.schedule_search(query, days_back, custom_urls if custom_urls else None, interval_minutes=interval_minutes)

    # Generate a summary using the results
    summary = "" # Initialize summary as an empty string
    if results: # Only generate a summary if there are results
        summary = summarizer.summarize(results, query)

    # Pass the results and the summary to the template
    return render_template('results.html',
                         results=results,
                         query=query,
                         summary=summary,
                         custom_urls=custom_urls,
                         notify_new_news=notify_new_news)
    
if __name__ == "__main__":
    app.run(debug=True)
