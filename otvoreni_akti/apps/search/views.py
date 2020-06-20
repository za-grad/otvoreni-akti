import time
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from otvoreni_akti.settings import MAX_SEARCH_RESULTS, RESULTS_PER_PAGE, ACTS_ROOT_URL_ZAGREB as root_url
from .utils import elastic_search
from .models import Act, Period


def search_home(request):
    return render(request, 'search/search_home.html')


def search_results(request):
    if request.GET:
        page = request.GET.get('page')
        search_term = request.GET.get('q', '')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        sort_by = request.GET.get('sort_by')
        file_type = request.GET.get('file_type')

        # Checks if advanced features were used
        advanced_used = (start_date or end_date or sort_by != 'newest_first' or file_type != 'All')

        # If no user input, sets default start and end dates
        if not start_date:
            start_date = str(datetime(1900, 1, 1, 0, 0))
        if not end_date:
            end_date = str(datetime.now())

        t1 = time.time()
        results = elastic_search(
            search_term,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            file_type=file_type,
        )
        time_taken = '{0:.5g}'.format(time.time()-t1)
        num_results = len(results)

        # Pagination
        pagniator = Paginator(results, RESULTS_PER_PAGE)
        results = pagniator.get_page(page)

        # Vanity Metrics
        earliest_period = Period.objects.order_by('start_date').first().start_date
        latest_period = Period.objects.order_by('-end_date').first().end_date
        total_acts = Act.objects.count()

        context = {
            'results': results,
            'num_results': num_results,
            'max_results': MAX_SEARCH_RESULTS,
            'root_url': root_url,
            'time_taken': time_taken,
            'earliest_period': earliest_period,
            'latest_period': latest_period,
            'total_acts': total_acts,
            'advanced_used': advanced_used,
        }
        return render(request, 'search/search_results.html', context)
    return redirect(search_home)


def act_detail(request, id):
    act = get_object_or_404(Act, id=id)
    context = {
        'root_url': root_url,
        'act': act,
    }
    return render(request, 'search/act_detail.html', context)


def about(request):
    return render(request, 'search/about.html')


def view_404(request, exception=None):
    return redirect(search_home)
