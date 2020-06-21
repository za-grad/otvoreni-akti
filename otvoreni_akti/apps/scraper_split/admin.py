from django.contrib import admin
from .models import ScraperPeriod


@admin.register(ScraperPeriod)
class ScraperAdmin(admin.ModelAdmin):
    # List view
    list_display = ('date', 'url', 'scrape_completed',)
    list_filter = ('date', )
    search_fields = ('date', 'url', )
    ordering = ('-date',)
