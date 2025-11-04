import google.generativeai as genai
from typing import List, Dict
from bs4 import BeautifulSoup
class GeminiSummarizer:
    """
    A class to summarize a list of news articles using the Google Gemini API.
    """

    def __init__(self, api_key: str):
        """
        Initializes the summarizer and configures the Gemini API.

        Args:
            api_key: The Google API key for the Gemini API.
        """
        if not api_key:
            raise ValueError("Google API key for Gemini is required.")
        
        try:
            # Configure the generative AI library with the API key
            genai.configure(api_key=api_key)
            # Initialize the specific Gemini model we want to use
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini model initialized successfully.")
        except Exception as e:
            print(f"❌ Error configuring the Gemini API: {e}")
            self.model = None

    def summarize(self, articles: List[Dict], query: str) -> str:
        """
        Generates a concise summary for a list of news articles.

        Args:
            articles: A list of article dictionaries from the NewsSearchAgent.
            query: The original search query, to provide context for the summary.

        Returns:
            A string containing the summary, or an error message if something goes wrong.
        """
        if not self.model:
            return "Summary is unavailable because the Gemini model could not be initialized."
            
        if not articles:
            return "No articles were provided to summarize."

        # Combine the title and description of each article into a single block of text.
        # We limit this to the first 20 articles to keep the prompt concise and efficient.
        articles_text = ""
        for i, article in enumerate(articles[:20]):
            title = article.get('title', 'No title')
            description = article.get('description', 'No description')
            # Ensure description is not None before processing
            if description:
                 # Clean up the description text a bit
                description_cleaned = BeautifulSoup(description, "html.parser").get_text()
                articles_text += f"Article {i+1}:\nTitle: {title}\nDescription: {description_cleaned}\n\n"

        if not articles_text.strip():
            return "Could not extract sufficient text from the articles to generate a summary."

        # Craft a clear and effective prompt for the Gemini model
        prompt = f"""
        You are an expert news analyst. Based on the following news articles about "{query}", please provide a concise, neutral, and easy-to-read summary.
        Synthesize the main points and key developments into a single, coherent paragraph. Do not list the articles or cite sources in your summary. Just provide the summary itself.

        Here are the articles to analyze:
        ---
        {articles_text}
        ---

        Summary:
        """

        try:
            print("\n🤖 Generating summary with Gemini...")
            response = self.model.generate_content(prompt)
            summary = response.text
            print("✅ Summary generated successfully.")
            return summary
        except Exception as e:
            print(f"❌ Gemini summary generation failed: {e}")
            return f"An error occurred while generating the AI summary: {str(e)}"
