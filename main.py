import os
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import Dict, List, Any, Tuple
import utils
import json

# Try different import methods for SerpAPI
try:
    from serpapi import google_search
except ImportError:
    try:
        import serpapi
        google_search = serpapi.search
    except (ImportError, AttributeError):
        try:
            from serpapi import GoogleSearch
            def google_search(params):
                search = GoogleSearch(params)
                return search.get_dict()
        except ImportError:
            print("Warning: Neither serpapi nor google-search-results package is installed properly.")
            google_search = None

# Load environment variables
load_dotenv()

def get_search_results(query: str, num_results: int = 10) -> Tuple[str, str]:
    """
    Use SerpAPI to get search results about Czech startups.
    Returns the raw text content and the search query used.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        print("Warning: SERPAPI_API_KEY not set. Falling back to direct scraping.")
        return scrape_startup_data()
    
    if google_search is None:
        print("Warning: SerpAPI functionality not available. Please install with: pip install google-search-results")
        return scrape_startup_data()
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": num_results,
        "gl": "cz",  # Country to use for the search (Czech Republic)
    }
    
    try:
        # Use serpapi.search function instead of GoogleSearch
        results = google_search(params)
        
        organic_results = results.get("organic_results", [])
        news_results = results.get("news_results", [])
        
        combined_text = f"Search query: {query}\n\n"
        
        # Add organic search results
        combined_text += "ORGANIC SEARCH RESULTS:\n\n"
        for i, result in enumerate(organic_results):
            combined_text += f"Result {i+1}:\n"
            combined_text += f"Title: {result.get('title', 'No title')}\n"
            combined_text += f"Link: {result.get('link', 'No link')}\n"
            combined_text += f"Snippet: {result.get('snippet', 'No snippet')}\n\n"
        
        # Add news results if available
        if news_results:
            combined_text += "NEWS RESULTS:\n\n"
            for i, result in enumerate(news_results):
                combined_text += f"News {i+1}:\n"
                combined_text += f"Title: {result.get('title', 'No title')}\n"
                combined_text += f"Link: {result.get('link', 'No link')}\n"
                combined_text += f"Snippet: {result.get('snippet', 'No snippet')}\n\n"
        
        return combined_text, query
    
    except Exception as e:
        print(f"Error using SerpAPI: {e}")
        print("Falling back to direct scraping.")
        return scrape_startup_data()

def scrape_startup_data() -> Tuple[str, str]:
    """
    Scrape data about Czech startups from relevant websites.
    Returns the raw text content and the URL used.
    """
    combined_text = ""
    primary_url = ""
    
    # First try the special handler for StartupBlink
    print("Trying special handling for StartupBlink...")
    startupblink_data = utils.scrape_startupblink_special()
    if startupblink_data:
        combined_text += f"\n\n--- DATA FROM {startupblink_data['url']} ---\n\n"
        combined_text += startupblink_data['content']
        primary_url = startupblink_data['url']
    
    # Then try to scrape from multiple sources
    scraped_data = utils.scrape_multiple_sources()
    
    if scraped_data or combined_text:
        # If we already have startupblink data but also got other data
        if not primary_url and scraped_data:
            primary_url = scraped_data[0]['url']
        
        # Add all scraped content with source information
        for item in scraped_data:
            combined_text += f"\n\n--- DATA FROM {item['url']} ---\n\n"
            combined_text += item['content']
        
        if combined_text:
            return combined_text, primary_url
    
    # If all scraping failed, return a message
    error_msg = "Failed to scrape data from any source. Consider using a different approach like SerpAPI or manual research."
    return error_msg, "N/A"

def create_prompt() -> PromptTemplate:
    """
    Create a prompt template for the LLM.
    """
    template = """
    You are a data analysis expert focusing on the startup ecosystem in the Czech Republic.
    
    Below is data from search results about Czech startups from {url}:
    
    {content}
    
    Based on this data, please provide a structured analysis with the following information:
    
    1. Estimate the number of startups in the Czech Republic (provide a specific number or range)
    2. Identify top 3-5 cities where startups are concentrated
    3. List the main industries or sectors where Czech startups are active
    4. Extract all email addresses that appear in the data
    5. Extract all company websites or LinkedIn URLs that appear in the data
    
    Format your response as follows:
    
    NUMBER OF STARTUPS: [your estimate]
    
    TOP STARTUP CITIES:
    - [City 1]: [brief description if available]
    - [City 2]: [brief description if available]
    ...
    
    KEY INDUSTRIES:
    - [Industry 1]: [brief description if available]
    - [Industry 2]: [brief description if available]
    ...
    
    CONTACT INFORMATION:
    - Emails: [list of unique email addresses]
    - Websites: [list of unique website URLs]
    - LinkedIn: [list of unique LinkedIn URLs]
    
    INSIGHTS AND NOTES:
    [Any additional insights or caveats about your analysis]
    """
    
    return PromptTemplate(
        input_variables=["content", "url"],
        template=template
    )

def process_with_llm(content: str, url: str) -> str:
    """
    Process the scraped content with an LLM using LangChain.
    """
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY environment variable not set. Please set it in a .env file or export it in your shell."
    
    try:
        # Try to initialize with GPT-4 first
        try:
            llm = ChatOpenAI(
                model_name="gpt-4",  # Preferred model
                temperature=0.2,
                max_tokens=1500
            )
        except Exception as model_error:
            print(f"Error using GPT-4: {str(model_error)}. Falling back to GPT-3.5-turbo.")
            # Fall back to GPT-3.5-turbo if GPT-4 is not available
            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",  # Fallback model
                temperature=0.2,
                max_tokens=1500
            )
        
        # Create the prompt template
        prompt = create_prompt()
        
        # Create the chain
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Run the chain
        response = chain.run(content=content, url=url)
        
        return response
    except Exception as e:
        error_msg = str(e)
        print(f"Error using OpenAI API: {error_msg}")
        
        # Provide a more user-friendly error message
        if "API key" in error_msg or "Authentication" in error_msg:
            return "Error: Invalid OpenAI API key. Please check your OPENAI_API_KEY environment variable."
        elif "quota" in error_msg or "rate limit" in error_msg:
            return "Error: OpenAI API rate limit exceeded or quota exhausted. Please try again later."
        elif "model" in error_msg and "do not exist" in error_msg:
            return "Error: The specified model is not available. Try using 'gpt-3.5-turbo' instead."
        else:
            return f"Error calling OpenAI API: {error_msg}"

def extract_structured_data(llm_response: str) -> Dict[str, Any]:
    """
    Parse the LLM's response into structured data.
    """
    result = {
        "number_of_startups": "",
        "top_cities": [],
        "key_industries": [],
        "contact_info": {
            "emails": [],
            "websites": [],
            "linkedin": []
        },
        "insights": ""
    }
    
    # Extract number of startups
    number_match = re.search(r"NUMBER OF STARTUPS:\s*(.*?)(?:\n\n|\Z)", llm_response, re.DOTALL)
    if number_match:
        result["number_of_startups"] = number_match.group(1).strip()
    
    # Extract top cities
    cities_section = re.search(r"TOP STARTUP CITIES:\s*(.*?)(?:\n\n|\Z)", llm_response, re.DOTALL)
    if cities_section:
        cities_text = cities_section.group(1).strip()
        city_items = re.findall(r"- (.*?)(?:\n|$)", cities_text)
        result["top_cities"] = [city.strip() for city in city_items if city.strip()]
    
    # Extract key industries
    industries_section = re.search(r"KEY INDUSTRIES:\s*(.*?)(?:\n\n|\Z)", llm_response, re.DOTALL)
    if industries_section:
        industries_text = industries_section.group(1).strip()
        industry_items = re.findall(r"- (.*?)(?:\n|$)", industries_text)
        result["key_industries"] = [industry.strip() for industry in industry_items if industry.strip()]
    
    # Extract contact information
    contact_section = re.search(r"CONTACT INFORMATION:\s*(.*?)(?:\n\n|\Z)", llm_response, re.DOTALL)
    if contact_section:
        contact_text = contact_section.group(1).strip()
        
        # Extract emails
        emails_match = re.search(r"Emails:\s*(.*?)(?:\n|$)", contact_text)
        if emails_match:
            emails_text = emails_match.group(1).strip()
            result["contact_info"]["emails"] = [email.strip() for email in emails_text.split(',') if email.strip()]
        
        # Extract websites
        websites_match = re.search(r"Websites:\s*(.*?)(?:\n|$)", contact_text)
        if websites_match:
            websites_text = websites_match.group(1).strip()
            result["contact_info"]["websites"] = [website.strip() for website in websites_text.split(',') if website.strip()]
        
        # Extract LinkedIn URLs
        linkedin_match = re.search(r"LinkedIn:\s*(.*?)(?:\n|$)", contact_text)
        if linkedin_match:
            linkedin_text = linkedin_match.group(1).strip()
            result["contact_info"]["linkedin"] = [linkedin.strip() for linkedin in linkedin_text.split(',') if linkedin.strip()]
    
    # Extract insights
    insights_match = re.search(r"INSIGHTS AND NOTES:\s*(.*?)(?:\Z)", llm_response, re.DOTALL)
    if insights_match:
        result["insights"] = insights_match.group(1).strip()
    
    return result

def main():
    """
    Main function to run the startup analysis.
    """
    print("Getting data about Czech startups...")
    # Use SerpAPI with a focused query
    content, query = get_search_results("how many startups in Czech Republic statistics data")
    
    print(f"Processing data from search query: {query}")
    llm_response = process_with_llm(content, query)
    
    print("\n--- LLM Analysis ---")
    print(llm_response)
    
    # Extract structured data from LLM response
    structured_data = extract_structured_data(llm_response)
    
    # Create the results dictionary
    results = {
        "raw_content": content,
        "url": query,
        "llm_response": llm_response,
        "structured_data": structured_data
    }
    
    # Enrich the results with additional emails and URLs extracted directly from the raw content
    enriched_results = utils.enrich_with_emails_and_urls(results)
    
    return enriched_results

if __name__ == "__main__":
    results = main()
    
    # Print key findings
    data = results["structured_data"]
    print("\n--- Key Findings ---")
    print(f"Number of startups: {data['number_of_startups']}")
    print(f"Top cities: {', '.join(data['top_cities'])}")
    print(f"Key industries: {', '.join(data['key_industries'])}")
    
    if data["contact_info"]["emails"]:
        print(f"Found {len(data['contact_info']['emails'])} email addresses")
    
    if data["contact_info"]["websites"]:
        print(f"Found {len(data['contact_info']['websites'])} website URLs")
    
    if data["contact_info"]["linkedin"]:
        print(f"Found {len(data['contact_info']['linkedin'])} LinkedIn profiles") 