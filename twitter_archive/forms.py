# Author: Ryan Stuart <ryan@kapiche.com>
from django.forms import ModelForm
from twitter_archive.models import TwitterSearch


class SearchForm(ModelForm):
    class Meta:
        model = TwitterSearch
        fields = ['query', 'type', ]
