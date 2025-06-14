import sys
sys.path.append('.')
from src.auth import MidwayAuth
from src.mercury_scraper import MercuryScraper

# Initialize and test
scraper = MercuryScraper(
    mercury_url="https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na",
    valid_locations=['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10'],
    valid_statuses=['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION']
)

# Get the raw response
auth = MidwayAuth()
session = auth.get_authenticated_session()
if session:
    response = session.get(scraper.mercury_url)
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    print(f"First 500 chars of response:")
    print(response.text[:500])
    
    # Save full response for analysis
    with open('mercury_response.html', 'w') as f:
        f.write(response.text)
    print("\nFull response saved to mercury_response.html")
