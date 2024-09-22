import asyncio
import bs4
import nodriver
import time
import tldextract

from database import Database


class Crawler:

    def __init__(self, main_url, urls_db_path, max_crawl_depth, debug=False):
        self.main_url = main_url
        parsed_url = tldextract.extract(self.main_url)
        self.domain = parsed_url.domain

        self.urls_db = Database(urls_db_path)
        self.max_crawl_depth = max_crawl_depth
        self.debug = debug

    def add_url_reference(self, url_i):
        self.urls_db.data[url_i][1] += 1

    def deduplicate_urls(self, urls):
        result_urls = set(urls)
        for row_i, row in enumerate(self.urls_db.data):
            url = row[0]
            if url in result_urls:
                result_urls.remove(url)
                self.add_url_reference(row_i)
                if self.debug:
                    print("\x1b[31mduplicate url\x1b[0m", url)
        return list(result_urls)

    def crawl(self):
        self.urls_db.read_data(just_headers=True)
        asyncio.run(self.crawl_())
        print("\x1b[1;32mwriting url data\x1b[0m")
        self.urls_db.write_data()

    async def crawl_(self):
        self.driver = await nodriver.start()
        await self.crawl_page_("https://" + self.main_url, 0)
        self.driver.stop()

    async def crawl_page_(self, page_url, crawl_depth):
        page = await self.driver.get(page_url)
        page_content = await page.get_content()
        soup = bs4.BeautifulSoup(page_content, "html.parser")
        soup_links = soup.find_all("a", href=True)
        pending_urls = []

        for soup_link in soup_links:
            link_href = soup_link["href"]
            pending_urls.append(link_href)

        pending_urls = self.deduplicate_urls(pending_urls)
        for pending_url in pending_urls:
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
            self.urls_db.data.append([url, 0, timestamp])

            if crawl_depth < self.max_crawl_depth:
                await self.crawl_page_(url, crawl_depth + 1)
