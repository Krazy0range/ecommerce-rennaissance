from crawler import Crawler

if __name__ == "__main__":

    crawler = Crawler(
        "www.walmart.com",
        "database/urls.csv",
        0,
        debug=False,
    )
    crawler.crawl()
