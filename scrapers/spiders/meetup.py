from typing import Any

import scrapy
# from scrapy import Request, RequestException
from scrapy.http import Request, Response
from urllib.parse import urlencode
from json import loads, load, dumps

from scrapers.items import Event


class MeetupSpider(scrapy.Spider):
    name = "meetup"
    allowed_domains = ["meetup.com"]
    start_urls = []

    def __init__(self, *args, **kwargs):
        start_urls = kwargs.pop('start_urls', [])
        if start_urls:
            self.start_urls = start_urls.split(',')
        self.logger.info("Start urls are {}".format(self.start_urls))
        super(MeetupSpider, self).__init__(*args, **kwargs)

    def parse(self, response: Response, **kwargs: Any):
        return [
            scrapy.Request(url="{}?{}".format(response.url, urlencode({
                'type': 'upcoming',
            })), callback=self.parse_per_timeline),
            scrapy.Request(url="{}?{}".format(response.url, urlencode({
                'type': 'past',
            })), callback=self.parse_per_timeline),
        ]

    def parse_per_timeline(self, response: Response):
        self.logger.info("Parsing per timeline {}".format(response.url))
        json_data = loads(response.css("script#__NEXT_DATA__::text").extract_first())
        apollo_state = json_data.get('props').get('pageProps').get('__APOLLO_STATE__')

        venues = {venue.get('id'): {
            'id': "meetup_venue::{}".format(venue.get('id')),
            'name': venue.get('name'),
            'address': venue.get('address'),
            'city': venue.get('city'),
            'state': venue.get('state'),
            'country': venue.get('country'),
        } for venue in apollo_state.values() if venue.get('__typename') == 'Venue'}

        events = [{
            'id': "meetup::{}".format(event.get('id')),
            'url': event.get('eventUrl'),
            'title': event.get('title'),
            'description': event.get('description'),
            'date_time_start': event.get('dateTime'),
            'date_time_end': event.get('endTime'),
            'created_at': event.get('createdTime'),
            'venue_details':
                venues.get(event.get('venue').get('__ref').replace('Venue:', ' ').strip()),
            # Use this for debugging
            # 'original_event': event
        } for event in apollo_state.values() if event.get('__typename') == 'Event']

        # This could be helpful for debugging.
        # print(dumps(venues, indent=4, ensure_ascii=False))
        # print(dumps(events, indent=4, ensure_ascii=False))

        return [Event(event_dict) for event_dict in events]
