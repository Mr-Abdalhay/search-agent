"""
Example usage script for News Search Agent
Run this to see the agent in action!
"""

from news_search_agent import NewsSearchAgent


def example_1_basic_search():
    """Example 1: Basic search for today's news"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Search - Today's News About Sudan")
    print("="*80)

    agent = NewsSearchAgent()
    results = agent.search_news("Sudan", days_back=1)
    agent.display_results(max_results=5)


def example_2_with_api_key():
    """Example 2: Search with NewsAPI key (better results)"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Using NewsAPI Key")
    print("="*80)

    # Replace 'YOUR_API_KEY' with your actual NewsAPI key
    # Get one free at: https://newsapi.org
    api_key = None  # Change to your API key

    if api_key:
        agent = NewsSearchAgent(api_key=api_key)
        results = agent.search_news(
            query="Sudan",
            days_back=7,
            language="en",
            sort_by="publishedAt"
        )
        agent.display_results(max_results=10)
        agent.save_to_json("sudan_news_7days.json")
    else:
        print("⚠️  Set your API key in this script to run this example")
        print("   Get free key from: https://newsapi.org")


def example_3_multiple_topics():
    """Example 3: Search multiple topics"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Searching Multiple Topics")
    print("="*80)

    topics = ["Sudan", "Egypt", "Ethiopia"]
    agent = NewsSearchAgent()

    for topic in topics:
        print(f"\n--- Searching: {topic} ---")
        results = agent.search_news(topic, days_back=1)
        print(f"Found {len(results)} articles about {topic}")

        # Save each to separate file
        agent.save_to_json(f"{topic.lower()}_news.json")


def example_4_interactive():
    """Example 4: Interactive search"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Interactive Search")
    print("="*80)

    topic = input("\nWhat topic do you want to search for? (e.g., Sudan): ").strip()
    if not topic:
        topic = "Sudan"  # Default

    try:
        days = int(input("How many days back? (1 for today, 7 for last week): ").strip())
    except:
        days = 1  # Default

    print(f"\nSearching for '{topic}' from the last {days} day(s)...")

    agent = NewsSearchAgent()
    results = agent.search_news(topic, days_back=days)

    if results:
        agent.display_results(max_results=15)

        # Ask if user wants to save
        save = input("\nDo you want to save results? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"{topic.lower().replace(' ', '_')}_news.json"
            agent.save_to_json(filename)
            agent.save_to_text(filename.replace('.json', '.txt'))
    else:
        print("\nNo results found. Try a different topic or increase the date range.")


def example_5_custom_filtering():
    """Example 5: Custom filtering and sorting"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Custom Filtering")
    print("="*80)

    agent = NewsSearchAgent()

    # Search for news
    results = agent.search_news("Sudan", days_back=3)

    # Custom filter: Only show articles with specific keywords in description
    keywords = ["conflict", "peace", "government", "humanitarian"]

    filtered_results = [
        article for article in results
        if any(keyword.lower() in article.get('description', '').lower()
               for keyword in keywords)
    ]

    print(f"\nFound {len(results)} total articles")
    print(f"Filtered to {len(filtered_results)} articles containing keywords: {', '.join(keywords)}")

    # Display filtered results
    if filtered_results:
        print("\nFiltered Results:")
        for idx, article in enumerate(filtered_results[:5], 1):
            print(f"\n[{idx}] {article['title']}")
            print(f"    Source: {article['source']}")
            print(f"    Description: {article['description'][:150]}...")


def main():
    """Main menu to run examples"""
    while True:
        print("\n" + "="*80)
        print("NEWS SEARCH AGENT - Examples Menu")
        print("="*80)
        print("\n1. Basic Search (Today's news about Sudan)")
        print("2. Search with NewsAPI Key (7 days)")
        print("3. Search Multiple Topics")
        print("4. Interactive Search (You choose the topic)")
        print("5. Custom Filtering Example")
        print("0. Exit")

        choice = input("\nSelect an example (0-5): ").strip()

        if choice == "1":
            example_1_basic_search()
        elif choice == "2":
            example_2_with_api_key()
        elif choice == "3":
            example_3_multiple_topics()
        elif choice == "4":
            example_4_interactive()
        elif choice == "5":
            example_5_custom_filtering()
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please select 0-5.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    # Run the main menu
    main()

    # Or uncomment below to run a specific example directly:
    # example_1_basic_search()
    # example_4_interactive()
