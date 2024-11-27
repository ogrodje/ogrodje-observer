import json

import requests
import os


class HyGraphClient(object):
    def __init__(self, url: str | None = None):
        if url is None or '':
            self.url = os.environ.get('HYGRAPH_ENDPOINT')
        else:
            self.url = url

        if self.url is None:
            raise Exception("HYGRAPH_ENDPOINT not set")

    def get(self):
        return requests.get(self.url).json()

    def query(self, raw_query: str, variables: dict):
        response = requests.post(self.url, json={
            'query': raw_query.replace('\n', ' '),
            'variables': variables
        }, headers={
            'Accept': 'application/json',
        })

        response.raise_for_status()
        return response.json().get('data')


class Source(object):
    def __init__(self, kind: str, url: str):
        self.kind = kind.capitalize()
        self.url = url

    @staticmethod
    def from_url(key: str, value: str):
        return Source(key.replace("Url", ""), value)

    @staticmethod
    def from_meetup(meetup_dict: dict):
        return [Source.from_url(key, value) for (key, value) in meetup_dict.items() if
                key.endswith("Url") and value is not None]


class Meetup:
    def __init__(self,
                 hygraph_id: str,
                 name: str,
                 source_links: list[Source]):
        self.hygraph_id = hygraph_id
        self.name = name
        self.source_links = source_links

    @staticmethod
    def from_graph(meetup_dict: dict):
        return Meetup(
            meetup_dict.get('id'),
            meetup_dict.get('name'),
            Source.from_meetup(meetup_dict))


class Meetups(HyGraphClient):
    def all(self):
        return [Meetup.from_graph(meetup) for meetup in self.query("""
            query AllMeetups($size: Int) {
                meetups(first: $size) { 
                    id
                    name
                    homePageUrl 
                    meetupUrl 
                    discordUrl 
                    linkedInUrl 
                    kompotUrl
                    icalUrl
                }
            }
            """, {
            'size': 1000
        }).get('meetups')]

    @staticmethod
    def all_meetups() -> list[Meetup]:
        return Meetups().all()


if __name__ == '__main__':
    for meetup in Meetups().all():
        print(json.dumps(meetup, default=lambda o: o.__dict__, indent=2))
