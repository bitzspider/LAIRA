# LAIRA – LangChain Artificial Intelligence Research Assistants

## Overview
**LAIRA** is a Python-based project that automates AI-driven research workflows using a multi-agent system. It generates subqueries from a user-provided query, performs web searches using Selenium and BeautifulSoup, and compiles the relevant findings into a comprehensive research report. LAIRA leverages LangChain components and Gradio for a user-friendly web interface, while python-dotenv is used for managing environment configurations.

## Features
- **Automated Query Processing:** Breaks down complex research queries into subqueries.
- **Web Scraping:** Uses Selenium and BeautifulSoup to fetch and parse search results.
- **Multi-Agent Collaboration:** Coordinates between search and report agents to gather and synthesize information.
- **Comprehensive Reporting:** Compiles relevant search snippets into a final, well-structured research report.
- **Web Interface:** Provides an interactive UI through Gradio.

## How It Works
1. **Subquery Generation:**  
   The system generates subqueries based on the user's research query to target specific information areas.

2. **Web Search and Scraping:**  
   Each subquery is used to perform a web search. The search tool scrapes the resulting web pages to extract relevant text snippets.

3. **Relevance Assessment:**  
   An agent evaluates the relevance of each snippet and aggregates the useful ones.

4. **Final Report Compilation:**  
   The relevant snippets are compiled into a final report, which is then presented to the user through a Gradio interface.

## Folder Structure
- **main.py**  
  Entry point for the LAIRA application. It initializes the agents, manages the research workflow, and launches the Gradio interface.
  
- **search_tool.py**  
  Contains the web scraping functionality using Selenium and BeautifulSoup.
  
- **requirements.txt**  
  Lists all the required Python dependencies for the project.
  
- **.env**  
  Contains environment variables (e.g., API keys and configuration settings). *This file should not be committed to version control.*
  
- **venv/**  
  Virtual environment folder (should be added to `.gitignore`).

## Clone the Repository
Clone the repository to your local machine:
```bash
git clone [<repository-url>](https://github.com/bitzspider/LAIRA.git)
cd LAIRA
