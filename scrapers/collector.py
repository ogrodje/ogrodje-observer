import os
import signal
from json import loads

from confluent_kafka import Consumer
from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import defer, reactor
import logging

from scrapers.spiders.meetup import MeetupSpider
from scrapers.start_collection import ObserverTopics
from scrapers import ObserverTopics

os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapers.settings'


class Collector(object):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    settings: Settings = get_project_settings()
    runner: CrawlerRunner
    consumer: Consumer

    @defer.inlineCallbacks
    def crawl_with_meetup(self, url: str):
        yield self.runner.crawl(MeetupSpider, start_urls=url)

    def schedule_meetup_crawl(self, url: str):
        reactor.callFromThread(lambda: defer.ensureDeferred(self.crawl_with_meetup(url)))

    def get_kafka_brokers(self) -> str:
        return os.environ.get('BOOTSTRAPSERVERS', default='127.0.0.1:9094')

    def __init__(self):
        self.logger.info("Initializing controller.")
        self.settings.update({
            "TWISTED_REACTOR": "twisted.internet.selectreactor.SelectReactor",
            "LOG_ENABLED": True,
            "LOG_STDOUT": True,
            "LOG_LEVEL": "INFO",
            'ITEM_PIPELINES': {'scrapers.pipelines.KafkaItemsPipeline': 300},
            'BOOTSTRAPSERVERS': self.get_kafka_brokers(),
            'KAFKA_ITEMS_TOPIC': ObserverTopics.CollectedItems.value,
            'KAFKA_ITEMS_SETTINGS': {}
        })

        configure_logging(self.settings)
        self.runner = CrawlerRunner(self.settings)

        extra_consumer_options = {}
        self.consumer = Consumer(
            {
                'bootstrap.servers': self.get_kafka_brokers(),
                'group.id': 'controllers',
                'auto.offset.reset': 'earliest',  # use this in prod
                # 'auto.offset.reset': 'latest',
                'enable.auto.commit': 'true',
                'auto.commit.interval.ms': 1000,
                'session.timeout.ms': 6000
            } | extra_consumer_options
        )

    def listen_for_events(self):
        self.consumer.subscribe([ObserverTopics.Scrapes.value])
        try:
            while True:
                message = self.consumer.poll(timeout=1.0)
                if message is None:
                    continue
                if message.error():
                    print("💥 Kafka error: {}".format(message.error()))
                    continue

                event = loads(message.value().decode('utf-8'))
                event_kind = event.get('source_kind')
                if event_kind == 'Meetup':
                    # print("Processing: {}".format(event))
                    self.schedule_meetup_crawl(event['url'])

        except Exception as e:
            self.logger.info("Closing consumer with {}".format(e))
            self.consumer.close()
        finally:
            self.consumer.close()

    def start_crawling(self):
        reactor.callInThread(self.listen_for_events)
        return reactor.run()

    def shutdown(self, signum, frame):
        self.logger.info("Stopping. {} w/ {}".format(signum, frame))
        self.consumer.close()
        reactor.stop()


if __name__ == '__main__':
    controller = Collector()
    signal.signal(signal.SIGINT, controller.shutdown)
    controller.start_crawling()
