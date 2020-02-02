import io
import docx
from PyPDF2 import PdfFileReader
from bs4 import BeautifulSoup
from .scrape_utils_requests import requests_retry_session

root_url = 'http://web.zagreb.hr'


def extract_docxfile_data(url_docx: str) -> str:
    response = requests_retry_session().get(url_docx)
    file = io.BytesIO(response.content)
    doc = docx.Document(file)
    doc_raw_data = ''
    for para in doc.paragraphs:
        doc_raw_data += para.text + '\n'
    return doc_raw_data


def extract_pdffile_data(url_pdf: str) -> str:
    response = requests_retry_session().get(url_pdf)
    file = io.BytesIO(response.content)
    pdf_reader = PdfFileReader(file)
    pdf_raw_data = ''
    for page in range(pdf_reader.numPages):
        pdf_raw_data += pdf_reader.getPage(page).extractText() + '\n'
    return pdf_raw_data


def parse_document_link(docu_url: str) -> tuple:
    site = requests_retry_session().get(root_url + docu_url).content
    soup = BeautifulSoup(site, 'html.parser')
    docu_text = soup.select('tr td b font')
    docu_link = soup.select('tr td a')[0].attrs['href']
    docu_title = '{}: {}'.format(docu_text[0].contents[0], docu_text[1].contents[0])
    docu_file_type = 'unknown'
    if '.docx' in docu_link in docu_link:
        docu_raw_data = extract_docxfile_data(root_url + docu_link)
        docu_file_type = 'docx'
    elif '.pdf' in docu_link:
        docu_raw_data = extract_pdffile_data(root_url + docu_link)
        docu_file_type = 'pdf'
    else:
        # For old Word documents and other file types
        docu_raw_data = 'The search engine could not extract data from this file.' \
                        ' Navigate to this URL to download the file: {}'.format(root_url + docu_link)
    return docu_title, docu_raw_data, docu_file_type
