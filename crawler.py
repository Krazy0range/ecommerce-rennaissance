import asyncio
import bs4
import nodriver
import random
import time
import tldextract

from database import Database


class Crawler:

    def __init__(self, main_url, urls_db_path, max_crawl_depth, debug=False, save_period=10):
        self.main_url = main_url
        parsed_url = tldextract.extract(self.main_url)
        self.domain = parsed_url.domain

        self.urls_db = Database(urls_db_path)
        self.max_crawl_depth = max_crawl_depth
        self.debug = debug
        self.save_period = save_period

        self.page_counter = 0

    def add_url_reference(self, url_i):
        self.urls_db.data[url_i][1] += 1

    def load_urls_set(self):
        self.urls_set = set()

        for row in self.urls_db.data:
            unique_url = UniqueURL(row[0], row[1], row[2])
            self.urls_set.add(unique_url)

    def convert_urls_set(self):
        for url in self.urls_set:
            self.urls_db.data.append(url.to_list())

    def crawl(self):

        def integerize(row):
            row[1] = int(row[1])
            row[2] = int(row[2])

        self.urls_db.read_data(func=integerize)
        self.load_urls_set()

        asyncio.run(self.crawl_())

        print("\x1b[1;42mwriting url data\x1b[0m")
        self.convert_urls_set()
        self.urls_db.write_data()

    async def crawl_(self):
        self.driver = await nodriver.start()

        if self.urls_db.data == []:
            url = "https://" + self.main_url
            await self.crawl_page_(url, 0)
        else:
            # ensures semi-even scraping over multiple iterations
            # of the program. TODO improve this, use a pending_urls
            # database maybe with URLs connected to a scraping depth
            shuffled_data = random.sample(self.urls_db.data, len(self.urls_db.data))
            max_pages = len(shuffled_data)
            for row in shuffled_data:
                await self.crawl_page_(row[0], 0, max_pages=max_pages)

        self.driver.stop()

    async def crawl_page_(self, page_url, crawl_depth, max_pages=None):
        self.page_counter += 1
        if self.page_counter % self.save_period == 0:
            print("\x1b[1;42mwriting url data\x1b[0m")
            self.urls_db.write_data()

        if max_pages:
            print(f"\x1b[1;42mscraping page {self.page_counter}/{max_pages}\x1b[0m", page_url)
        else:
            print(f"\x1b[1;42mscraping page {self.page_counter}\x1b[0m", page_url)

        page = await self.driver.get(page_url)
        page_content = await page.get_content()
        soup = bs4.BeautifulSoup(page_content, "html.parser")
        soup_links = soup.find_all("a", href=True)
        pending_urls = []

        for soup_link in soup_links:
            link_href = soup_link["href"]
            pending_urls.append(link_href)

        pending_urls_set = {UniqueURL(url, 0, 0) for url in pending_urls}
        pending_urls_set.difference_update(self.urls_set)

        for pending_unique_url in pending_urls_set:
            pending_url = pending_unique_url.url

            parsed_url = tldextract.extract(pending_url)
            if parsed_url.domain == "":
                url = "https://" + self.main_url + pending_url
            elif parsed_url.domain != self.domain:
                if self.debug:
                    print("\x1b[31moutside url\x1b[0m", pending_url)
                continue
            else:
                url = pending_url

            if self.debug:
                print("\x1b[32mvalid url\x1b[0m", url)

            timestamp = int(time.time())
            self.urls_set.add(UniqueURL(url, 0, timestamp))

            if crawl_depth < self.max_crawl_depth:
                await self.crawl_page_(url, crawl_depth + 1)


class UniqueURL:

    def __init__(self, url, references, timestamp):
        self.url = url
        self.references = references
        self.timestamp = timestamp

    def __key(self):
        return (self.url,)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, UniqueURL):
            return self.__key() == other.__key()
        else:
            return NotImplemented

    def __repr__(self):
        return f"UniqueURL {self.url} {self.references} {self.timestamp}"

    def to_list(self):
        return [
            self.url,
            self.references,
            self.timestamp,
        ]
