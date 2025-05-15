import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Tuple
import time
import random
import json
import string
from fake_useragent import UserAgent
from urllib.parse import urlparse

# Try to load fake_useragent, fall back to our list if not available
try:
    ua = UserAgent()
    def get_random_user_agent():
        return ua.random
except Exception:
    # List of common user agents to rotate
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    ]
    
    def get_random_user_agent():
        return random.choice(USER_AGENTS)

# List of free proxies - ideally you would use a paid proxy service
# These are just placeholders and likely won't work
FREE_PROXIES = [
    # Format: "protocol://user:pass@ip:port" or "protocol://ip:port"
]

# Use a proxy rotation service instead (these are examples, you'll need your own API keys)
PROXY_SERVICES = {
    # "brightdata": {
    #     "url": "http://brd.superproxy.io:22225",
    #     "username": "your_username",
    #     "password": "your_password",
    # },
    # "smartproxy": {
    #     "url": "http://gate.smartproxy.com:7000",
    #     "username": "your_username",
    #     "password": "your_password",
    # },
}

# Updated URLs for Czech startup information
# These have been manually verified to be accessible
CZECH_STARTUP_SOURCES = [
    # Primary sources - major startup data sites
    "https://cc.cz/cc25/",
    "https://wellfound.com/startups/location/czech-republic",
    "https://www.czechstartups.org/en/startup-ecosystem/start-ups/",
    
    # Secondary sources - articles about Czech startups
    "https://www.seedtable.com/best-startups-in-prague",
    "https://www.startupblink.com/startup-ecosystem/czechia?page=1",
    
]

# Backup sources if we can't access the primary ones
FALLBACK_SEARCH_QUERIES = [
    "how many startups in Czech Republic statistics",
    "Czech Republic startup ecosystem report",
    "Prague startup scene statistics",
    "Czech tech startups data 2023"
]

# Request delays to avoid triggering anti-scraping
MIN_REQUEST_DELAY = 3.0  # Minimum seconds between requests
MAX_REQUEST_DELAY = 7.0  # Maximum seconds between requests
JITTER_FACTOR = 0.2      # Random jitter to add to delays

# IP rotation settings
MAX_REQUESTS_PER_IP = 5  # Max requests before rotating IP

# Track requests per IP
request_count = 0

def get_random_proxy():
    """Return a random proxy from our list or proxy service."""
    if FREE_PROXIES:
        return random.choice(FREE_PROXIES)
    
    if PROXY_SERVICES:
        service = random.choice(list(PROXY_SERVICES.keys()))
        service_config = PROXY_SERVICES[service]
        return f"{service_config['url']}"
        
    return None

def wait_between_requests():
    """Wait a random amount of time between requests to avoid detection."""
    delay = random.uniform(MIN_REQUEST_DELAY, MAX_REQUEST_DELAY)
    jitter = random.uniform(-JITTER_FACTOR * delay, JITTER_FACTOR * delay)
    total_delay = delay + jitter
    print(f"Waiting {total_delay:.2f} seconds between requests...")
    time.sleep(total_delay)

def generate_random_client():
    """Generate random client information to mimic real browser behavior."""
    # Random screen resolution
    width = random.choice([1366, 1440, 1536, 1920, 2560])
    height = random.choice([768, 900, 864, 1080, 1440])
    
    # Random platform
    platform = random.choice(['Win32', 'MacIntel', 'Linux x86_64'])
    
    # Random color depth
    color_depth = random.choice([24, 30, 48])
    
    return {
        'screenWidth': width,
        'screenHeight': height,
        'colorDepth': color_depth,
        'platform': platform,
        'doNotTrack': random.choice(['1', None]),
        'webdriver': 'false',
        'language': random.choice(['en-US', 'en-GB', 'en']),
    }

def get_browser_headers(url=None) -> Dict[str, str]:
    """Generate headers that mimic a real browser."""
    parsed_url = urlparse(url) if url else None
    domain = parsed_url.netloc if parsed_url else None
    
    # Generate random cookies and tokens
    cookie_values = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'TE': 'trailers',
    }
    
    # Add domain-specific cookies to bypass some protections
    if domain:
        headers['Host'] = domain
        if 'startupblink.com' in domain:
            headers['Cookie'] = f'session_id={cookie_values}; has_js=1; visited=1'
        elif 'crunchbase.com' in domain:
            headers['Cookie'] = f'caid={cookie_values}; xsrf_token={cookie_values[:16]}'
        elif 'eu-startups.com' in domain:
            headers['Cookie'] = f'wordpress_logged_in_{cookie_values[:8]}=1; euCookie=1'
    
    return headers

def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text using regex.
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # Remove duplicates

def extract_urls(text: str, linkedin_only: bool = False) -> List[str]:
    """
    Extract URLs from text using regex.
    If linkedin_only is True, only extract LinkedIn URLs.
    """
    # General URL pattern
    url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*'
    
    if linkedin_only:
        linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/(?:company|in)/[-a-zA-Z0-9@:%._\+~#=]{1,256}'
        urls = re.findall(linkedin_pattern, text)
    else:
        urls = re.findall(url_pattern, text)
    
    return list(set(urls))  # Remove duplicates

def clean_text(text: str) -> str:
    """
    Clean text by removing excessive whitespace and normalizing line breaks.
    """
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def verify_url_exists(url: str) -> bool:
    """
    Check if a URL exists without downloading the full content.
    Returns True if the URL exists, False otherwise.
    """
    global request_count
    
    try:
        # Rotate IP if needed
        proxy = None
        if request_count >= MAX_REQUESTS_PER_IP:
            proxy = get_random_proxy()
            request_count = 0
        else:
            request_count += 1
        
        headers = get_browser_headers(url)
        
        # Set up proxy if available
        proxies = None
        if proxy:
            proxies = {
                "http": proxy,
                "https": proxy
            }
        
        response = requests.head(
            url, 
            headers=headers, 
            timeout=10, 
            allow_redirects=True,
            proxies=proxies
        )
        
        # Wait between requests
        wait_between_requests()
        
        return response.status_code < 400
    except Exception as e:
        print(f"Error verifying URL {url}: {e}")
        return False

def find_working_urls() -> List[str]:
    """
    Find URLs that actually work from our list of sources.
    Returns a list of verified URLs that respond with 200 OK.
    """
    working_urls = []
    
    # Check each URL in our sources list
    for url in CZECH_STARTUP_SOURCES:
        print(f"Verifying URL: {url}")
        if verify_url_exists(url):
            working_urls.append(url)
            print(f"✓ URL verified: {url}")
        else:
            print(f"✗ URL not accessible: {url}")
    
    return working_urls

def fetch_with_retry(url: str, max_retries: int = 3, delay: float = 2.0, proxy: str = None) -> str:
    """
    Fetch a URL with retry logic and proxy support.
    
    Args:
        url: The URL to fetch
        max_retries: Maximum number of retry attempts
        delay: Base delay between retries (will be randomized)
        proxy: Optional proxy URL (e.g., "http://user:pass@10.10.10.10:8000")
        
    Returns:
        The HTML content as a string
    """
    global request_count
    
    # Get fresh proxy if needed or use provided one
    if not proxy and request_count >= MAX_REQUESTS_PER_IP:
        proxy = get_random_proxy()
        request_count = 0
    else:
        request_count += 1
    
    # Generate dynamic headers for this request
    headers = get_browser_headers(url)
    
    # Add appropriate referrer for different sites
    parsed_url = urlparse(url)
    base_domain = parsed_url.netloc
    
    if "startupblink.com" in url:
        headers['Referer'] = 'https://www.google.com/search?q=startups+czech+republic'
    elif "crunchbase.com" in url:
        headers['Referer'] = 'https://www.google.com/search?q=crunchbase+czech+startups'
    elif "eu-startups.com" in url:
        headers['Referer'] = 'https://www.google.com/search?q=eu+startups+czech+republic'
    elif "dealroom.co" in url:
        headers['Referer'] = 'https://www.google.com/search?q=dealroom+czech+startup+report'
    else:
        # Generic referer from Google search
        headers['Referer'] = f'https://www.google.com/search?q={base_domain.replace(".", "+")}+czech+startups'
    
    proxies = None
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy
        }
    
    for attempt in range(max_retries):
        try:
            # Add a random delay to avoid rate limiting
            if attempt > 0:
                jitter = random.uniform(0.5, 1.5)
                time.sleep(delay * attempt * jitter)
            else:
                # Wait between requests even on first attempt
                wait_between_requests()
            
            # Create a session to maintain cookies
            session = requests.Session()
            
            # Generate client info to mimic browser behavior
            client_info = generate_random_client()
            
            # Pre-visit steps to appear more like a real browser
            if "startupblink.com" in url or "crunchbase.com" in url:
                # First get the base domain to set cookies
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                print(f"Pre-visiting {base_url} to set cookies...")
                
                # First request to the homepage
                session.get(
                    base_url, 
                    headers=headers, 
                    proxies=proxies, 
                    timeout=15
                )
                
                # Randomly update some headers between requests to mimic browser behavior
                headers['User-Agent'] = get_random_user_agent()
                
                # Add some randomized delay to mimic human browsing
                time.sleep(random.uniform(1, 3))
                
                # Second request to the actual page
                response = session.get(
                    url, 
                    headers=headers, 
                    proxies=proxies, 
                    timeout=15,
                    allow_redirects=True
                )
            else:
                # For other sites, make a direct request
                response = session.get(
                    url, 
                    headers=headers, 
                    proxies=proxies, 
                    timeout=15,
                    allow_redirects=True
                )
            
            response.raise_for_status()
            
            # Check response validity
            if len(response.text) < 500:
                if "captcha" in response.text.lower():
                    raise Exception("Captcha detected, will retry with different approach")
                elif "access denied" in response.text.lower() or "forbidden" in response.text.lower():
                    raise Exception("Access denied, will retry with different approach")
            
            return response.text
            
        except Exception as e:
            print(f"Attempt {attempt+1}/{max_retries} failed for {url}: {e}")
            
            # Change headers and proxy for next attempt
            headers = get_browser_headers(url)
            if attempt < max_retries - 1:  # Don't change on last attempt
                proxy = get_random_proxy()
                if proxy:
                    proxies = {
                        "http": proxy,
                        "https": proxy
                    }
            
            # If this was the last attempt, raise the exception
            if attempt == max_retries - 1:
                raise
    
    raise Exception(f"Failed to fetch {url} after {max_retries} attempts")

def try_google_search_results(query: str) -> Dict[str, str]:
    """
    Get content from Google search results for a query.
    This is a fallback method when direct site scraping fails.
    """
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        headers = get_browser_headers(search_url)
        proxy = get_random_proxy()
        
        proxies = None
        if proxy:
            proxies = {
                "http": proxy,
                "https": proxy
            }
        
        # Wait to avoid detection
        wait_between_requests()
        
        response = requests.get(
            search_url, 
            headers=headers, 
            timeout=15,
            proxies=proxies
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract search results
        search_results = []
        for result in soup.select('div.g'):
            title_elem = result.select_one('h3')
            snippet_elem = result.select_one('div.IsZvec')
            
            if title_elem and snippet_elem:
                title = title_elem.text
                snippet = snippet_elem.text.strip()
                search_results.append(f"Title: {title}\nSnippet: {snippet}\n")
        
        # Combine results
        content = f"Google search results for '{query}':\n\n" + "\n".join(search_results)
        
        return {
            'content': content,
            'url': search_url
        }
    except Exception as e:
        print(f"Error fetching Google search results for '{query}': {e}")
        return None

def scrape_multiple_sources() -> List[Dict[str, str]]:
    """
    Scrape data from multiple sources about Czech startups.
    Returns a list of dictionaries with 'content' and 'url' keys.
    """
    print("Finding working URLs for Czech startup data...")
    working_urls = find_working_urls()
    
    if not working_urls:
        print("No working URLs found in our primary sources. Using fallback search queries...")
        for query in FALLBACK_SEARCH_QUERIES:
            result = try_google_search_results(query)
            if result:
                return [result]
        return []
    
    results = []
    
    for url in working_urls:
        try:
            print(f"Scraping {url}...")
            
            # Use enhanced fetching with retry logic
            html_content = fetch_with_retry(url)
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try different selectors to find the main content
            main_content = (
                soup.find('main') or 
                soup.find('div', {'id': 'content'}) or 
                soup.find('div', {'class': 'content'}) or
                soup.find('article') or
                soup.find('div', {'class': 'entry-content'}) or
                soup.find('div', {'class': 'post-content'}) or
                soup.body
            )
            
            if main_content:
                content = main_content.get_text(separator='\n', strip=True)
                
                # Only add if we got meaningful content (more than 500 chars)
                if len(content) > 500:
                    results.append({
                        'content': clean_text(content),
                        'url': url
                    })
                    # If we've got at least 3 good sources, stop to avoid overwhelming
                    if len(results) >= 3:
                        break
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    # If we couldn't get any useful content, try Google searches as fallback
    if not results:
        print("No useful content found from direct URL scraping. Using fallback search queries...")
        for query in FALLBACK_SEARCH_QUERIES:
            result = try_google_search_results(query)
            if result:
                results.append(result)
                # One good search result is enough for fallback
                break
    
    return results

def scrape_startupblink_special() -> Dict[str, str]:
    """
    Special handling for StartupBlink which requires extra steps to bypass protections.
    """
    # First check if the URL actually exists
    url = "https://www.startupblink.com/startups/czech-republic"
    if not verify_url_exists(url):
        print(f"StartupBlink URL doesn't exist or isn't accessible: {url}")
        
        # Try alternative StartupBlink URL
        alt_url = "https://www.startupblink.com/startup-ecosystem/czech-republic"
        if not verify_url_exists(alt_url):
            print(f"Alternative StartupBlink URL isn't accessible either: {alt_url}")
            return None
        url = alt_url
    
    try:
        # Get a proxy for this request
        proxy = get_random_proxy()
        proxies = None
        if proxy:
            proxies = {
                "http": proxy,
                "https": proxy
            }
        
        # Create a session to maintain cookies
        session = requests.Session()
        
        # First visit the homepage to get cookies
        headers = get_browser_headers("https://www.startupblink.com/")
        session.get("https://www.startupblink.com/", headers=headers, timeout=15, proxies=proxies)
        
        # Wait a bit to seem more human
        time.sleep(random.uniform(3, 6))
        
        # Then visit the target page with same session (cookies maintained)
        headers = get_browser_headers(url)  # Fresh headers
        headers['Referer'] = "https://www.startupblink.com/"
        
        # Add some specific cookies that might help bypass protections
        cookies = session.cookies.get_dict()
        if not cookies:
            # Add some fake cookies if none were set by the server
            session.cookies.set('session_id', ''.join(random.choices(string.ascii_letters + string.digits, k=32)))
            session.cookies.set('has_js', '1')
            session.cookies.set('visited', '1')
        
        response = session.get(url, headers=headers, timeout=15, proxies=proxies)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the main content
        main_content = (
            soup.find('div', {'class': 'ecosystem-page'}) or 
            soup.find('div', {'id': 'content'}) or
            soup.find('div', {'class': 'content'}) or
            soup.find('main')
        )
        
        if main_content:
            content = main_content.get_text(separator='\n', strip=True)
            return {
                'content': clean_text(content),
                'url': url
            }
        
    except Exception as e:
        print(f"Error with special handling for StartupBlink: {e}")
    
    return None

def enrich_with_emails_and_urls(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich the analysis results with emails and URLs extracted directly from the raw content.
    """
    raw_content = data.get("raw_content", "")
    
    # Extract emails and URLs from raw content
    emails = extract_emails(raw_content)
    all_urls = extract_urls(raw_content)
    linkedin_urls = extract_urls(raw_content, linkedin_only=True)
    
    # Filter website URLs (exclude LinkedIn)
    websites = [url for url in all_urls if "linkedin.com" not in url]
    
    # Merge with existing data
    if "structured_data" in data and "contact_info" in data["structured_data"]:
        # Add emails
        existing_emails = set(data["structured_data"]["contact_info"]["emails"])
        existing_emails.update(emails)
        data["structured_data"]["contact_info"]["emails"] = list(existing_emails)
        
        # Add websites
        existing_websites = set(data["structured_data"]["contact_info"]["websites"])
        existing_websites.update(websites)
        data["structured_data"]["contact_info"]["websites"] = list(existing_websites)
        
        # Add LinkedIn URLs
        existing_linkedin = set(data["structured_data"]["contact_info"]["linkedin"])
        existing_linkedin.update(linkedin_urls)
        data["structured_data"]["contact_info"]["linkedin"] = list(existing_linkedin)
    
    return data

def get_linkedin_company_data(linkedin_url: str) -> Dict[str, Any]:
    """
    Attempt to extract company information from a LinkedIn company page URL.
    This is a simple implementation and might not work in all cases due to LinkedIn's protections.
    """
    headers = get_browser_headers(linkedin_url)
    
    # Get a proxy for this request
    proxy = get_random_proxy()
    proxies = None
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy
        }
    
    try:
        # Wait between requests
        wait_between_requests()
        
        response = requests.get(
            linkedin_url, 
            headers=headers,
            proxies=proxies,
            timeout=15
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract company name
        company_name = None
        name_elem = soup.find('h1', {'class': 'org-top-card-summary__title'})
        if name_elem:
            company_name = name_elem.text.strip()
        
        # Try to extract company location
        location = None
        location_elem = soup.find('div', {'class': 'org-top-card-summary__headquarters'})
        if location_elem:
            location = location_elem.text.strip()
        
        # Try to extract company description
        description = None
        desc_elem = soup.find('p', {'class': 'org-top-card-summary__tagline'})
        if desc_elem:
            description = desc_elem.text.strip()
        
        return {
            'name': company_name,
            'location': location,
            'description': description,
            'url': linkedin_url
        }
    
    except Exception as e:
        print(f"Error extracting data from LinkedIn URL {linkedin_url}: {e}")
        return {
            'name': None,
            'location': None,
            'description': None,
            'url': linkedin_url
        } 