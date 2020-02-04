from django.contrib import admin
from django.urls import path
from .apps.search.views import search_results, search_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', search_home, name='search_home'),
    path('search/', search_results, name='search_results'),
]
