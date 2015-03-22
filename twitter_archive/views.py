# Author: Ryan Stuart <ryan@kapiche.com>
import csv
import os
import shutil
import uuid
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, StreamingHttpResponse
from django.shortcuts import render, redirect
from twython import Twython

from twitter_archive import creds, tasks
from twitter_archive.forms import SearchForm
from twitter_archive.models import TwitterProfile, TwitterSearch


def twitter_login(request):
    if request.method == 'GET':
        twitter = Twython(creds.APP_KEY, creds.APP_SECRET)
        auth = twitter.get_authentication_tokens(callback_url='http://127.0.0.1:8000/callback')
        request.session['oauth_token'] = auth['oauth_token']
        request.session['oauth_token_secret'] = auth['oauth_token_secret']

        return render(request, 'login.html', {'twitter_url': auth['auth_url']})


def account(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    if request.method == 'GET':
        twitter = Twython(
            creds.APP_KEY,
            creds.APP_SECRET,
            request.user.twitterprofile.oauth_token,
            request.user.twitterprofile.oauth_secret
        )
        tasks.collect_tweets()
        return render(request, 'account.html', {
            'searches': TwitterSearch.objects.filter(user=request.user),
            'max_tweets': settings.MAX_TWEETS,
            'max_searches': settings.MAX_SEARCHES
        })


def callback(request):
    if request.method == 'GET':
        oauth_verifier = request.GET['oauth_verifier']
        twitter = Twython(
            creds.APP_KEY,
            creds.APP_SECRET,
            request.session['oauth_token'],
            request.session['oauth_token_secret']
        )
        final_step = twitter.get_authorized_tokens(oauth_verifier)
        request.session['oauth_token'] = final_step['oauth_token']
        request.session['oauth_token_secret'] = final_step['oauth_token_secret']

        try:
            User.objects.get(username=final_step['screen_name'])
        except ObjectDoesNotExist:
            user = User.objects.create_user(final_step['screen_name'], "this@is.crap", final_step['oauth_token_secret'])
            profile = TwitterProfile()
            profile.user = user
            profile.oauth_token = final_step['oauth_token']
            profile.oauth_secret = final_step['oauth_token_secret']
            profile.save()
        finally:
            user = authenticate(
                username=final_step['screen_name'],
                password=final_step['oauth_token_secret']
            )
            login(request, user)

        return redirect(reverse(account))


def new_search(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    if request.method == 'GET':
        form = SearchForm()
        return render(request, 'new_search.html', {'form': form})
    elif request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.save(commit=False)
            search.user = request.user
            path = os.path.join(
                settings.CSV_STORAGE_DIR,
                '{}-{}.csv'.format(
                    request.user.username,
                    uuid.uuid4()
                )
            )
            with open(path, 'w+') as out:  # Create the file
                writer = csv.writer(out)
                writer.writerow([
                    'created_at', 'id_str', 'in_reply_to_user_id_str', 'retweet_count', 'user_name'
                    'user_profile_image_url', 'user_location', 'coordinates', 'text'
                ])
            search.csv_path = path
            search.save()
            return redirect(reverse(account))
        return render(request, 'new_search.html', {'form': form})


def delete_search(request, search_id):
    search = TwitterSearch.objects.get(pk=search_id)
    shutil.rmtree(search.csv_path, ignore_errors=True)
    search.delete()
    return redirect(reverse(account))


def download_search(request, search_id):
    search = TwitterSearch.objects.get(pk=search_id)
    path = search.csv_path
    # Create a new csv for this search. Downloading clears all tweets.
    search.active = True
    search.collected = 0
    search.csv_path = os.path.join(
        settings.CSV_STORAGE_DIR,
        '{}-{}.csv'.format(
            request.user.username,
            uuid.uuid4()
        )
    )
    with open(search.csv_path, 'w+') as out:  # Create the file
        writer = csv.writer(out)
        writer.writerow([
            'created_at', 'id_str', 'in_reply_to_user_id_str', 'retweet_count', 'user_name'
            'user_profile_image_url', 'user_location', 'coordinates', 'text'
        ])
    search.save()

    # Stream back the file
    with open(path, 'Ur') as f:
        tasks.delete_tweets.apply_async(countdown=60*10, args=[path])
        return StreamingHttpResponse(f.readlines(), content_type="text/csv")
