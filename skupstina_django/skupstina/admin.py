from django.contrib import admin

from .models import Category, Source, Item, Act

admin.site.register(Category)
admin.site.register(Source)
admin.site.register(Item)
admin.site.register(Act)
