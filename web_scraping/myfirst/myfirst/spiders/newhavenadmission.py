# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor

class NewhavenadmissionSpider(scrapy.Spider):
    name = "newhavenadmission"
    allowed_domains = ["newhaven.edu"]
    start_urls = ["https://www.newhaven.edu/admissions/index.php"]

    def parse(self, response):
        # Follow links within /admissions/
        link_extractor = LinkExtractor(allow=r'/admissions/.*')
        links = link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(link.url, callback=self.parse_info)

    def parse_info(self, response):
        # Extract and clean data
        title = response.css('title::text').get()
        paragraphs = response.css('p::text').getall()
        content = ' '.join(paragraphs)
        content = re.sub(r'\s+', ' ', content).strip()  # Clean whitespace

        # Yield the extracted data
        yield {
            "title": title,
            "content": content,
            "url": response.url  # Optional: add the URL for reference
        }
