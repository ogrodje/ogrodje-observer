# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field


class Event(Item):
    id = Field()
    url = Field()
    title = Field()
    description = Field()
    date_time_start = Field()
    date_time_end = Field()
    created_at = Field()
    venue_details = Field()
