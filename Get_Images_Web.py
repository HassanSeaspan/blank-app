import os
import pdfplumber
import PyPDF2
from urllib.parse import quote
import streamlit as st
import tempfile

# Initialize variables to hold the selected directory and file
saved_directory = ""
pdf_file = ""

def extract_images_from_page(pdf_path, page_num, image_directory):
    image_coordinates = {}  # Dictionary to store image coordinates
    i = 0

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        images = page.images

        if images:
            for img in images:
                x0, y0, x1, y1 = img['x0'], img['top'], img['x1'], img['bottom']
                print(f"Page {page_num + 1}: Image found at ({x0}, {y0}, {x1}, {y1})")
                
                # Validate coordinates
                if x0 < 0: x0 = 0
                if y0 < 0: y0 = 0
                if x1 < 0: x1 = 0
                if y1 < 0: y1 = 0

                height = abs(y1 - y0)
                width = abs(x1 - x0)
                area = height * width

                if area > 5:  # Ensure there is a valid area to extract
                    try:
                        image_data = page.within_bbox((x0, y0, x1, y1)).to_image(resolution=300).original
                        if image_data:
                            # Ensure the directory exists
                            if not os.path.exists(image_directory):
                                os.makedirs(image_directory)

                            # Save the image data to a file
                            image_filename = os.path.join(image_directory, f"{page_num}_{i}.png")
                            image_data.save(image_filename)  # Save using PIL's save method

                            # Convert backslashes to forward slashes for the path
                            image_path = image_filename.replace(os.sep, "/")

                            print(f"Saved image: {image_path}")
                            st.success(f"Saved image: {image_path}")
                            
                            # Store the image coordinates and path
                            image_coordinates[i] = {
                                'path': image_path,  # Keep the path in the desired format
                                'coordinates': (x0, y0, x1, y1),  # Store coordinates
                                'page': page_num + 1  # 1-based page index
                            }
                            i += 1
                        else:
                            print("No image data extracted.")
                    except Exception as e:
                        print(f"Error saving image: {e}")
        else:
            print(f"Page {page_num + 1}: Image NOT found")


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
                        extract_images_from_page(pdf_file, 0, saved_directory)  # Trigger extraction
        else:
            st.warning("Please upload a PDF document.")

    except FileNotFoundError:
        st.error("Error: The file was not found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")



# Main function (Streamlit app entry point)
def main():
    import_document()


if __name__ == "__main__":
    main()
