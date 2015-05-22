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

urlpatterns = [

    #Management
	url(r'^manage/$', views.IndexView.as_view(), name='listhosts'),
	#url(r'^manage/(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^manage/(?P<host_id>[0-9]+)/$', views.managehost, name='managehost'),
    url(r'^manage/add/$', views.managehost, name='managehost'),
    url(r'^manage/scan/(?P<host_id>[0-9]+)/$', views.scanhost, name='scanhost'),
    url(r'^manage/delete/(?P<host_id>[0-9]+)/$', views.deletehost, name='deletehost'),
    #url(r'^manage/addmultiple/$', views.addhosts, name='addhosts'),

    #Dashboard
    url(r'^$', views.dashboard, name='dashboard'),
    #url(r'^(?P<p_account_id>[0-9]+)/$', views.dashboard, name='dashboard')
    #url(r'^(?P<p_account_id>[0-9]+)/(?P<p_grade>[0-9]+)$', views.dashboard, name='dashboard')

]
