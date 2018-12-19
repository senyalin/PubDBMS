from __future__ import unicode_literals
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    credit_point = models.FloatField(default=1000)
    group_id = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    assessor_notes = models.CharField(max_length=200)
    gender = models.CharField(max_length=20)
    
class Publication(models.Model):
    title = models.CharField(max_length=1000, blank=True, null=True)
    category = models.IntegerField(blank=True, null=True)
    authors = models.CharField(max_length=1000, blank=True, null=True)
    institution = models.CharField(max_length=200, blank=True, null=True)
    publication_date = models.CharField(max_length = 200, blank=True, null=True)
    keywords = models.CharField(max_length = 1000, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    public_or_not = models.IntegerField(blank=True, null=True)
    abstract = models.CharField(max_length=10000, blank=True, null=True)
    file_name = models.CharField(max_length = 200, blank=True, null=True)
    file_location = models.CharField(max_length = 1000, blank=True, null=True)
    uploader_id = models.IntegerField()
    upload_date = models.CharField(max_length = 200, blank=True, null=True)
    
class Transaction_publication(models.Model):
    user_id = models.IntegerField()
    publication_id = models.IntegerField()
    amount = models.FloatField(blank=True, null=True)