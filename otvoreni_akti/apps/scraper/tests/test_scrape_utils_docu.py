import os
from django.test import TestCase
from .mock_requests import requests_patcher
from .. import scrape_utils_docu

file_path = os.path.dirname(os.path.abspath(__file__))


class TestExtractDocxfileData(TestCase):
    def test_function_extracts_data_from_docx_body(self):
        with open(file_path + '/dummy_website/dummy_docx.docx', 'rb') as file:
            docx_raw_data = requests_patcher(
                parent_module=scrape_utils_docu,
                function_to_patch=scrape_utils_docu.extract_docxfile_data,
                payload=file.read()
            )
            # Check for data with special characters in the body
            self.assertIn('This iš just a tribute', docx_raw_data)
            # Check for data with special characters inside a nested table
            self.assertIn('KONAČNU Lucifer!', docx_raw_data)


class TestExtractPdffileData(TestCase):
    def test_function_extracts_data_from_pdf_body(self):
        with open(file_path + '/dummy_website/dummy_pdf.pdf', 'rb') as file:
            pdf_raw_data = requests_patcher(
                parent_module=scrape_utils_docu,
                function_to_patch=scrape_utils_docu.extract_pdffile_data,
                payload=file.read()
            )
            # Check for data with special characters in the body
            self.assertIn('KONAČNU LISTU REDA PRVENSTVA', pdf_raw_data)
            # Check for data with special characters inside a nested table
            self.assertIn('KRIŽNIK MARJANA', pdf_raw_data)


class TestParseDocumentLink(TestCase):
    """This test uses requires City Website to be online and reachable."""

    test_url_docx = '/Sjednice/2017/Sjednice_2017.nsf/0/BA0CD92F5FD33BB5C12584CC0031AEAB?OpenDocument'
    test_url_pdf = '/sjednice/2017/Sjednice_2017.nsf/0/E4DD04E1B54F903AC12583CC004A61B7?OpenDocument'
    test_url_doc = '/Sjednice/2017/Sjednice_2017.nsf/0/8203D0E3AE893366C12585030031087D?OpenDocument'

    def test_function_extracts_correct_docx_data(self):
        docu_title, docu_raw_data, docu_file_type = scrape_utils_docu.parse_document_link(self.test_url_docx)
        self.assertEqual(docu_file_type, 'docx')
        self.assertIn('ZAKLJUČAK Špoljarić', docu_title)
        self.assertNotIn('Dodatni opis', docu_title)
        self.assertIn('ĆORIĆ ROMANA', docu_raw_data)

    def test_function_extracts_correct_pdf_data(self):
        docu_title, docu_raw_data, docu_file_type = scrape_utils_docu.parse_document_link(self.test_url_pdf)
        self.assertEqual(docu_file_type, 'pdf')
        self.assertIn('Konačna lista', docu_title)
        self.assertNotIn('Dodatni opis', docu_title)
        self.assertIn('KRIŽNIK MARJANA', docu_raw_data)

    def test_function_extracts_correct_doc_data(self):
        docu_title, docu_raw_data, docu_file_type = scrape_utils_docu.parse_document_link(self.test_url_doc)
        self.assertEqual(docu_file_type, 'unknown')
        self.assertIn('PLAN', docu_title)
        self.assertNotIn('Dodatni opis', docu_title)
        self.assertIn('The search engine could not extract data', docu_raw_data)
