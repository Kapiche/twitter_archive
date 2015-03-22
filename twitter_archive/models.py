# Copyright (c) 2012-2014 Kapiche Limited
# Author: Ryan Stuart <ryan@kapiche.com>
from django.conf import settings
from django.db import models


class TwitterProfile(models.Model):
    """Profile model that handles storing the oauth_token and oauth_secret in relation to a user."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)


class TwitterSearch(models.Model):
    TYPES = (
        ("recent", "recent",),
        ("popular", "popular",),
        ("mixed", "mixed",),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    query = models.CharField(max_length=255)
    type = models.CharField(max_length=100, choices=TYPES)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=True)
    collected = models.IntegerField(default=0)
    last_tweet_id = models.CharField(max_length=255, blank=True, default='')
    csv_path = models.CharField(max_length=512)
