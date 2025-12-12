import os
import json
from dotenv import load_dotenv
from google_patents_mcp.client import GooglePatentsClient

# Load environment variables
load_dotenv()

def test_details():
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        print("Error: SERPAPI_API_KEY not found in environment or .env file.")
        print("Please add SERPAPI_API_KEY=your_key_here to .env")
        return

    client = GooglePatentsClient(api_key=api_key)
    patent_ids_to_try = [
        "US11734097B1",
        "patent/US11734097B1/en",
        "patent/US11734097B1"
    ]
    
    for pid in patent_ids_to_try:
        print(f"\nTesting with patent_id: {pid}")
        try:
            results = client.get_details(patent_id=pid)
            if "error" in results:
                print(f"Error: {results['error']}")
            else:
                print("Success!")
                print("Keys:", list(results.keys()))
                return
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_details()
