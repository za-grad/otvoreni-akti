import time
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from otvoreni_akti.settings import MAX_SEARCH_RESULTS, ACTS_ROOT_URL as root_url
from .utils import elastic_search
from .models import Act, Period


def search_home(request):
    return render(request, 'search/search_home.html')


def search_results(request):
    if request.GET:
        page = request.GET.get('page')
        search_term = request.GET.get('q')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not start_date:
            # If no user input, sets default start date to 1 Jan 1900
            start_date = str(datetime(1900, 1, 1, 0, 0))

        if not end_date:
            # If no user input, sets default end date to today
            end_date = str(datetime.now())

        t1 = time.time()
        results = elastic_search(search_term, start_date=start_date, end_date=end_date)
        time_taken = '{0:.5g}'.format(time.time()-t1)
        num_results = len(results)

        # Pagination
        pagniator = Paginator(results, 20)
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
        }
        return render(request, 'search/search_results.html', context)


def act_detail(request, id):
    act = get_object_or_404(Act, id=id)
    context = {
        'root_url': root_url,
        'act': act,
    }
    return render(request, 'search/act_detail.html', context)
