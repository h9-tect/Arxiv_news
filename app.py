import streamlit as st
import requests
import feedparser

class ArxivScraper:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query?"
        self.search_term = ""
        self.start = 0
        self.max_results = 10
        self.results = []

    def set_search_term(self, term):
        self.search_term = term

    def set_start(self, start):
        self.start = start

    def set_max_results(self, max_results):
        self.max_results = max_results

    def execute_query(self):
        query = f"search_query=ti:{self.search_term}&start={self.start}&max_results={self.max_results}"
        response = requests.get(self.base_url + query)

        if response.status_code != 200:
            st.error("Error fetching data from ArXiv!")
            return

        feed = feedparser.parse(response.content)

        # Sorting results based on publication date in descending order
        sorted_entries = sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)
        self.results = sorted_entries

    def display_results(self):
        for entry in self.results:
            with st.container():
                st.markdown(f"### {entry.title}")
                st.markdown(f"[Read More]({entry.link})")
                st.markdown(f"**Summary:** {entry.summary}")
                st.write("Published:", entry.published)
                st.write("="*60)

# Streamlit app starts here
st.title('ArXiv Scraper')

scraper = ArxivScraper()

# Input fields
scraper.set_search_term(st.text_input("Enter the search term"))
scraper.set_start(st.number_input("Enter the starting index (default is 0)", min_value=0, value=0, step=1))
scraper.set_max_results(st.number_input("Enter the maximum number of results (default is 10)", min_value=1, value=10, step=1))

if st.button('Scrape'):
    scraper.execute_query()
    scraper.display_results()

