import json
import os
import sys
from datetime import datetime

from confluent_kafka import Producer

from scrapers import ObserverTopics

sys.path.insert(0, '../../ogrodje_observer')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ogrodje_observer.settings'

from scrapers.clients import Meetups, Source


class ScraperCommand(object):
    kind: str = None


class CollectSource(ScraperCommand):
    def __init__(self, kind: str, url: str, source: Source):
        self.kind = "collect_source"
        self.source_kind = kind
        self.url = url
        self.source = source
        self.created_at = datetime.now().isoformat()


def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def main():
    producer = Producer({
        'bootstrap.servers': os.environ.get('BOOTSTRAPSERVERS', default='127.0.0.1:9094'),
    })

    commands = [
        CollectSource(source.kind, source.url, source)
        for meetup in Meetups.all_meetups()
        for source in meetup.source_links
    ]

    for command in commands:
        message = json.dumps(command, default=lambda o: o.__dict__).encode('utf-8')
        producer.poll(0)
        producer.produce(ObserverTopics.Scrapes.value, message, callback=delivery_report)

    producer.flush()


if __name__ == "__main__":
    main()
