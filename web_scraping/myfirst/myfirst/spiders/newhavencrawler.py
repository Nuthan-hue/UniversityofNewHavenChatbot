#scrapy crawl newhavencrawler -o output.json

'''from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class NewhavenSpider(CrawlSpider):
    name = "newhavencrawler"
    allowed_domains = ["newhaven.edu"]
    start_urls = ["https://www.newhaven.edu/admissions/index.php"]

    rules = [
        Rule(LinkExtractor(allow=r'/admissions/.*'), callback='parse_admissions', follow=True)
    ]

    def parse_admissions(self, response):
        title = response.css('title::text').get()
        paragraphs = response.css('p::text').getall()
        content = ' '.join(paragraphs)
        yield {"url": response.url, "title": title, "content": content}
'''
# -*- coding: utf-8 -*-


'''import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
import logging


class NewhavenSpider(CrawlSpider):
    name = "newhavencrawler"
    allowed_domains = ["newhaven.edu"]
    start_urls = ["https://www.newhaven.edu/admissions/index.php"]

    # Keep track of unique content
    seen_content = set()

    # Define rules to extract links from /admissions/ section
    rules = [
        Rule(LinkExtractor(allow=r'/admissions/.*'), callback='parse_admissions', follow=True)
    ]

    def parse_admissions(self, response):
        # Extract page title
        title = response.css('title::text').get()

        # Extract content from <p> tags
        paragraphs = response.css('p::text').getall()
        content = ' '.join(paragraphs).strip()

        # Step 1: Filter Duplicate Content
        if content in self.seen_content:
            logging.info(f"Duplicate content skipped for URL: {response.url}")
            return

        # Add unique content to the seen set
        self.seen_content.add(content)

        # Step 2: Remove Unwanted Sentences
        blacklist = [
            "The campus visit is one of the most important parts of your college selection process."
        ]
        for sentence in blacklist:
            content = content.replace(sentence, "").strip()

        # Step 3: Clean Up Excessive Whitespace
        content = re.sub(r'\s+', ' ', content)

        # Log processed URL and a sample of its content for debugging
        logging.info(f"Processed URL: {response.url}")
        logging.info(f"Content Preview: {content[:100]}...")  # Log first 100 characters

        # Yield the cleaned and processed data
        yield {
            "url": response.url,
            "title": title,
            "content": content
        }'''

# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re

class NewhavenSpider(CrawlSpider):
    name = "newhavencrawler"
    allowed_domains = ["newhaven.edu"]
    start_urls = ["https://www.newhaven.edu/admissions/index.php"]

    # Track duplicate content
    seen_content = set()

    rules = [
        Rule(LinkExtractor(allow=r'/admissions/.*'), callback='parse_admissions', follow=True)
    ]

    def parse_admissions(self, response):
        # Extract page title and URL to use as metadata
        title = response.css('title::text').get()
        url = response.url

        # Extract content from <p> tags
        paragraphs = response.css('p::text').getall()
        content = ' '.join(paragraphs).strip()

        # Remove duplicates
        if content in self.seen_content:
            return
        self.seen_content.add(content)

        # Remove repetitive patterns
        patterns = [
            r"campus visit.*?college selection process",
            r"visit our campus.*?learn more",
            r"annual security.*?fire safety report"
        ]
        for pattern in patterns:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE).strip()

        # Split content into chunks
        chunks = self.chunk_text(content, chunk_size=500)

        # Yield each chunk with metadata
        for chunk in chunks:
            yield {
                "text": chunk,
                "metadata": {
                    "heading": title,
                    "url": url
                }
            }

    def chunk_text(self, text, chunk_size=500):
        """Split text into smaller chunks of specified size."""
        words = text.split()
        for i in range(0, len(words), chunk_size):
            yield ' '.join(words[i:i + chunk_size])
