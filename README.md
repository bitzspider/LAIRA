```md
# LAIRA – LangChain Artificial Intelligence Research Assistants

## Overview
LAIRA is a Python-based project that automates AI-driven research workflows using a multi-agent system. It accepts a user query, breaks it into targeted subqueries, searches the web using Selenium and BeautifulSoup, and compiles the collected data into a comprehensive research report. The project leverages LangChain for AI components, Gradio for a user-friendly web interface, and python-dotenv for environment configuration.

## Features
- **Automated Query Processing:** Breaks down complex research queries into manageable subqueries.
- **Web Scraping:** Retrieves and parses data from web pages using Selenium and BeautifulSoup.
- **Multi-Agent Collaboration:** Coordinates multiple agents to efficiently gather and process information.
- **Comprehensive Reporting:** Aggregates search results into a structured final report.
- **User-Friendly Interface:** Provides an interactive UI through Gradio.

## How It Works
1. **Subquery Generation:**  
   LAIRA splits the initial research query into multiple targeted subqueries.
2. **Web Search and Data Extraction:**  
   Each subquery is used to perform a web search. Selenium and BeautifulSoup then scrape relevant data from the results.
3. **Data Aggregation:**  
   An intelligent agent evaluates and compiles the best data snippets.
4. **Final Report Compilation:**  
   The aggregated data is presented as a well-organized research report via a Gradio web interface.

## Folder Structure
- **main.py**  
  Entry point of the application. It initializes the agents, manages the research workflow, and launches the web interface.
- **search_tool.py**  
  Contains functions for web scraping using Selenium and BeautifulSoup.
- **requirements.txt**  
  Lists the Python dependencies required for the project.
- **.env**  
  Stores environment variables (do not commit this file to version control).
- **venv/**  
  Virtual environment folder (should be added to `.gitignore`).

## Installation and Setup

### 1. Clone the Repository
Clone the project repository to your local machine:
```bash
git clone https://github.com/bitzspider/LAIRA.git
cd LAIRA
```

### 2. Create a Virtual Environment
It is recommended to create a virtual environment to manage project dependencies.

#### For Windows (CMD or PowerShell)
```bash
python -m venv venv
venv\Scripts\activate
```

#### For macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
With the virtual environment activated, install the necessary Python packages:
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root and add your environment-specific settings. For example:
```env
API_KEY=your_api_key_here
OTHER_CONFIG=your_other_config_here
```

### 5. Run the Application
Start the application with:
```bash
python main.py
```

## Usage
After starting the application, open your web browser and navigate to the address provided by Gradio (usually [http://127.0.0.1:7860](http://127.0.0.1:7860)). Enter your research query in the interface, and LAIRA will process the query, perform web searches, and generate a comprehensive research report.

## Troubleshooting
- **Virtual Environment Issues:** Ensure the virtual environment is activated before installing dependencies.
- **Dependency Errors:** Verify that all required packages from `requirements.txt` are installed.
- **Web Interface Not Loading:** Check if the default port (7860) is in use or modify the configuration as needed.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request with your suggestions or improvements.

## License
This project is licensed under the [MIT License](LICENSE).
```
