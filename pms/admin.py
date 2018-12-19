from django.contrib import admin
from .models import User, Publication, Transaction_publication

# Register your models here.
admin.site.register(User)
admin.site.register(Publication)
admin.site.register(Transaction_publication)
