import re
from datetime import datetime

from scrapy.http import JsonRequest

from locations.hours import DAYS_FULL, OpeningHours
from locations.items import SocialMedia, set_social_media
from locations.json_blob_spider import JSONBlobSpider

millisecond_date = re.compile(r"/Date\((\d+)\)/")
mdy_date = re.compile(r"(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)")
iso_date = re.compile(r"(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)T(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)")


class CaliberCollisionUSSpider(JSONBlobSpider):
    name = "caliber_collision_us"
    item_attributes = {"brand": "Caliber Collision", "brand_wikidata": "Q109329782"}
    download_timeout = 30
    locations_key = "contentlets"

    def start_requests(self):
        data = {"size": 100000, "query": {"bool": {"must": {"query_string": {"query": "+contentType:Center"}}}}}
        yield JsonRequest("https://www.caliber.com/api/es/search", data=data)

    def post_process_item(self, item, response, location):
        item["branch"] = location["title"]
        item["extras"]["fax"] = location.get("faxNumber")
        if "zip" in location:
            item["postcode"] = str(location["zip"])
        item["state"] = location.get("state")
        set_social_media(item, SocialMedia.YELP, location.get("yelpUrl"))

        if "metaTitle" in location and "|" in location["metaTitle"]:
            item["name"] = location["metaTitle"].split("|")[1].strip()
        else:
            del item["name"]

        oh = OpeningHours()
        for day in map(str.lower, DAYS_FULL):
            if location.get(f"{day}HoursClose") == location.get(f"{day}HoursOpen") == "1970-01-01 00:00:00.0":
                oh.set_closed(day)
            else:
                oh.add_range(
                    day,
                    location.get(f"{day}HoursClose"),
                    location.get(f"{day}HoursOpen"),
                    time_format="%Y-%m-%d %H:%M:%S.0",
                )
        item["opening_hours"] = oh

        if date_str := location.get("openDate"):
            if match := millisecond_date.match(date_str):
                start_date = datetime.fromtimestamp(int(match.group(1)) / 1000)
            elif (match := mdy_date.match(date_str)) or (match := iso_date.match(date_str)):
                start_date = datetime(**{k: int(v) for k, v in match.groupdict().items()})
            else:
                self.logger.info(f"Unknown date format {date_str!r}")
                start_date = None
            if start_date is not None:
                item["extras"]["start_date"] = start_date.strftime("%Y-%m-%d")

        if path := location.get("urlMap"):
            item["website"] = response.urljoin(path)
        else:
            del item["website"]

        yield item
