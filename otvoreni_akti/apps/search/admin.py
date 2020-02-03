from django.contrib import admin
from .models import Period, Item, Subject, Act

admin.site.register(Item)


@admin.register(Act)
class ActAdmin(admin.ModelAdmin):
    # List view
    list_display = ('title', 'file_type', 'content_url',)
    list_filter = ('file_type',)
    search_fields = ('title', 'content', 'content_url',)


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    # List view
    list_display = ('period_text', 'start_date', 'end_date', 'period_url',)
    search_fields = ('period_text', 'period_url',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    # List view
    list_display = ('subject_title', 'item', 'subject_url',)
    search_fields = ('subject_title', 'subject_url',)
