from django.contrib import admin
from .models import Item,Comment
# Register your models here.

class ShowItems(admin.ModelAdmin):
    fields = ('name', 'description','price','image')
    search_fields = ('name', 'description','price','image')
    list_display = ('name', 'description','price','image')
    list_editable = ['description']

admin.site.register(Item,ShowItems)
admin.site.register(Comment)