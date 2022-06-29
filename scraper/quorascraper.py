import json
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm


class QuoraScraper():
    def __init__(self, prefix: str, keywords: set, suffix: str = '', posts_per_keyword: int = 10, times_to_retry: int = 10, is_streamlit: bool = False, output_container=None) -> None:
        self.streamlit = is_streamlit
        self.output_container = output_container
        self.prefix = prefix
        self.suffix = suffix
        self.keywords = keywords
        self.posts_per_keyword = posts_per_keyword
        self.times_to_retry = times_to_retry

    def display(self, string):
        if self.streamlit:
            self.output_container.text(string)
        else:
            print(string)

    def scrape(self):
        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(
            options=options,
            executable_path='./scraper/geckodriver.exe')

        data = {}

        overall_count = 0
        start = time.time()

        for keyword in self.keywords:
            self.display(f'\nBEGIN SEARCH: {keyword}')
            data[keyword] = []
            driver.get(self.prefix + keyword + self.suffix)
            time.sleep(2)

            last_len = 0
            no_new_posts_retrial_count = 0
            sentences = set()
            if self.streamlit:
                pbars = {}

            if not self.streamlit:
                pbar = tqdm(
                    ncols=80, total=self.posts_per_keyword, unit='post',)
            else:

                pbars[keyword] = self.output_container.progress(0)

            while True:
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")

                time.sleep(1)

                page_source = driver.page_source

                soup = BeautifulSoup(
                    page_source.encode("utf-8"), "html.parser")

                posts = [post for post in soup.findAll('span', {'class': 'qt_truncated_inline'}) if post.get_text(
                ) != '' and not post.get_text().isspace()]

                for post in posts:
                    for sentence in re.split('[.\n!?]', post.get_text()):
                        if re.search((keyword if keyword.isupper() else f'{keyword}|{keyword.lower()}|{keyword.title()}'), sentence):
                            sentences.add(sentence)

                if not self.streamlit:
                    pbar.update(
                        (min(len(sentences), self.posts_per_keyword)) - pbar.n)
                else:
                    pbars[keyword].progress(
                        (min(len(sentences), self.posts_per_keyword)/self.posts_per_keyword))
                
                if last_len != len(sentences):
                    last_len = len(sentences)
                    no_new_posts_retrial_count = 0
                else:
                    no_new_posts_retrial_count += 1
                    if no_new_posts_retrial_count >= self.times_to_retry:
                        no_new_posts_retrial_count = 0
                        if not self.streamlit:
                            pbar.close()
                        self.display(f'Could only find {len(sentences)}')
                        break
                
                if len(sentences) >= self.posts_per_keyword:
                    no_new_posts_retrial_count = 0
                    if not self.streamlit:
                        pbar.close()
                    break
            if not self.streamlit:
                pbar.close()

            self.display(
                f'Got {len(sentences)} for "{keyword}", using {self.posts_per_keyword}')
            data[keyword] = list(sentences)[:self.posts_per_keyword]
            overall_count += self.posts_per_keyword
        self.display(
            f'Total of {overall_count} sentences gathered in {time.time() - start} seconds.')
        
        if self.streamlit:
            json_string = json.dumps(data)
            self.output_container.download_button(
                label="As .json", data=json_string, file_name='sentences.json', mime='application/json')
        else:
            with open('data.json', 'w') as file:
                json.dump(obj=data, fp=file)


if __name__ == '__main__':

    keywords = []
    with open('termsofinterest.txt', 'r') as file:
        keywords = file.read().split('\n')

    scraper = QuoraScraper(prefix='https://www.quora.com/search?q="',
                           keywords=keywords, suffix='"&type=answer', posts_per_keyword=20)
    scraper.scrape()
