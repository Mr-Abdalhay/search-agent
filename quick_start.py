"""
Quick Start Script - News Search Agent
Run this file to immediately search for news!
"""

from news_search_agent import NewsSearchAgent
import config


def main():
    print("\n" + "="*80)
    print("NEWS SEARCH AGENT - Quick Start")
    print("="*80)

    # Use API key from config if available
    api_key = config.NEWSAPI_KEY if hasattr(config, 'NEWSAPI_KEY') and config.NEWSAPI_KEY != "YOUR_API_KEY_HERE" else None

    # Create agent
    agent = NewsSearchAgent(api_key=api_key)

    # Get user input
    print("\nWhat would you like to search for?")
    topic = input("Enter topic (default: Sudan): ").strip()
    if not topic:
        topic = "Sudan"

    print("\nHow many days back?")
    print("  1 = Today's news only")
    print("  7 = Last week")
    print("  30 = Last month")
    days_input = input("Enter days (default: 1): ").strip()

    try:
        days = int(days_input) if days_input else 1
    except:
        days = 1

    # Search
    print(f"\n🔍 Searching for news about '{topic}' from the last {days} day(s)...")
    print("Please wait...\n")

    results = agent.search_news(
        query=topic,
        days_back=days,
        language="en",
        sort_by="publishedAt"
    )

    # Display results
    if results:
        print(f"\n✅ SUCCESS! Found {len(results)} articles")

        # Show results
        show_count = min(20, len(results))
        agent.display_results(max_results=show_count)

        # Save results
        print("\n" + "="*80)
        save_option = input("\nSave results? (y/n): ").strip().lower()

        if save_option == 'y':
            json_file = f"{topic.lower().replace(' ', '_')}_news.json"
            txt_file = f"{topic.lower().replace(' ', '_')}_news.txt"

            agent.save_to_json(json_file)
            agent.save_to_text(txt_file)

            print(f"\n✅ Files saved:")
            print(f"   - {json_file}")
            print(f"   - {txt_file}")
    else:
        print("\n❌ No results found.")
        print("Try:")
        print("  - Different search term")
        print("  - Increase days_back parameter")
        print("  - Check your internet connection")

    print("\n" + "="*80)
    print("Done! Thank you for using News Search Agent")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
