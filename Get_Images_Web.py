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


def import_document():
    """Handles document import and directory selection for image extraction."""
    global pdf_file, saved_directory

    # Step 1: File upload (Streamlit file uploader)
    uploaded_file = st.file_uploader("Choose a PDF document", type="pdf", key="pdf_uploader")

    # Check if a file is uploaded
    if uploaded_file is not None:
        # Check if the uploaded file is a valid PDF
        if uploaded_file.type != "application/pdf":
            st.error("Invalid file type. Please upload a PDF document.")
        else:
            pdf_file = uploaded_file
            st.success("File has been successfully uploaded!")

            # Step 2: Directory selection (Input box)
            saved_directory = st.text_input("Enter directory to save images:", key="directory_input")
            
            if saved_directory:
                st.success(f"Images will be saved to: {saved_directory}")

                # Step 3: Extract Images Button (Trigger the extraction)
                if st.button('Extract Images', key="extract_button"):
                    st.write("Extracting images...")

                    # You can add a spinner to show that extraction is in progress
                    with st.spinner('Extracting images...'):
                        # Simulate extraction process (replace with your actual function)
                        extract_images_from_page(pdf_file, 0, saved_directory)  # Trigger extraction
    else:
        # This will show a waiting message until the file is uploaded
        st.info("Please upload a PDF document to proceed.")




# Main function (Streamlit app entry point)
def main():
    import_document()


if __name__ == "__main__":
    main()
