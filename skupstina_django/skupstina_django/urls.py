from django.contrib import admin
from django.urls import path
from skupstina.views import search_results_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/<search_term>', search_results_view, name='search_results'),
]
