import os
import pdfplumber
import PyPDF2
from urllib.parse import quote
import streamlit as st
from io import StringIO
import pandas as pd

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

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        st.write(bytes_data)

        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)

        # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe)
    # Step 1: File upload (Streamlit file uploader)
    # uploaded_file = st.file_uploader("Choose a file")
    # st.info("Please upload a PDF document to proceed.")
    # # If no file is uploaded yet, show a message prompting the user to upload a file
    # if uploaded_file is not None:
    #     # Now that we know the file is uploaded, check its type
    #     st.success("File has been successfully uploaded!")
    #     pdf_file = uploaded_file  # Save the uploaded file

    #     # Step 2: Directory selection (Input box)
    #     saved_directory = st.text_input("Enter directory to save images:", key="directory_input")
    #     if saved_directory:
    #         st.success(f"Images will be saved to: {saved_directory}")

    #         # Step 3: Extract Images Button (Trigger the extraction)
    #         if st.button('Extract Images', key="extract_button"):
    #             st.write("Extracting images...")
    #             # You can add a spinner to show that extraction is in progress
    #             with st.spinner('Extracting images...'):
    #                 extract_images_from_page(pdf_file, 0, saved_directory)  # Trigger extraction



# Main function (Streamlit app entry point)
def main():
    import_document()

if __name__ == "__main__":
    main()
