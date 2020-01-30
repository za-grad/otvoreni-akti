from django.contrib import admin
from django.urls import path
from skupstina.views import search_results, search_bar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', search_bar, name='search_bar'),
    path('search/', search_results, name='search_results'),
]
