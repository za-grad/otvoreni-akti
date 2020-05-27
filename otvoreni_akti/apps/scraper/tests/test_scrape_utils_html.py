from collections import Counter
import os
from bs4 import BeautifulSoup
from django.test import TestCase
import pytest
from .mock_requests import requests_patcher
from .. import scrape_utils_html
from ..scrape_utils_requests import requests_retry_session
from otvoreni_akti.apps.search.models import Period, Item, Subject, Act

pytestmark = pytest.mark.django_db
file_path = os.path.dirname(os.path.abspath(__file__))


class TestGetVisibleText(TestCase):
    """This test uses requires City Website to be online and reachable."""
    test_url_with_redirect = 'http://web.zagreb.hr/sjednice/2017/Sjednice_2017.nsf/' \
                             'Dokument_opci_sjednica_noatt_web?OpenForm&ParentUNID=2FE43BDF830C9381C12582C000231875'

    def test_function_extracts_correct_data_from_normal_page(self):
        with open(file_path + '/dummy_website/dummy_act_body_1.html', 'rb') as site:
            soup = BeautifulSoup(site, 'html.parser')
            text = scrape_utils_html.get_visible_text(soup)
            self.assertIn('TheHiddenMarker1', text)

    def test_function_extracts_correct_data_from_page_with_hidden_redirect(self):
        site = requests_retry_session().get(self.test_url_with_redirect).content
        soup = BeautifulSoup(site, 'html.parser')
        text = scrape_utils_html.get_visible_text(soup)
        self.assertIn('Gradonačelnik Grada Zagreba', text)


class TestParseSubjectList(TestCase):
    def test_function_extracts_correct_data(self):
        with open(file_path + '/dummy_website/dummy_subjects_list.html', 'rb') as file:
            subjects, num_els = requests_patcher(
                parent_module=scrape_utils_html,
                function_to_patch=scrape_utils_html.parse_subjects_list,
                payload=file.read()
            )
            self.assertEqual(
                'Korištenje - Gradski ured za sport i mlade',
                subjects[4]['subject_title']
            )
            # Function can handle Subjects without a link
            self.assertEqual(
                'Dom za starije osobe Sv. Josip Zagreb i dr.',
                subjects[57]['subject_title']
            )

            self.assertEqual(num_els, 59)


class TestParseSubjectDetails(TestCase):
    """This test uses requires City Website to be online and reachable."""
    test_url = 'http://web.zagreb.hr/' \
               'sjednice/2017/sjednice_2017.nsf/pw?openform&parentunid=4a889525e0ddaf45c12582bf004dd869'

    def test_function_extracts_correct_data(self):
        subject_details = scrape_utils_html.parse_subject_details(self.test_url)

        # Check the first Act
        first_act = subject_details['acts'][0]
        self.assertIn('ZAKLJUČAK: Vodoopskrba i odvodnja d.o.o.', first_act['act_title'])
        self.assertIn('Društvu VODOOPSKRBA I ODVODNJA d.o.o. iz Zagreba, Folnegovićeva', first_act['act_content'])
        self.assertEqual(
            '/sjednice/2017/sjednice_2017.nsf/'
            'dokument_opci_sjednica_noatt_web?openform&parentunid=019fc4205efe7e53c12582be00459082',
            first_act['act_url']
        )
        self.assertEqual('HTML', first_act['act_file_type'])

        # Check the fifth Act
        fifth_act = subject_details['acts'][4]
        self.assertIn('ZAKLJUČAK:  "HEP-ODS“ d.o.o.', fifth_act['act_title'])
        self.assertIn('Društvu „HEP-ODS“ d.o.o. ELEKTRA ZAGREB', fifth_act['act_content'])
        self.assertEqual(
            '/sjednice/2017/sjednice_2017.nsf/'
            'dokument_opci_sjednica_noatt_web?openform&parentunid=ababd5fa3445a319c12582bf004e1959',
            fifth_act['act_url']
        )
        self.assertEqual('HTML', fifth_act['act_file_type'])

        # Check an Act with a document is saved
        document_act = subject_details['acts'][15]
        self.assertIn('OBRAZLOŽENJE', document_act['act_title'])
        self.assertIn('Drezga Anto', document_act['act_content'])
        self.assertEqual(
            '/sjednice/2017/Sjednice_2017.nsf/'
            '0/C22E9EED079C7123C12582BF002813A2?OpenDocument',
            document_act['act_url']
        )
        self.assertEqual('docx', document_act['act_file_type'])

        # Check all acts on the page are saved
        self.assertEqual(len(subject_details['acts']), 30)
        file_type_counter = Counter(x['act_file_type'] for x in subject_details['acts'])
        self.assertEqual(file_type_counter['HTML'], 15)
        self.assertEqual(file_type_counter['docx'], 12)
        self.assertEqual(file_type_counter['unknown'], 3)


class TestScrapeEngine(TestCase):
    """This test uses requires City Website to be online and reachable."""
    test_act_period = '13. kolovoza 2018. - 17.kolovoza 2018'
    test_periods_url = 'http://web.zagreb.hr/sjednice/2017/Sjednice_2017.nsf/DRJ?OpenAgent&'

    def test_function_saves_all_data(self):
        self.assertEqual(Period.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(Act.objects.count(), 0)

        scrape_utils_html.scrape_engine(self.test_act_period, self.test_periods_url)

        self.assertEqual(Period.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 17)
        self.assertEqual(Subject.objects.count(), 25)
        self.assertEqual(Act.objects.count(), 89)
