#!/usr/bin/env python3
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

class WebSearchScraper:
    def __init__(self):
        self.chrome_options = Options()
        # Uncomment headless to run without a visible browser window.
        # self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        # Suppress logging
        self.chrome_options.add_argument("--log-level=3")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        )

    def duckduckgo_search_scrape(self, query):
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.get("https://duckduckgo.com")
        time.sleep(2)
        search_box = driver.find_element("name", "q")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(10)  # Wait for results to load
        html = driver.page_source
        driver.quit()
        return html

    def parse_search_results(self, html):
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
        # Look for h2 elements with a unique class substring from our sample.
        # These classes may need to be updated periodically.
        for header in soup.find_all("h2", class_=lambda c: c and "LnpumSThxEWMIsDdAT17" in c):
            a_tag = header.find("a", href=True)
            if not a_tag:
                continue
            link = a_tag["href"]
            title = a_tag.get_text(strip=True)
            snippet_div = header.find_next("div", class_=lambda c: c and "E2eLOJr8HctVnDOTM8fs" in c)
            snippet = snippet_div.get_text(separator=" ", strip=True) if snippet_div else "No snippet"
            results.append({
                "link": link,
                "title": title,
                "snippet": snippet
            })
        return results

    def scrape_page_content(self, url):
        options = Options()\
        
        # Uncomment to view the Selenium Browser
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        )
        driver = webdriver.Chrome(options=options)
        try:
            print(f"Scraping: {url}")
            driver.get(url)
            time.sleep(5)  # Wait for page content to load
            html = driver.page_source
        except Exception as e:
            html = f"Error retrieving content from {url}: {e}"
        driver.quit()
        return html

    def extract_relevant_text(self, html):
        soup = BeautifulSoup(html, "html.parser")
        # Only process tags that typically contain article content.
        allowed_tags = {"p", "article", "b"}
        allowed_pattern = re.compile(r'^[A-Za-z0-9\s\.,!\?\'":;\-]+$')
        texts = []
        for tag in soup.find_all(allowed_tags):
            txt = tag.get_text(separator=" ", strip=True)
            if not txt:
                continue
            # Only include text if it meets one of these conditions:
            # 1. It is longer than 100 characters.
            # 2. It is at least 50 characters long, contains at least 4 spaces,
            # 3. Consists only of allowed characters.
            if len(txt) >= 100 or (len(txt) >= 50 and txt.count(" ") >= 4 and allowed_pattern.match(txt)):
                texts.append(txt)
        # Remove duplicates.
        unique_texts = list(dict.fromkeys(texts))
        # Join list into a multi-line string, then filter the lines.
        joined_text = "\n".join(unique_texts)
        filtered_texts = self.filterLines(joined_text)
        return "\n\n".join(filtered_texts)

    def filterLines(self, text):
        filtered = []
        for line in text.splitlines():
            non_whitespace = "".join(line.split())
            if len(non_whitespace) > 50:
                filtered.append(line)
        return filtered

    def webSearch_text(self, query):
        search_html = self.duckduckgo_search_scrape(query)
        results = self.parse_search_results(search_html)
        if not results:
            return "No search results found."
        aggregated_text = ""
        # Only process the top 3 search results.
        for result in results[:3]:
            page_html = self.scrape_page_content(result["link"])
            relevant_text = self.extract_relevant_text(page_html)
            aggregated_text += relevant_text + "\n\n"
        return aggregated_text

# Example usage:
if __name__ == "__main__":
    query = input("Enter search query (default: what is today's date?): ").strip()
    if not query:
        query = "what is today's date?"
    scraper = WebSearchScraper()
    final_text = scraper.webSearch_text(query)
    print(final_text)
