from django.shortcuts import render
from django.http import JsonResponse
from .utils import sql_search, elastic_search


def sql_search_results_view(request):
    if request.GET:
        search_term = request.GET.get('q')
        result = sql_search(search_term)
        return JsonResponse(result)


def elastic_search_results_view(request):
    if request.GET:
        search_term = request.GET.get('q')
        result = elastic_search(search_term)
        return JsonResponse(result)


def search_bar(request):
    return render(request, 'skupstina/search.html')
