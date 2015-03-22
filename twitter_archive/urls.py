from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from twitter_archive import views

urlpatterns = patterns('',
    # Static
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),

    # Dynamic
    url(r'^login/$', views.twitter_login, name='login'),
    url(r'^callback/$', views.callback, name='callback'),
    url(r'^account/$', views.account, name='account'),
    url(r'^new_search/$', views.new_search, name='new_search'),
    url(r'^delete_search/(\d+)/$', views.delete_search, name='delete_search'),
    url(r'^download_search/(\d+)/$', views.download_search, name='download_search'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
)
