from django.contrib import admin
from django.urls import path
from skupstina.views import sql_search_results_view, elastic_search_results_view, search_bar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', search_bar, name='search_bar'),
    path('sqlsearch/', sql_search_results_view, name='sql_search_results'),
    path('esearch/', elastic_search_results_view, name='elastic_search_results'),
]
