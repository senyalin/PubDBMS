# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.login, name="index"),
    url(r'^login/$', views.login, name="login"),
    url(r'^register/$', views.register, name="register"),
    url(r'^retrieve/$', views.retrieve, name="retrieve"),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^upload_publication/$', views.upload_publication, name="upload_publication"),
    url(r'^search_publication/$', views.search_publication, name = "search_publication"),
    url(r'^detail_publication/(?P<publication_id>[0-9]+)/$', views.detail_publication, name = "detail_publication"),
    url(r'^save_publication/$', views.save_publication, name="save_publication"),
    url(r'^order_publication/$', views.order_publication, name="order_publication"),
    url(r'^payment_publication/$', views.payment_publication, name="payment_publication"),
    url(r'^process_publication/(?P<publication_id>[0-9]+)/$', views.process_publication, name="process_publication")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
