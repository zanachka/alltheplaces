import scrapy
import re
from locations.items import GeojsonPointItem

DAY_MAPPING = {
    'M': 'Mo',
    'T': 'Tu',
    'W': 'We',
    'F': 'Fr',
    'Sat': 'Sa',
    'Sun': 'Su'
}


class MarksSpencerSpider(scrapy.Spider):

    name = "marksandspencer"
    allowed_domains = ["www.marksandspencer.com"]
    download_delay = 0
    start_urls = (
        'https://www.marksandspencer.com/s/store-listing',
    )

    def parse_day(self, day):

        if re.search('Sat', day) or re.search('Sun', day):
            return DAY_MAPPING[day.strip()]

        if re.search('-', day):
            days = day.split('-')
            osm_days = []
            if len(days) == 2:
                for day in days:
                    osm_day = DAY_MAPPING[day.strip()]
                    osm_days.append(osm_day)
            return "-".join(osm_days)

    def parse_times(self, times):
        if times.strip() == 'Open 24 hours':
            return '24/7'
        hours_to = [x.strip() for x in times.split('-')]
        cleaned_times = []

        for hour in hours_to:
            if re.search('PM$', hour):
                hour = re.sub('PM', '', hour).strip()
                hour_min = hour.split(":")
                if int(hour_min[0]) < 12:
                    hour_min[0] = str(12 + int(hour_min[0]))
                cleaned_times.append(":".join(hour_min))

            if re.search('AM$', hour):
                hour = re.sub('AM', '', hour).strip()
                hour_min = hour.split(":")
                if len(hour_min[0]) <2:
                    hour_min[0] = hour_min[0].zfill(2)
                else:
                    hour_min[0] = str(12 + int(hour_min[0]))

                cleaned_times.append(":".join(hour_min))
        return "-".join(cleaned_times)

    def parse_hours(self, lis):
        hours = []
        for li in lis:
            day = li.xpath('normalize-space(.//span[@class="day single-day"]/text() | .//span[@class="day"]/text())').extract_first()
            times = li.xpath('.//span[@class="timings"]/text()').extract_first()
            if times and day:
                parsed_time = self.parse_times(times)
                parsed_day = self.parse_day(day)
                hours.append(parsed_day + ' ' + parsed_time)

        return "; ".join(hours)

    def parse_stores(self, response):
        properties = {
            'addr_full': response.xpath('normalize-space(//li[@class="address"]/p[1]/text())').extract_first().split(',')[1],
            'phone': response.xpath('normalize-space(//div[@class="scroll-area"]/ul/li[2]/text())').extract_first(),
            'city': response.xpath('normalize-space(//li[@class="address"]/p[1]/text())').extract_first().split(',')[2],
            'state': '',
            'country':'United Kingdom',
            'postcode': response.xpath('normalize-space(//li[@class="address"]/p[1]/text())').extract_first().split(',')[3],
            'ref': re.findall(r"[0-9]+$" ,response.url)[0],
            'website': response.url,
            'lat':'',
            'lon': '',
        }

        hours = self.parse_hours(response.xpath('//ul[@class="cleanList srHours srSection"]/li'))
        if hours:
            properties['opening_hours'] = hours

        yield GeojsonPointItem(**properties)
    def parse(self, response):
        urls = response.xpath('//div[@class="content"]/ul/li/a/@href').extract()
        print(urls)
        for path in urls:
            yield scrapy.Request(response.urljoin(path), callback=self.parse_stores)
