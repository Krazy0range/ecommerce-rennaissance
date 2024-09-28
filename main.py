from crawler import Crawler


def init_crawler(url, store):
    return Crawler(
        url,
        f"database/{store}_urls.csv",
        0,
        debug=False,
    )


if __name__ == "__main__":

    # walmart_crawler = init_crawler("www.walmart.com", "walmart")
    # walmart_crawler.crawl()

    costco_crawler = init_crawler("www.costco.com", "costco")
    costco_crawler.crawl()
