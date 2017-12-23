import json, re, scrapy, logging
from locations.items import GeojsonPointItem

class KarstadtSpider(scrapy.Spider):
    name = "karstadt"
    allowed_domains = ["karstadt.de"]

    def start_requests(self):
        url = 'https://www.karstadt.de/filialfinder?dwcont=C1131381089' 
        body = {
            'dwfrm_storelocator_countryCode': 'DE',
            'dwfrm_storelocator_distanceUnit': 'km',
            'dwfrm_storelocator_postalCode': '10115',
            'dwfrm_storelocator_findbyzip': 'Suchen',
            'dwfrm_storelocator_maxdistance': '100%2C00'
        }
        headers = {
            'origin': 'https://www.karstadt.de',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'cache-control': 'max-age=0',
            #'authority': 'www.karstadt.de',
            'referer': 'https://www.karstadt.de/filialfinder?dwcont=C1131032283',
        }
        yield scrapy.http.FormRequest(
            url=url, 
            method='POST', 
            #body=body,
            formdata=body,
            headers=headers, 
            callback=self.parse
        )

    def parse(self, response):
        logging.info(response.body_as_unicode())
