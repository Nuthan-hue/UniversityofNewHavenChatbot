import scrapy

class MyspiderSpider(scrapy.Spider):
    name = 'myspider'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com/']

    def parse(self, response):
        # Extract data using CSS selectors or XPath
        for title in response.css('h1::text'):
            yield {'title': title.get(),
                   }  # Yields extracted data
