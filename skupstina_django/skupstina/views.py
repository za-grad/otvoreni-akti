from django.shortcuts import render
from django.core.paginator import Paginator
from .utils import elastic_search

base_url = 'http://web.zagreb.hr'


def search_results(request):
    if request.GET:
        page = request.GET.get('page')
        search_term = request.GET.get('q')
        results = elastic_search(search_term)
        num_results = len(results)

        # Pagination
        pagniator = Paginator(results, 20)
        results = pagniator.get_page(page)

        context = {
            'results': results,
            'num_results': num_results,
            'base_url': base_url,
            }
        return render(request, 'skupstina/search_results.html', context)


def search_bar(request):
    return render(request, 'skupstina/search_bar.html')
