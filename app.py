import streamlit as st
import requests
import feedparser
from transformers import pipeline

class ArxivScraper:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query?"
        self.search_term = ""
        self.start = 0
        self.max_results = 10
        self.results = []
        self.generator = pipeline('text-generation', model='EleutherAI/gpt-neo-2.7B')

    def set_search_term(self, term):
        if not term.strip():
            st.error("Search term cannot be empty.")
            return False
        self.search_term = term
        return True

    def set_start(self, start):
        if start < 0:
            st.error("Starting index must be non-negative.")
            return False
        self.start = start
        return True

    def set_max_results(self, max_results):
        if not (1 <= max_results <= 100):
            st.error("Maximum results must be between 1 and 100.")
            return False
        self.max_results = max_results
        return True

    def execute_query(self):
        query = f"search_query=ti:{self.search_term}&start={self.start}&max_results={self.max_results}"
        try:
            response = requests.get(self.base_url + query)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            self.results = sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)
        except requests.RequestException as e:
            st.error(f"Failed to fetch data: {str(e)}")

    def generate_explanation(self, summary):
        result = self.generator(summary, max_length=150, num_return_sequences=1)[0]
        return result['generated_text']

    def display_results(self):
        if not self.results:
            st.write("No results found.")
            return
        for entry in self.results:
            with st.container():
                st.markdown(f"### {entry.title}")
                st.markdown(f"[Read More]({entry.link})")
                explanation = self.generate_explanation(entry.summary)
                st.markdown(f"**Detailed Explanation:** {explanation}")
                st.markdown(f"**Summary:** {entry.summary}")
                st.write("Published:", entry.published)
                st.write("="*60)

st.title('ArXiv Scraper')

scraper = ArxivScraper()

if scraper.set_search_term(st.text_input("Enter the search term")):
    if scraper.set_start(st.number_input("Enter the starting index (default is 0)", min_value=0, value=0, step=1)):
        if scraper.set_max_results(st.number_input("Enter the maximum number of results (default is 10)", min_value=1, value=10, step=1)):
            if st.button('Scrape'):
                scraper.execute_query()
                scraper.display_results()
