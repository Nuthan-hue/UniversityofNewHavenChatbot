# -*- coding: utf-8 -*-

## Command to execute this code: scrapy runspider newhaven.py -o output.json

import scrapy

class NewhavenSpider(scrapy.Spider):
    name = "newhaven"
    start_urls = ["https://www.newhaven.edu/admissions/index.php"]

    def parse(self, response):
        # Define the sections and their respective XPath details
        sections = [
            {
                "name": "spotlights",
                "section_xpath": '//section[@class="spotlights"]/*',
                "heading_xpath": './/h3[@class="label"]/text()',
                "body_xpath": './/p/text()'
            },
            {
                "name": "admissions-info",
                "section_xpath": '//*[@class="involvement-preview"]',
                "heading_xpath": './/*[@class="article-title"]/text()',
                "body_xpath": './/*[@class="article-desc"]/text()'
            }
            # Add more sections as needed
        ]

        # Loop through each defined section
        for section in sections:
            for element in response.xpath(section["section_xpath"]):
                # Extract heading and body using the specified XPaths
                heading = element.xpath(section["heading_xpath"]).get()
                body = element.xpath(section["body_xpath"]).get()

                if heading and body:
                    # Clean up the extracted text
                    clean_heading = heading.replace("\n", "").replace("\t", "").strip()
                    clean_body = body.replace("\n", "").replace("\t", "").strip()

                    # Yield the extracted data with metadata
                    yield {
                        "text": f"{clean_heading}: {clean_body}",
                        "metadata": {
                            "heading": clean_heading,
                            "section": section["name"]
                        }
                    }
