"""
Quick test of Google Custom Search API
"""
import httpx
import json
from app.core.config import settings

# Your credentials
API_KEY = settings.GOOGLE_API_KEY
CSE_ID = settings.GOOGLE_CSE_ID

def test_google_cse():
    """Test Google Custom Search API"""
    print("🔍 Testing Google Custom Search API\n")
    print("=" * 60)

    # Test query
    query = "brake pads Honda Civic Singapore"

    print(f"\nQuery: '{query}'")
    print("Searching Lazada.sg, Shopee.sg, Carousell.sg, Amazon.sg...")

    # Make API request
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "num": 5,
        "gl": "sg",  # Singapore
        "lr": "lang_en"
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Check if we got results
            if "items" in data:
                results = data["items"]
                print(f"\n✅ Success! Found {len(results)} results\n")

                for i, result in enumerate(results, 1):
                    title = result.get("title", "")
                    link = result.get("link", "")
                    snippet = result.get("snippet", "")

                    # Detect source
                    source = "Unknown"
                    if "lazada.sg" in link:
                        source = "Lazada"
                    elif "shopee.sg" in link:
                        source = "Shopee"
                    elif "carousell.sg" in link:
                        source = "Carousell"
                    elif "amazon.sg" in link:
                        source = "Amazon"

                    print(f"{i}. [{source}] {title[:60]}...")
                    print(f"   {link[:80]}")
                    print(f"   {snippet[:100]}...")
                    print()

                # Check search info
                search_info = data.get("searchInformation", {})
                total_results = search_info.get("totalResults", "Unknown")
                search_time = search_info.get("searchTime", "Unknown")

                print("=" * 60)
                print(f"📊 Search Stats:")
                print(f"   Total results available: {total_results}")
                print(f"   Search time: {search_time}s")

                # Check quota
                print(f"\n💰 Quota Usage:")
                print(f"   Free tier: 100 searches/day")
                print(f"   This search used: 1 query")
                print(f"   Remaining today: ~99 queries")

                print("\n✅ Google Custom Search is working!")
                print("🎉 Your hybrid system can now search real marketplaces!")

            else:
                print("\n⚠️  No results found")
                print("This might be because:")
                print("  1. No matching products on the configured sites")
                print("  2. CSE needs time to index the sites")
                print("  3. Sites aren't configured correctly")

                if "error" in data:
                    error = data["error"]
                    print(f"\n❌ API Error: {error.get('message', 'Unknown error')}")

    except httpx.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        print("\nPossible issues:")
        print("  1. API key is invalid")
        print("  2. CSE ID is incorrect")
        print("  3. API quota exceeded")
        print("  4. Network connection issue")

    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_google_cse()
