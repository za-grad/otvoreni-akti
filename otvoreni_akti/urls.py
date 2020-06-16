from django.contrib import admin
from django.urls import path
from .apps.search.views import search_results, search_home, act_detail, about, view_404

handler404 = view_404
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', search_home, name='search_home'),
    path('search/', search_results, name='search_results'),
    path('acts/<int:id>/', act_detail, name='act_detail'),
    path('manifest/', about, name='about'),
]
