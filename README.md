# Czech Startup Ecosystem Analyzer

An application to analyze the startup ecosystem in the Czech Republic using web scraping and LLM processing.

## Features

- Scrapes data from multiple sources about Czech startups
- Uses advanced anti-blocking measures for reliable web scraping
- Processes the data with GPT-4 (or GPT-3.5-turbo as fallback)
- Extracts structured information including:
  - Number of startups in the Czech Republic
  - Top cities for startups
  - Key industries
  - Contact information (emails, websites, LinkedIn profiles)
- Provides a user-friendly Streamlit interface

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/abhimattx/StartInsightCZ.git
   cd StartInsightCZ
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Mac/Linux
   source .venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   # Required
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Optional - for enhanced search functionality
   SERPAPI_API_KEY=your_serpapi_api_key_here
   ```

## API Keys Setup

### OpenAI API Key (Required)
1. Visit [OpenAI's platform](https://platform.openai.com/signup)
2. Sign up for an account if you don't have one
3. Navigate to the [API keys section](https://platform.openai.com/api-keys)
4. Create a new secret key
5. Copy the key and add it to your `.env` file as shown above

### SerpAPI Key (Optional)
1. Visit [SerpAPI](https://serpapi.com/users/sign_up)
2. Create an account
3. Get your API key from the dashboard
4. Copy the key and add it to your `.env` file as shown above

## Usage

1. Run the Streamlit app:
   ```
   streamlit run streamlit_app.py
   ```

2. Open your browser and go to the URL shown in the terminal (usually http://localhost:8501)

3. Click "Run Analysis" to start the scraping and analysis process

4. View the results in the UI

## Troubleshooting

### API Key Issues
- If you get an authentication error, double-check your API keys in the `.env` file
- Ensure the OpenAI API key has sufficient credits and permissions

### Web Scraping Issues
- If you encounter 403 Forbidden errors, the application will automatically try to use alternative scraping methods
- The app includes sophisticated anti-blocking measures, but some websites might still block access
- Consider using the SerpAPI fallback option by providing a SerpAPI key

### Model Availability
- The app will try to use GPT-4 first, but will fall back to GPT-3.5-turbo if GPT-4 is not available
- If you don't have access to GPT-4, the app will automatically use GPT-3.5-turbo

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

- **Abhishek Singh** - [GitHub Profile](https://github.com/abhimattx)

