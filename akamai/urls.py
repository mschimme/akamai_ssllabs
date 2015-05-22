from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse

urlpatterns = [
	url(r'^$', lambda x: HttpResponseRedirect('/ssllabs/')),
    url(r'^ssllabs/', include('ssllabs.urls', namespace="ssllabs")),
    url(r'^admin/', include(admin.site.urls)),

    #Robots
    url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain"))
]