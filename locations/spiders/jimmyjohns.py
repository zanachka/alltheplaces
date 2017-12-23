# -*- coding: utf-8 -*-
import json
import scrapy

from locations.items import GeojsonPointItem


class JimmyjohnsSpider(scrapy.Spider):
	name = "jimmyjohns"
	allowed_domains = ["www.jimmyjohns.com"]
	start_urls = (
		'https://www.jimmyjohns.com/find-a-jjs/',
	)
	download_delay = 1.5

	def parse(self, response):
		# states = response.css('select#drpdwnState > option ::text').extract()
		# print states[1]
		for state in response.css('select#drpdwnState > option ::text').extract():
			if state<>'' or state<>'Select State':
				print state
				yield scrapy.FormRequest.from_response(
					# 'https://www.jimmyjohns.com/webservices/Location/LocationServiceHandler.asmx/GetCitiesByStateNameAbbreviation',
					'https://www.jimmyjohns.com/find-a-jjs/#/'+state+'/55555',
					formdata={
						'state': state,
						'__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first()
					},
					callback=self.parse_storesbycity
				)

			
	def parse_storesbycity(self,response):
		for city in response.css('select#citySelect > option ::attr(value)').extract():
			yield scrapy.y.FormRequest.from_response(
				'https://www.jimmyjohns.com/find-a-jjs/#/'+state+'/'+city,
				response,
				formdata={
					'city': city,
					'__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first(),
				},
				callback=self.parse_results
			)
			
	def parse_results(self,response):
		for storeInfo in response.css("p.storeInfo"):
			yield GeojsonPointItem(
				ref='1',
				# lat=float(item.get('latitude')),
				# lon=float(item.get('longitude')),
				# addr_full=item.get('address'),
				# city=item.get('city'),
				# state=item.get('state'),
				# postcode=item.get('zip'),
				# website='https://www.superonefoods.com/store-details/'+item.get('url'),
			)
