#scrapy crawl newhavencrawler -o output.json
#scrapy crawl newhavencrawler -o rag_data.json

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
