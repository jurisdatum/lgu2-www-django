
from django.contrib import admin

from .models import *

admin.site.register(Message)

@admin.register(DatasetCompleteness)
class DatasetAdmin(admin.ModelAdmin):
   list_display = [ 'type', 'cutoff' ]
