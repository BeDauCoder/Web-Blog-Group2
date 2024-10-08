from django.contrib import admin
from .models import User
# Register your models here.

class DisplayUser(admin.ModelAdmin):
    fields = ('username','email','password','birth_date','created_at')
    search_fields = ('username','email','password','birth_date','created_at')
    list_display = ('username','email','password','birth_date','created_at')
    list_editable = ['email']

admin.site.register(User,DisplayUser)