import io

import fitz  # PyMuPDF
import pytesseract as pyt
from PIL import Image


class DocParser:
    def __init__(self, file: str):
        """
        Initializes the document parser with the provided file path.
        :param file: Path to the file (PDF or image).
        """
        self.file = file
        self.content = ''

    @staticmethod
    def extract_text_ocr(image: str) -> str:
        """
        Extracts text from an image file using Tesseract OCR.
        :param image: Path to the image file.
        :return: Extracted text as a string.
        """
        try:
            img = Image.open(image)
            img_text = pyt.image_to_string(img).strip()
            return img_text
        except Exception as e:
            print(f"Error reading text from image: {e}")
            return ''

    @staticmethod
    def extract_text(page) -> str:
        """
        Extracts text from a single PDF page.
        :param page: A page object from PyMuPDF.
        :return: Extracted text as a string.
        """
        try:
            text_page = page.get_textpage()
            text = text_page.extractTEXT(sort=True)
            return text
        except Exception as e:
            print(f"Error extracting text from page: {e}")
            return ''

    @staticmethod
    def is_scanned_pdf(page) -> bool:
        text = page.get_text().strip()
        if not text:
            return True
        else:
            return False

    @staticmethod
    def convert_page_img(page):
        pix_map = page.get_pixmap()
        image = pix_map.tobytes('png')
        img = Image.open(io.BytesIO(image))
        return img
    

    def parse_doc(self) -> str:
        """
        Parses the document (PDF or image) and extracts text content.
        :return: Extracted text content as a string.
        """
        file_type = self.file.split('.')[-1].lower()

        if file_type == 'pdf':
            print('Proceeding with PDF extraction...')
            try:
                doc = fitz.open(self.file)
                for page_index, page in enumerate(doc):

                    flag = DocParser.is_scanned_pdf(page)
                    if flag:
                        print (f'Processing page{page_index +1} as scanned page')
                        print(f"Processing page {page_index + 1} out of {doc.page_count}")

                        image = DocParser.convert_page_img(page)
                        text = pyt.image_to_string(image).strip()
                        self.content += text + '\n'


                    print(f"Processing page {page_index + 1} out of {doc.page_count}")
                    text = self.extract_text(page)
                    self.content += text + '\n' 

                return self.content
            except Exception as e:
                print(f"Error processing PDF file: {e}")
                return ''
        else:
            print('Proceeding with image extraction...')
            text = self.extract_text_ocr(image=self.file)
            self.content = text
            return self.content



# if __name__ == "__main__":
#     d = DocParser(file='/Users/omniadmin/Desktop/invoice_remittance_project/app/uploads/Scanned Network 312.pdf')
#     text = d.parse_doc()
#     print('*' * 50)
#     print(text)
