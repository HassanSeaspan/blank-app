import os
import pdfplumber
import PyPDF2
from urllib.parse import quote
import streamlit as st
import tempfile
from PIL import Image  # Import Pillow for image handling
from io import BytesIO

# Initialize variables to hold the selected directory and file
saved_directory = ""
pdf_file = ""

def extract_images_from_page(pdf_path, page_num, image_directory):
    image_coordinates = {}  # Dictionary to store image coordinates
    i= 0
    with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_num]
            images = page.images
            if images:
                for img in images:
                    st.info(f"There are {len(images)} imgs")
                    x0, y0, x1, y1 = img['x0'], img['top'], img['x1'], img['bottom']
                    st.info(f"Page {page_num + 1}: Image found at ({x0}, {y0}, {x1}, {y1})")
                    # image_key = f'image_{index + 1}'
                    
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
                    # if x0 < 0 or x1 < 0 or y0 < 0 or y1 < 0:
                        # Extract the image data directly from the img dictionary
                    if area > 5:
                        try:
                            image_data = page.within_bbox((x0, y0, x1, y1)).to_image(resolution=300).original
                            
                            # Save the image data to a file
                            image_filename = os.path.join(image_directory, f"{page_num}_{i}.png")  # Unique filename
                            image_data.save(image_filename)  # Save using PIL's save method

                            # Encode the path to handle spaces and special characters
                            image_path = f'file:///{quote(os.path.abspath(image_filename).replace(os.sep, "/"))}'
                            
                            st.success(f"Saved image: {image_filename}")
                            image_coordinates[i] = {
                                'path': image_path,  # Convert path to a file URL            # Store the path of the saved image
                                'coordinates': (x0, y0, x1, y1),   # Store coordinates
                                'page': page_num + 1    # Store page number (1-based index)
                            }
                            i += 1
                        except Exception as e:
                            st.error(e)

            else:
                st.error(f"Page {page_num + 1}: Image NOT found")


def save_uploaded_file(uploaded_file):
    """Save the uploaded file temporarily and return the file path."""
    # Create a temporary directory to save the uploaded file
    temp_dir = tempfile.mkdtemp()

    # Define the file path where the uploaded file will be saved
    temp_file_path = os.path.join(temp_dir, uploaded_file.name)

    # Save the file to the temporary directory
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return temp_file_path

def import_document():
    """Handles document import and directory selection for image extraction."""
    global pdf_file, saved_directory

    # Step 1: File upload (Streamlit file uploader)
    try:
        uploaded_file = st.file_uploader("Choose a PDF document", type="pdf", key="pdf_uploader")
        
        if uploaded_file:
            # Check if the uploaded file is a valid PDF
            if uploaded_file.type != "application/pdf":
                st.error("Invalid file type. Please upload a PDF document.")
            else:
                pdf_file = save_uploaded_file(uploaded_file)
                
                # Step 3: Provide a download button for the user to download the temp file
                with open(pdf_file, "rb") as f:
                    file_data = f.read()
                
                st.download_button(
                    label="Download temporary file",
                    data=file_data,
                    file_name=uploaded_file.name,
                    mime="application/pdf"
                )
                
                # pdf_file = uploaded_file
                st.success("File has been successfully uploaded!")

                # Step 2: Directory selection (Input box)
                saved_directory = st.text_input("Enter directory to save images:", key="directory_input")
                if saved_directory:
                    st.success(f"Images will be saved to: {saved_directory}")

                    # Step 3: Extract Images Button (Trigger the extraction)
                    if st.button('Extract Images', key="extract_button"):
                        st.write(f"Extracting images from {pdf_file}")
                        page_count = count_pdf_pages(pdf_file)
                        for page_num in range(0, page_count):
                            extract_images_from_page(pdf_file, page_num, saved_directory)  # Trigger extraction
        else:
            st.warning("Please upload a PDF document.")

    except FileNotFoundError:
        st.error("Error: The file was not found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def count_pdf_pages(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return len(reader.pages)

# Main function (Streamlit app entry point)
def main():
    import_document()


if __name__ == "__main__":
    main()
# import streamlit as st
# from PIL import Image, UnidentifiedImageError
# from io import BytesIO
# import os
# from pathlib import Path

# @st.cache
# def load_image(image_file):
#     # st.info("Now that we installed the libraries:")
#     # try:
#     #     # Open the image file
#     #     img = Image.open(image_file)
#     #     st.success("The uploaded file is not a valid image or is corrupted.")
#     #     return img
#     # except UnidentifiedImageError:
#     #     st.error("The uploaded file is not a valid image or is corrupted.")
#     #     return None
#     img = Image.open(image_file)  # Convert to BytesIO explicitly
#     return img

# def main():
#     st.title("Welcome! Here you can extract all the images from a pdf file....")
    
#     menu = ["Home", "Dataset", "About"]
#     choice = st.sidebar.selectbox("Menu", menu)
    
#     if choice == "Home":
#         st.subheader("Upload Images")
#         image_file = st.file_uploader("Upload An Image", type=['jpeg', 'png', 'jpg'])
        
#         if image_file is not None:
#             # Check current working directory for debugging
#             # Display file details
#             file_details = {"FileName": image_file.name, "FileType": image_file.type}
#             st.write(file_details)
            
#             # Load and display the image
#             img = load_image(image_file)
#             # st.image(img,height=250,width=250)
#             st.image(img, use_column_width=True, width=100)
#             # st.image(img, caption="Uploaded Image", use_column_width=True, width=100)
            
#             with open(image_file.name, "wb") as f:
#                 f.write(image_file.getbuffer())

            
# if __name__ == "__main__":
#     main()
