import os
from unittest.mock import patch
from django.test import TestCase
import pytest
from .. import scrape_utils_docu

pytestmark = pytest.mark.django_db
file_path = os.path.dirname(os.path.abspath(__file__))


class TestExtractDocxfileData(TestCase):
    def test_function_extracts_data_from_doc_body(self):
        with open(file_path + '/dummy_website/dummy_docx.docx', 'rb') as file:
            with patch.object(scrape_utils_docu, 'requests_retry_session') as mocked_session:
                mocked_get = mocked_session.return_value.get
                mocked_get.return_value.content = file.read()
                docu_raw_data = scrape_utils_docu.extract_docxfile_data('dummyvalue')
                # Check for data with special characters in the body
                self.assertIn('This iš just a tribute', docu_raw_data)
                # Check for data with special characters inside a nested table
                self.assertIn('KONAČNU Lucifer!', docu_raw_data)


class TestExtractPdffileData(TestCase):
    def test_function_extracts_data_from_doc_body(self):
        with open(file_path + '/dummy_website/dummy_pdf.pdf', 'rb') as file:
            with patch.object(scrape_utils_docu, 'requests_retry_session') as mocked_session:
                mocked_get = mocked_session.return_value.get
                mocked_get.return_value.content = file.read()
                pdf_raw_data = scrape_utils_docu.extract_pdffile_data('dummyvalue')
                # Check for data with special characters in the body
                self.assertIn('KONAČNU LISTU REDA PRVENSTVA', pdf_raw_data)
                # Check for data with special characters inside a nested table
                self.assertIn('KRIŽNIK MARJANA', pdf_raw_data)
