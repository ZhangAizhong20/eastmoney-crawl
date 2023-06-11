import scrapy


class MyspiderSpider(scrapy.Spider):
    name = "myspider"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com/"]

    def parse(self, response):
        pass
