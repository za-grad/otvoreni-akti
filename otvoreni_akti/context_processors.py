from otvoreni_akti.settings import SINGLE_CITY_SCOPE


def template_settings(request):
    return {
        'SHOW_CITY_SELECTOR': not SINGLE_CITY_SCOPE,
    }
