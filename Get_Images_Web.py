import os
import pdfplumber
import PyPDF2
from urllib.parse import quote
import streamlit as st

# Initialize variables to hold the selected directory and file
saved_directory = ""
pdf_file = ""


def extract_images_from_page(pdf_path, page_num, image_directory):
    """Extracts images from the given PDF page and saves them in the specified directory."""
    image_coordinates = {}  # Dictionary to store image coordinates
    i = 0
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        images = page.images
        if images:
            for img in images:
                x0, y0, x1, y1 = img['x0'], img['top'], img['x1'], img['bottom']
                if x0 < 0:
                    x0 = 0
                if y0 < 0:
                    y0 = 0
                if x1 < 0:
                    x1 = 0
                if y1 < 0:
                    y1 = 0

                height = abs(y1 - y0)
                width = abs(x1 - x0)
                area = height * width
                if area > 5:
                    try:
                        image_data = page.within_bbox((x0, y0, x1, y1)).to_image(resolution=300).original
                        image_filename = os.path.join(image_directory, f"{page_num}_{i}.png")
                        image_data.save(image_filename)

                        # Encode the path to handle spaces and special characters
                        image_path = f'file:///{quote(os.path.abspath(image_filename).replace(os.sep, "/"))}'
                        image_coordinates[i] = {
                            'path': image_path,
                            'coordinates': (x0, y0, x1, y1),
                            'page': page_num + 1
                        }
                        i += 1
                    except Exception as e:
                        print(e)

uploaded_file = None

def import_document():
    """Handles document import and directory selection for image extraction."""
    global pdf_file, saved_directory

    # Display an info message while waiting for file upload
    st.info("Please upload a PDF document to proceed.")

    # Step 1: File upload (Streamlit file uploader)
    pdf_file = st.file_uploader("Choose a PDF document", type="pdf", key="pdf_uploader")
    
    return pdf_file





# Main function (Streamlit app entry point)
def main():
    x = import_document()
    st.success(f"{x} is successfully downloaded")
    


if __name__ == "__main__":
    main()
