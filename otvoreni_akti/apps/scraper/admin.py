from django.contrib import admin
from .models import ScraperPeriod


@admin.register(ScraperPeriod)
class ScraperAdmin(admin.ModelAdmin):
    # List view
    list_display = ('period_text', 'scrape_completed', 'start_date', 'end_date', 'year_range',)
    list_filter = ('scrape_completed', 'year_range',)
    search_fields = ('period_text',)
    ordering = ('-start_date',)
