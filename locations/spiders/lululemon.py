# -*- coding: utf-8 -*-
import scrapy


class LululemonSpider(scrapy.Spider):
    name = 'lululemon'
    allowed_domains = ['https://info.lululemon.com']
    start_urls = ['http://https://info.lululemon.com/shopLocation']

    def parse(self, response):
        urls = response.xpath('//a[@class="store-link"]').extract()
        for url in urls:
            url = url.split('href="')[1].split('">')[0]
            url = response.url + link
            yield scrapy.Request(url, callback = self.parse_store)
