from confluent_kafka import Consumer, Producer, KafkaError
import os, json


class KafkaItemsPipeline:
    _shared_state = {}  # Borg pattern shared state

    def __init__(self, kafka_broker=None, kafka_topic=None, kafka_settings={}):
        self.__dict__ = self._shared_state  # Assign instance dict to shared state
        if not hasattr(self, 'initialized'):
            self.kafka_broker = kafka_broker
            self.kafka_topic = kafka_topic
            self.kafka_settings = kafka_settings
            self.producer = None
            self.initialized = True

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            kafka_broker=crawler.settings.get("BOOTSTRAPSERVERS", "127.0.0.1:9094"),
            kafka_topic=crawler.settings.get("KAFKA_ITEMS_TOPIC"),
            kafka_settings=crawler.settings.get("KAFKA_ITEMS_SETTINGS", {})
        )

    def delivery_report(self, error, message):
        if error is not None:
            print('Message delivery failed: {}'.format(error))
        else:
            print('Message delivered to {} [{}]'.format(message.topic(), message.partition()))

    def open_spider(self, spider):
        if self.producer is None:
            print("🔥 Opening spider here {}".format(spider.name))
            self.producer = Producer(
                {
                    'bootstrap.servers': os.environ.get('BOOTSTRAPSERVERS', self.kafka_broker),
                } | self.kafka_settings)

    def close_spider(self, spider):
        if self.producer is not None:
            print("🔥 Flushing here. {}".format(spider.name))
            self.producer.flush()
            self.producer = None

    def process_item(self, item, _spider):
        if self.producer is not None:
            self.producer.poll(0)
            message = json.dumps(dict(item), ensure_ascii=False, indent=0)
            self.producer.produce(self.kafka_topic, message, callback=self.delivery_report)
            return item
