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
import config

app = Flask(__name__)

# Instantiate the NewsSearchAgent with your NewsAPI key
agent = NewsSearchAgent(api_key=config.NEWSAPI_KEY)

# 2. Instantiate the GeminiSummarizer with your Gemini API key
summarizer = GeminiSummarizer(api_key=config.GEMINI_API_KEY)

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
    
    # Get the search results from the news agent
    results = agent.search_news(
        query=query, 
        days_back=days_back,
        language='ar',
        custom_urls=custom_urls if custom_urls else None
    )
    
    # Generate a summary using the results
    summary = "" # Initialize summary as an empty string
    if results: # Only generate a summary if there are results
        summary = summarizer.summarize(results, query)
    
    # Pass the results and the summary to the template
    return render_template('results.html', 
                         results=results, 
                         query=query, 
                         summary=summary, 
                         custom_urls=custom_urls)
    
if __name__ == "__main__":
    app.run(debug=True)