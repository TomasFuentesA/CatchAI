import re
from pypdf import PdfReader

def extract_text(pdf_path):
    '''
    Input: Path a los archivos PDF
    Output: Texto extraído de los archivos PDF
    Descripción: Esta función utiliza la biblioteca PyPDF para leer un archivo PDF y extraer su contenido de texto.
    '''
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def clean_text(text):
    '''
    Input: Texto extraído de los archivos PDF
    Output: Texto limpio y procesado
    Descripción: Esta función toma el texto extraído de un PDF y realiza limpieza y normalización.
    '''
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = text.replace('\r', '').replace('\t', ' ')
    return text