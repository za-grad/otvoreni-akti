import dateparser
import re
from skupstina.models import Period, Item, Subject, Act


def parse_date_range(date_range: str) -> tuple:
    """Parses Croatian date range to return datetime objects."""
    start_date, end_date = date_range.split(' - ')
    start_date = dateparser.parse(start_date, languages=['hr'])
    end_date = dateparser.parse(end_date, languages=['hr'])
    return start_date, end_date


def parse_item_details(subject_details):
    # Regex to find the first set of digits in the subject_details
    item_number = int(re.findall(r'\d+', subject_details['text'])[0])
    item_text = 'Blank'
    return item_number, item_text


def write_period_to_db(period_text: str, period_url: str):
    start_date, end_date = parse_date_range(period_text)
    if not Period.objects.filter(period_text=period_text).exists():
        print('Adding period:', period_text)
        new_period = Period(
            period_text=period_text,
            start_date=start_date,
            end_date=end_date,
            period_url=period_url,
        )
        new_period.save()
        return new_period
    else:
        return Period.objects.get(period_text=period_text)


def write_item_to_db(subject_details, period_obj):
    item_number, item_text = parse_item_details(subject_details)
    item_title = '#{} from period {}'.format(str(item_number), period_obj.period_text)
    if not Item.objects.filter(item_title=item_title).exists():
        print('Adding item:', item_title)
        new_item = Item(
            period=period_obj,
            item_title=item_title,
            item_number=item_number,
            item_text=item_text,
        )
        new_item.save()
        return new_item
    else:
        return Item.objects.get(item_title=item_title)


def write_subject_to_db(subject, period_obj):
    item_obj = write_item_to_db(subject['details'], period_obj)
    if not Subject.objects.filter(subject_url=subject['subject_url']).exists():
        print('Adding subject:', subject['subject_title'])
        new_subject = Subject(
            item=item_obj,
            subject_title=subject['subject_title'],
            subject_url=subject['subject_url'],
        )
        new_subject.save()
        return new_subject
    else:
        return Subject.objects.get(subject_url=subject['subject_url'])


def write_act_to_db(acts: dict, subject_obj):
    for act in acts:
        # Populate the Act table
        if not Act.objects.filter(content_url=act['act_url']).exists():
            print('Adding act:', act['act_title'])
            new_act = Act(
                subject=subject_obj,
                title=act['act_title'],
                content=act['act_content'],
                content_url=act['act_url'],
            )
            new_act.save()
