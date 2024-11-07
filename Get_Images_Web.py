import os
import pdfplumber
import tempfile
import streamlit as st
from urllib.parse import quote
from PIL import Image

# Initialize variables to hold the selected directory and file
saved_directory = ""
pdf_file = ""

def extract_images_from_page(pdf_path, page_num, image_directory):
    """Extract images from a given PDF page and save them."""
    image_coordinates = {}  # Dictionary to store image coordinates
    i = 0

    # Open the PDF file using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        images = page.images

        if images:
            for img in images:
                x0, y0, x1, y1 = img['x0'], img['top'], img['x1'], img['bottom']

                # Ensure coordinates are within bounds
                x0, y0, x1, y1 = max(x0, 0), max(y0, 0), max(x1, 0), max(y1, 0)

                height = abs(y1 - y0)
                width = abs(x1 - x0)
                area = height * width

                # Extract the image if it is large enough
                if area > 5:
                    try:
                        # Extract the image from the specified bounding box
                        image_data = page.within_bbox((x0, y0, x1, y1)).to_image(resolution=300).original

                        # Save the image as PNG
                        image_filename = os.path.join(image_directory, f"{page_num}_{i}.png")
                        image_data.save(image_filename)  # Save using PIL's save method

                        # Create a file URL
                        image_path = f'file:///{quote(os.path.abspath(image_filename).replace(os.sep, "/"))}'

                        print(f"Saved image: {image_filename}")

                        # Store image path and coordinates
                        image_coordinates[i] = {
                            'path': image_path,
                            'coordinates': (x0, y0, x1, y1),
                            'page': page_num + 1
                        }
                        i += 1
                    except Exception as e:
                        print(f"Error extracting image: {e}")
        else:
            print(f"Page {page_num + 1}: No images found")

    return image_coordinates


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
            # Save the uploaded file temporarily
            pdf_path = save_uploaded_file(uploaded_file)
            st.success(f"File has been successfully uploaded and saved to: {pdf_path}")

            # Step 2: Directory selection (Input box)
            saved_directory = st.text_input("Enter directory to save images:", key="directory_input")
            if saved_directory:
                st.success(f"Images will be saved to: {saved_directory}")

                # Step 3: Extract Images Button (Trigger the extraction)
                if st.button('Extract Images', key="extract_button"):
                    st.write(f"Extracting images from {pdf_path}...")
                    image_coordinates = extract_images_from_page(pdf_path, 0, saved_directory)

                    # Show the extracted image coordinates for verification
                    if image_coordinates:
                        st.write("Extracted images:")
                        for i, data in image_coordinates.items():
                            st.write(f"Image {i}: {data['path']} at coordinates {data['coordinates']} on page {data['page']}")
                    else:
                        st.write("No images were found on the page.")
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
