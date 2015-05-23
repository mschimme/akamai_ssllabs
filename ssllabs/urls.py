"""ssllabs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import url
from . import views
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

urlpatterns = [

    #Auth and logout
    url(r'^auth/$', views.auth, name='auth'),
    url(r'^logout/$', views.logout_view, name='logout_view'),

    #Management
	url(r'^manage/$', login_required(views.IndexView.as_view()), name='listhosts'),
    url(r'^manage/(?P<host_id>[0-9]+)/$', views.managehost, name='managehost'),
    url(r'^manage/add/$', views.managehost, name='managehost'),
    url(r'^manage/scan/(?P<host_id>[0-9]+)/$', views.scanhost, name='scanhost'),
    url(r'^manage/delete/(?P<host_id>[0-9]+)/$', views.deletehost, name='deletehost'),

    #Dashboard
    url(r'^$', views.dashboard, name='dashboard'),

]
