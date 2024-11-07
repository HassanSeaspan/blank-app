import os
import pdfplumber
import PyPDF2
from urllib.parse import quote
import streamlit as st

# Try importing tkinter only if running locally (not in Streamlit Cloud)
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ImportError:
    tkinter = None  # Set tkinter to None if we are in Streamlit Cloud

# Initialize variables to hold the selected directory and file
saved_directory = ""
pdf_file = ""


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def import_document():
    """Handles document import using tkinter locally and Streamlit on cloud."""
    global pdf_file
    if tkinter:
        # Use tkinter for file selection locally
        root = tk.Tk()
        root.withdraw()
        document = filedialog.askopenfilename(
            title="Select a PDF Document",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if document:
            pdf_file = document
            messagebox.showinfo("Success", "File has been successfully retrieved!")
            root.destroy()
            show_directory_prompt()  # Proceed to directory selection
        else:
            messagebox.showinfo("No Selection", "No document selected.")
    else:
        # Use Streamlit's file uploader for cloud
        uploaded_file = st.file_uploader("Choose a PDF document", type="pdf")
        if uploaded_file:
            pdf_file = uploaded_file
            st.success("File has been successfully retrieved!")
            show_directory_prompt()  # Proceed to directory selection


def show_directory_prompt():
    """Handles directory selection using tkinter locally and Streamlit in the cloud."""
    global saved_directory
    if tkinter:
        # Use tkinter for directory selection locally
        dir_window = tk.Tk()
        dir_window.title("Select Directory")
        window_width = 400
        window_height = 100
        center_window(dir_window, window_width, window_height)

        question_label = tk.Label(dir_window, text="Where would you like the images to be saved?", font=("Arial", 12, "bold"))
        question_label.pack(pady=(20, 5))

        select_button = tk.Button(dir_window, text="Select Directory", command=lambda: get_directory(dir_window), width=20)
        select_button.pack(pady=(5, 10))

        dir_window.mainloop()
    else:
        # Use Streamlit's text input for directory in the cloud
        saved_directory = st.text_input("Enter directory to save images:")
        if saved_directory:
            st.success(f"Images will be saved to: {saved_directory}")
            extract_images_from_page(pdf_file, 0, saved_directory)  # Extract images


def get_directory(dir_window):
    """Handles directory selection using tkinter locally."""
    global saved_directory
    directory = filedialog.askdirectory(title="Select a Folder to Save Images")
    if directory:
        if os.path.isdir(directory):
            saved_directory = directory
            messagebox.showinfo("Selected Directory", f"Images will be saved to: {saved_directory}")
            dir_window.destroy()
            extract_images_from_page(pdf_file, 0, saved_directory)  # Extract images
        else:
            messagebox.showerror("Invalid Directory", "The selected path is not a valid directory.")
    else:
        messagebox.showinfo("No Selection", "No directory selected.")


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


def count_pdf_pages(file_path):
    """Returns the number of pages in the provided PDF document."""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return len(reader.pages)


# Main function (needed for Streamlit app)
def main():
    import_document()


if __name__ == "__main__":
    main()
