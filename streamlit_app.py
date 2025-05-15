import streamlit as st
import main
import utils
import json
import re

def display_contact_info(contact_info):
    """Display contact information in a formatted way."""
    if contact_info["emails"]:
        st.subheader("Email Addresses")
        for email in contact_info["emails"]:
            st.markdown(f"- {email}")
    
    if contact_info["websites"]:
        st.subheader("Websites")
        for website in contact_info["websites"]:
            st.markdown(f"- [{website}]({website})")
    
    if contact_info["linkedin"]:
        st.subheader("LinkedIn Profiles")
        for linkedin in contact_info["linkedin"]:
            if not linkedin.startswith("http"):
                linkedin = f"https://{linkedin}"
            st.markdown(f"- [{linkedin}]({linkedin})")

def run_analysis():
    """Run the startup analysis and store results in session state."""
    try:
        with st.spinner("Scraping data and analyzing with LLM..."):
            results = main.main()
            
            # Check if the LLM response contains an error message
            if results and isinstance(results, dict) and "llm_response" in results:
                llm_response = results["llm_response"]
                if llm_response.startswith("Error:"):
                    st.error(llm_response)
                    # Create a minimal results structure to avoid errors in the UI
                    results = {
                        "raw_content": "Error occurred during analysis",
                        "url": "N/A",
                        "llm_response": llm_response,
                        "structured_data": {
                            "number_of_startups": "N/A",
                            "top_cities": [],
                            "key_industries": [],
                            "contact_info": {
                                "emails": [],
                                "websites": [],
                                "linkedin": []
                            },
                            "insights": "An error occurred during the analysis."
                        }
                    }
            
            st.session_state.results = results
            return results
    except Exception as e:
        error_msg = str(e)
        st.error(f"An error occurred: {error_msg}")
        
        # Create a minimal results structure to avoid errors in the UI
        results = {
            "raw_content": f"Error: {error_msg}",
            "url": "N/A",
            "llm_response": f"Error: {error_msg}",
            "structured_data": {
                "number_of_startups": "N/A",
                "top_cities": [],
                "key_industries": [],
                "contact_info": {
                    "emails": [],
                    "websites": [],
                    "linkedin": []
                },
                "insights": "An error occurred during the analysis."
            }
        }
        st.session_state.results = results
        return results

st.set_page_config(
    page_title="Czech Startup Analyzer",
    page_icon="🚀",
    layout="wide"
)

st.title("Czech Startup Ecosystem Analyzer")
st.markdown("This app analyzes the startup ecosystem in the Czech Republic using web scraping and LLM analysis.")

# Initialize session state for results if not already done
if "results" not in st.session_state:
    st.session_state.results = None

# Add a button to run the analysis
if st.button("Run Analysis") or st.session_state.results:
    if st.session_state.results is None:
        results = run_analysis()
    else:
        results = st.session_state.results
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("LLM Analysis")
        structured_data = results["structured_data"]
        
        st.subheader("Number of Startups")
        st.markdown(f"**{structured_data['number_of_startups']}**")
        
        st.subheader("Top Startup Cities")
        for city in structured_data["top_cities"]:
            st.markdown(f"- {city}")
        
        st.subheader("Key Industries")
        for industry in structured_data["key_industries"]:
            st.markdown(f"- {industry}")
        
        if structured_data["insights"]:
            st.subheader("Additional Insights")
            st.markdown(structured_data["insights"])
    
    with col2:
        st.header("Contact Information")
        display_contact_info(structured_data["contact_info"])
    
    # Show raw data in an expandable section
    with st.expander("View Raw Scraped Data"):
        st.text_area("Raw Content", results["raw_content"], height=300)
    
    with st.expander("View Full LLM Response"):
        st.markdown(results["llm_response"])

# Add information about the app
with st.expander("About this app"):
    st.markdown("""
    This application:
    1. Scrapes data about Czech startups from websites like StartupBlink
    2. Uses LangChain and GPT-4 to analyze the scraped content
    3. Provides insights about the number of startups, top cities, and key industries
    4. Extracts contact information including emails, websites, and LinkedIn profiles
    
    Technologies used:
    - Python
    - LangChain
    - OpenAI API (GPT-4)
    - BeautifulSoup for web scraping
    - Streamlit for the user interface
    """) 