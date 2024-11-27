from django.db import models
from django.contrib import admin
import uuid
from django.utils.html import format_html
import re


class Event(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    event_id = models.CharField(max_length=255, editable=False, unique=True)
    title = models.CharField(max_length=255)
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    venue_details = models.JSONField(blank=True, default=dict)
    url = models.CharField(max_length=1024, blank=True, null=True)

    list_display = ('title', 'date_time_start')
    search_fields = ['title']

    def __str__(self):
        return self.title

    @classmethod
    def from_item(cls, item):
        return cls(
            name=item['name'],
            date=item['date'],
            description=item['description'],
        )


def easy_url(url):
    return re.sub(r'https://www\.|http://www\.|https://www|http://|https://|www\.', "",
                  url).strip('/')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title",
                    'visit_url',
                    "date_time_start", "date_time_end",
                    # 'updated_at',
                    )
    ordering = ['-date_time_start']

    fields = ['title', 'url', ('date_time_start', 'date_time_end'),
              'description', 'venue_details']

    @admin.display(description='URL', ordering='url')
    def visit_url(self, obj):
        return format_html('<a href="{0}" target="_blank">{1}</a>', obj.url, easy_url(obj.url))
