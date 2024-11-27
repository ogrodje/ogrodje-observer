from enum import Enum


class ObserverTopics(Enum):
    Scrapes = "scrapes-dev-1"  # This is the topic for scraper work
    CollectedItems = "collected-items-dev-1"  # This is the topic for items that ware collected

