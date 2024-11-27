import os, logging, signal, sys
from json import loads
from confluent_kafka import Consumer
from scrapers.start_collection import ObserverTopics

sys.path.insert(0, '../../ogrodje_observer')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ogrodje_observer.settings'
os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapers.settings'

import django
from django.conf import settings

django.setup()

from pub_events.models import Event as EventModel


class Persistor(object):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    consumer: Consumer

    def __init__(self, extra_consumer_options=None):
        if extra_consumer_options is None:
            extra_consumer_options = {}
        self.consumer = Consumer(
            {
                'bootstrap.servers': self.get_kafka_brokers(),
                'group.id': 'persistors',
                # 'auto.offset.reset': 'beginning',
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': 'true',
                'auto.commit.interval.ms': 1000,
                'session.timeout.ms': 6000
            } | extra_consumer_options)

    def get_kafka_brokers(self) -> str:
        return os.environ.get('BOOTSTRAPSERVERS', default='127.0.0.1:9094')

    def listen_for_events(self):
        self.consumer.subscribe([ObserverTopics.CollectedItems.value])
        try:
            while True:
                message = self.consumer.poll(timeout=1.0)
                if message is None:
                    continue
                if message.error():
                    print("💥 Kafka error: {}".format(message.error()))
                    continue

                item = loads(message.value().decode('utf-8'))
                self.persist_item(item)
        except Exception as ex:
            print(ex)
            self.consumer.close()
        finally:
            self.consumer.close()

    def shutdown(self, signum, frame):
        self.logger.info("Stopping. {} w/ {}".format(signum, frame))
        self.consumer.close()

    def persist_item(self, item):
        print("persisting {}".format(item))
        EventModel.objects.update_or_create(
            event_id=item['id'],
            defaults={
                'title': item['title'],
                'url': item['url'],
                'date_time_start': item['date_time_start'],
                'date_time_end': item['date_time_end'],
                'description': item['description'],
                'created_at': item['created_at'],
                'venue_details': item['venue_details']
            }
        )


if __name__ == '__main__':
    persistor = Persistor()
    signal.signal(signal.SIGINT, persistor.shutdown)
    persistor.listen_for_events()
