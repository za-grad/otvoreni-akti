from datetime import datetime
from django.utils import timezone
from django.test import TestCase
from mixer.backend.django import mixer
import pytest
from .. import db_utils
from otvoreni_akti.apps.search.models import Period, Item, Subject, Act

pytestmark = pytest.mark.django_db

subject_details = {
    'text': '32. TOČKA DNEVNOG REDA\nTOČKA: 32.\nREPUBLIKA HRVATSKA\nGRAD ZAGREB\nStručna služba gradonačelnika\n'
            'Predmet:\nImenovanje pomoćnika pročelnika Stručne službe gradonačelnika\nAkti:\nRJEŠENJE: skraćeno',
    'acts':
        [
            {
                'act_content': 'RJEŠENJE\nTOČKA: 32.\nPODTOČKA: 32.\n- -RJEŠENJE- -\n'
                               'KLASA: UP/I-080-03/20-01/3URBROJ: 251-03-02-20-1\nZagreb, 31. siječnja 2020.\n'
                               'Na temelju članka 5. stavka 3. Zakona o službenicima i namještenicima u lokalnoj i '
                               'područnoj (regionalnoj) samoupravi (Narodne novine 86/08, 61/11 i 112/19), u vezi s '
                               'točkom 7. stavkom 4. Načela o unutarnjem ustrojstvu i načinu rada u gradskim upravnim '
                               'tijelima (Službeni glasnik Grada Zagreba\n17/10, 4/12 i 7/19), gradonačelnik '
                               'Grada Zagreba, donosi\nRJ E Š E NJ E\no imenovanju\nDIAN TURČINOV, '
                               'diplomirani inženjer prometa, imenuje se, s danom 3.2.2020., pomoćnikom '
                               'pročelnika za poslove zaštite osoba i imovine (I. kategorija, potkategorija '
                               'viši rukovoditelj, klasifikacijski rang 2.) Izvan ustrojstvenih jedinica u Stručnoj '
                               'službi gradonačelnika.\nGRADONAČELNIK\nGRADA ZAGREBA\n'
                               'Milan Bandić, dipl.politolog, v.r.',
                'act_url': '/sjednice/2017/sjednice_2017.nsf/'
                           'dokument_opci_sjednica_noatt_web?openform&parentunid=8f55fc7a97225cdac1258500003b451d',
                'act_title': 'RJEŠENJE: skraćeno',
                'act_file_type': 'HTML'
            }
        ]
}

subject = {
    'details': subject_details,
    'subject_url': 'dummy subject url',
    'subject_title': 'Dummy Subject Title',
}

act_list = [
    {
        'act_content': 'ZAKLJUČAK\nTOČKA: 32.\nPODTOČKA: 32.\n- -ZAKLJUČAK- -\n'
                       'Na temelju članka 60. stavka 1. točke 24. Statuta Grada Zagreba (Službeni glasnik '
                       'Grada Zagreba 23/16, 2/18 i 23/18 ), gradonačelnik Grada Zagreba, 5. veljače 2020., donosi\n'
                       'Z A K LJ U Č A K\no izmjenama Zaključka o osnivanju i imenovanju Organizacijskog odbora '
                       'za održavanje\n9. sastanka gradonačelnika glavnih gradova država članica Europske unije i\n'
                       'Europske komisije\n1. U Zaključku o osnivanju i imenovanju Organizacijskog odbora za '
                       'održavanje 9. sastanka gradonačelnika glavnih gradova država članica '
                       'Europske unije i Europske komisije '
                       '(Službeni glasnik Grada Zagreba 22/19) točka 3. mijenja se i glasi:\n„'
                       'Organizacijski odbor sastavljen je od predsjednice i osam članova.“.\n'
                       '2. U točki 4. alineji 2. riječi:\n"Marijan Crnjak," brišu se.\n'
                       '3. Ovaj će zaključak biti objavljen u Službenom glasniku Grada Zagreba.\nKLASA:\n'
                       '910-01/20-02/1\nURBROJ: 251-03-02-20-2\nZagreb,\n5. 2. 2020.\nGRADONAČELNIK\nGRADA ZAGREBA\n'
                       'Milan Bandić, dipl. politolog, v.r.',
        'act_url': '/sjednice/2017/sjednice_2017.nsf/dokument_opci_sjednica_noatt_web?'
                   'openform&parentunid=0e0d2d85de08d544c125850400357f7e',
        'act_title': 'ZAKLJUČAK',
        'act_file_type': 'HTML'
    },
    {
        'act_content': 'OBRAZLOŽENJE\nTOČKA: 32.\nPODTOČKA: 32.\n--OBRAZLOŽENJE- -\n'
                       'Zaključkom o osnivanju i imenovanju Organizacijskog odbora za održavanje 9. '
                       'sastanka gradonačelnika glavnih gradova država članica Europske unije i Europske '
                       'komisije (Službeni glasnik Grada Zagreba 22/19) osnovan je Organizacijski odbor i imenovani '
                       'su predsjednica i devet članova. Između ostalih, za člana je imenovan Marijan Crnjak. '
                       'Kako je Marijanu Crnjaku završilo stručno osposobljavanje za rad bez zasnivanja radnog odnosa '
                       'u Uredu za međugradsku i međunarodnu suradnju i promicanje ljudskih prava, isti se razrješuje '
                       'dužnosti člana u navedenom odboru, te će Organizacijski odbor imati osam članova.Sukladno '
                       'navedenom, donosi se zaključak u predloženome tekstu.',
        'act_url': '/sjednice/2017/sjednice_2017.nsf/dokument_opci_sjednica_noatt_web?'
                   'openform&parentunid=65bec36fa1d214cec12585040035a50a',
        'act_title': 'OBRAZLOŽENJE',
        'act_file_type': 'HTML'
    }
]


class TestParseDateRange(TestCase):
    def test_function_returns_correct_dates(self):
        date_range = '3. veljače 2020.   -   7.veljače 2020'
        start_date, end_date = db_utils.parse_date_range(date_range)
        self.assertEqual(
            start_date,
            timezone.make_aware(datetime(2020, 2, 3, 0, 0, 0))
        )
        self.assertEqual(
            end_date,
            timezone.make_aware(datetime(2020, 2, 7, 0, 0, 0))
        )

    def test_function_handles_studenog(self):
        date_range = '25. studenog 2019. - 29.studenog 2019'
        start_date, end_date = db_utils.parse_date_range(date_range)
        self.assertEqual(
            start_date,
            timezone.make_aware(datetime(2019, 11, 25, 0, 0, 0))
        )
        self.assertEqual(
            end_date,
            timezone.make_aware(datetime(2019, 11, 29, 0, 0, 0))
        )


class TestParseItemDetails(TestCase):
    def test_function_returns_correct_data(self):
        item_number, item_text = db_utils.parse_item_details(subject_details)
        self.assertEqual(item_number, 32)
        self.assertEqual(item_text, 'Blank')


class TestWritePeriodToDB(TestCase):
    def test_function_writes_correct_data(self):
        period_text = '25. studenog 2019. - 29.studenog 2019'
        period_url = 'dummyurl'
        period_obj = db_utils.write_period_to_db(period_text, period_url)
        self.assertEqual(period_obj.pk, 1)
        self.assertEqual(period_obj.period_text, '25.Nov.2019 to 29.Nov.2019')
        self.assertEqual(
            period_obj.start_date,
            timezone.make_aware(datetime(2019, 11, 25, 0, 0, 0))
        )
        self.assertEqual(
            period_obj.end_date,
            timezone.make_aware(datetime(2019, 11, 29, 0, 0, 0))
        )
        self.assertEqual(period_obj.period_url, 'dummyurl')

    def test_function_ignores_duplicate_data(self):
        period_text = '29. studenog 2019. - 30.studenog 2019'
        period_url = 'dummyurl'
        db_utils.write_period_to_db(period_text, period_url)
        self.assertEqual(Period.objects.first().period_text, '29.Nov.2019 to 30.Nov.2019')
        self.assertEqual(Period.objects.count(), 1)

        # Try to write the same period again
        period_obj = db_utils.write_period_to_db(period_text, period_url)
        self.assertEqual(Period.objects.first().period_text, period_obj.period_text)
        self.assertEqual(Period.objects.count(), 1)


class TestWriteItemToDB(TestCase):
    def test_function_writes_correct_data(self):
        period_text = '01. studenog 2019. - 05.studenog 2019'
        period_url = 'dummyurl'
        period_obj = db_utils.write_period_to_db(period_text, period_url)
        item_obj = db_utils.write_item_to_db(subject_details, period_obj)
        self.assertEqual(item_obj.pk, 1)
        self.assertEqual(item_obj.period, period_obj)
        self.assertEqual(item_obj.item_title, '#{} from period {}'.format(32, '01.Nov.2019 to 05.Nov.2019'))
        self.assertEqual(item_obj.item_number, 32)
        self.assertEqual(item_obj.item_text, 'Blank')

    def test_function_ignores_duplicate_data(self):
        period_text = '01. studenog 2019. - 05.studenog 2019'
        period_url = 'dummyurl'
        period_obj = db_utils.write_period_to_db(period_text, period_url)
        item_obj = db_utils.write_item_to_db(subject_details, period_obj)
        self.assertEqual(Item.objects.first().item_title, '#{} from period {}'.format(32, '01.Nov.2019 to 05.Nov.2019'))
        self.assertEqual(Item.objects.count(), 1)

        # Try to write the same item again
        item_obj = db_utils.write_item_to_db(subject_details, period_obj)
        self.assertEqual(Item.objects.first().item_title, item_obj.item_title)
        self.assertEqual(Item.objects.count(), 1)


class TestWriteSubjectToDB(TestCase):
    def test_function_writes_correct_data(self):
        period_obj = mixer.blend(Period)
        subj_obj = db_utils.write_subject_to_db(subject, period_obj)
        self.assertEqual(subj_obj.pk, 1)
        self.assertEqual(subj_obj.subject_title, subject['subject_title'])
        self.assertEqual(subj_obj.subject_url, subject['subject_url'])

    def test_function_ignores_duplicate_data(self):
        period_obj = mixer.blend(Period)
        subj_obj = db_utils.write_subject_to_db(subject, period_obj)
        self.assertEqual(Subject.objects.first().subject_url, subject['subject_url'])
        self.assertEqual(Subject.objects.count(), 1)

        # Try to write the same subject again
        subj_obj = db_utils.write_subject_to_db(subject, period_obj)
        self.assertEqual(Subject.objects.first().subject_url, subject['subject_url'])
        self.assertEqual(Subject.objects.count(), 1)


class TestWriteActToDB(TestCase):
    def test_function_writes_correct_data(self):
        subj_obj = mixer.blend(Subject)
        db_utils.write_act_to_db(act_list, subj_obj)
        new_acts = Act.objects.all()
        self.assertEqual(new_acts.count(), 2)
        self.assertEqual(new_acts[0].content_url, act_list[0]['act_url'])
        self.assertEqual(new_acts[1].content_url, act_list[1]['act_url'])

    def test_function_ignores_duplicate_data(self):
        subj_obj = mixer.blend(Subject)
        db_utils.write_act_to_db(act_list, subj_obj)
        new_acts = Act.objects.all()
        self.assertEqual(new_acts[0].content_url, act_list[0]['act_url'])
        self.assertEqual(new_acts[1].content_url, act_list[1]['act_url'])
        self.assertEqual(new_acts.count(), 2)

        # Try to write the same acts again
        db_utils.write_act_to_db(act_list, subj_obj)
        latest_act = Act.objects.first()
        self.assertEqual(latest_act.content_url, act_list[0]['act_url'])
        self.assertEqual(Act.objects.count(), 2)
