import os

from django.conf import settings

import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image 
import PIL 
  
def read_bill_of_lading(file):
#    TESSERACT_PATH = r'dependencies/tesseract/tesseract.exe'
#    path = os.getcwd()
#    tesseract = os.path.abspath(os.path.join(path, TESSERACT_PATH))
#    pytesseract.pytesseract.tesseract_cmd = tesseract 
    
    # Search keyterms
    SIMPLE_SEARCH_QUERY = {
        'delivery_number' : "Delivery No.:",
        'sales_number' : "Sales Order #",
        'delivery_date' : "Delivery Date:",
    }

    # Set dependencies
    POPPLER_PATH = None
    TESSERACT_PATH = None
    if os.name == 'nt':
        POPPLER_PATH = settings.BASE_DIR / 'dependencies/poppler/Library/bin'
        TESSERACT_PATH = settings.BASE_DIR / 'dependencies/tesseract/tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        

    # Convert PDF to PIL images using pdf2image
    pages = convert_from_bytes(file.read(), dpi=400, poppler_path = POPPLER_PATH)
    page = np.array(pages[0])
    gray = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)
                                
    # Extract text from image
    ocr_text = pytesseract.image_to_string(gray, lang='eng')
    ocr_split_lines = ocr_text.split('\n')
    ocr_split_text = ocr_text.replace('\n', ' ').split(' ')


    mapped_values = {}
    for key, value in SIMPLE_SEARCH_QUERY.items():
        search_terms = value.split(' ')

        for i in range(len(ocr_split_text)):
            if ocr_split_text[i] == search_terms[0]:
                for j in range(len(search_terms)):
                    if i+j < len(ocr_split_text) and ocr_split_text[i+j] == search_terms[j]:
                        if j == len(search_terms) - 1:
                            search_result = ocr_split_text[i + len(search_terms)]
                            mapped_values.update({key : search_result})
                    else:
                        break
                    
    return mapped_values

def combine_pdfs(file1, file2):
    pdfs = [file1, file2]
    merger = PdfMerger()

    for pdf in pdfs:
        merger.append(pdf)

    result = merger.write("result.pdf")
    merger.close()
    return result
