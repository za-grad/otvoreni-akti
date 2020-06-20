import io
import docx2txt
import fitz
from bs4 import BeautifulSoup
from otvoreni_akti.apps.common_utils.scrape_utils_requests import requests_retry_session
from otvoreni_akti.settings import ACTS_ROOT_URL as root_url


def extract_docxfile_data(url_docx: str) -> str:
    response = requests_retry_session().get(url_docx)
    file = io.BytesIO(response.content)
    return docx2txt.process(file)


def extract_pdffile_data(url_pdf: str) -> str:
    response = requests_retry_session().get(url_pdf)
    file = io.BytesIO(response.content)
    pdf_reader = fitz.open(stream=file, filetype='pdf')
    pdf_raw_data = ''
    for page in range(pdf_reader.pageCount):
        pdf_raw_data += pdf_reader.loadPage(page).getText() + '\n'
    return pdf_raw_data


def parse_document_link(docu_url: str) -> tuple:
    site = requests_retry_session().get(root_url + docu_url).content
    soup = BeautifulSoup(site, 'html.parser')
    docu_text = soup.select('tr td b font')
    docu_link = soup.select('tr td a')[0].attrs['href']

    # Strip all <br/> from soup
    for br in soup.findAll('br'):
        br.extract()

    # Get document title
    docu_title = ''
    for sub_docu_text in docu_text:
        if sub_docu_text.contents:
            if sub_docu_text.contents[0] != 'Dodatni opis':
                docu_title += sub_docu_text.contents[0] + ' '

    docu_file_type = 'unknown'
    if docu_link.endswith('.docx'):
        docu_raw_data = extract_docxfile_data(root_url + docu_link)
        docu_file_type = 'docx'
    elif docu_link.endswith('.pdf'):
        docu_raw_data = extract_pdffile_data(root_url + docu_link)
        docu_file_type = 'pdf'
    else:
        # For old Word documents and other file types
        docu_raw_data = 'The search engine could not extract data from this file.' \
                        ' Navigate to this URL to download the file: {}'.format(root_url + docu_link)
    return docu_title, docu_raw_data, docu_file_type
