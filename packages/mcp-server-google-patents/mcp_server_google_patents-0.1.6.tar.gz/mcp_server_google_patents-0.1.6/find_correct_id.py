import os
import json
from dotenv import load_dotenv
from google_patents_mcp.client import GooglePatentsClient

load_dotenv()

def find_patent():
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        print("Error: SERPAPI_API_KEY not found.")
        return

    client = GooglePatentsClient(api_key=api_key)
    query = "US12193429"
    
    print(f"Searching for {query}...")
    try:
        results = client.search(query=query)
        if "organic_results" in results:
            for result in results["organic_results"]:
                print(f"Found: {result.get('title')} - ID: {result.get('patent_id')}")
        else:
            print("No results found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_patent()
