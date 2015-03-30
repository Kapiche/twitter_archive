from __future__ import absolute_import
import csv
import shutil
from django.conf import settings

from celery import Celery
from celery.utils.log import get_task_logger
from twython import Twython

from twitter_archive import creds
from twitter_archive.models import TwitterSearch

app = Celery(broker='amqp://')
logger = get_task_logger(__name__)


@app.task
def delete_tweets(path):
    shutil.rmtree(path, ignore_errors=True)


@app.task
def collect_tweets():
    for search in TwitterSearch.objects.filter(active=True):
        user = search.user
        twitter = Twython(
            creds.APP_KEY,
            creds.APP_SECRET,
            user.twitterprofile.oauth_token,
            user.twitterprofile.oauth_secret,
        )
        # Run the search
        result = twitter.search(
            q=search.query,
            result_type=search.type,
            lang='en',
            count=100 if settings.MAX_TWEETS - search.collected > 100 else settings.MAX_TWEETS - search.collected,
            since_id=search.last_tweet_id,
        )

        # Write the tweets
        with open(search.csv_path, 'a') as out:
            writer = csv.writer(out)
            for tweet in result['statuses']:
                user = tweet.get('user', {})
                writer.writerow([
                    tweet.get('created_at', '').encode('utf-8'),
                    tweet.get('id_str', '').encode('utf-8'),
                    tweet.get('in_reply_to_user_id_str', ''),
                    tweet.get('retweet_count', 0),
                    user.get('name', '').encode('utf-8'),
                    user.get('profile_image_url', '').encode('utf-8'),
                    user.get('location', '').encode('utf-8'),
                    tweet.get('coordinates', ''),
                    tweet.get('text', '').encode('utf-8'),
                ])

        # Save stats
        search.last_tweet_id = result['search_metadata']['max_id_str']
        search.collected += len(result['statuses'])
        if search.collected >= settings.MAX_TWEETS:
            search.active = False
        search.save()
