import os
import pdfplumber
import PyPDF2  # Ensure PyPDF2 is imported
from urllib.parse import quote
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image  # Import Pillow for image handling

# Initialize a variable to hold the selected directory
saved_directory = ""

# Centering function
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def import_document():
    # Open the file explorer dialog to select a PDF document
    document = filedialog.askopenfilename(
        title="Select a PDF Document",
        filetypes=[("PDF Files", "*.pdf")]
    )
    
    if document:
        try:
            with open(document, "r") as file:
                global pdf_file
                pdf_file = document
                messagebox.showinfo("Success", "File has been successfully retrieved!")
            # Close the main window
            root.destroy()
            # Show the directory selection UI
            show_directory_prompt()
        except FileNotFoundError:
            messagebox.showerror("File Not Found", "Error: The file was not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    else:
        messagebox.showinfo("No Selection", "No document selected.")
        
def show_directory_prompt():
    # Create a new window to ask where to save images
    dir_window = tk.Tk()  # Use a new Tk instance for the directory prompt
    dir_window.title("Select Directory")
    window_width = 400
    window_height = 100
    center_window(dir_window, window_width, window_height)

    question_label = tk.Label(dir_window, text="Where would you like the images to be saved?", font=("Arial", 12, "bold"))
    question_label.pack(pady=(20, 5))

    # Button to select directory
    select_button = tk.Button(dir_window, text="Select Directory", command=lambda: get_directory(dir_window), width=20)
    select_button.pack(pady=(5,10))

    # Start the directory window's main loop
    dir_window.mainloop()
    
def get_directory(dir_window):
    global saved_directory  # Use the global variable to save the directory
    # Open a dialog to select a directory
    directory = filedialog.askdirectory(title="Select a Folder to Save Images")
    
    if directory:
        # Check if the selected directory exists
        if os.path.isdir(directory):
            global saved_directory
            saved_directory = directory  # Save the selected directory
            messagebox.showinfo("Selected Directory", f"Images will be saved to: {saved_directory}")
            dir_window.destroy()
        else:
            messagebox.showerror("Invalid Directory", "The selected path is not a valid directory.")
    else:
        messagebox.showinfo("No Selection", "No directory selected.")
    
# Create the main window
root = tk.Tk()
root.title("Document Importer")
window_width = 400
window_height = 100

center_window(root, window_width, window_height)

# Create a label for the document question
question_label = tk.Label(root, text="Please select a PDF document to import:", font=("Arial", 12, "bold"))
question_label.pack(pady=(20, 5))

# Create and place the import document button
import_button = tk.Button(root, text="Import Here", command=import_document, width=20)
import_button.pack(pady=(5, 10))

# Start the GUI main loop
root.mainloop()

def extract_images_from_page(pdf_path, page_num, image_directory):
    image_coordinates = {}  # Dictionary to store image coordinates
    i= 0
    with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_num]
            images = page.images
            if images:
                for img in images:
                    print(len(images))
                    x0, y0, x1, y1 = img['x0'], img['top'], img['x1'], img['bottom']
                    print(f"Page {page_num + 1}: Image found at ({x0}, {y0}, {x1}, {y1})")
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
                            
                            print(f"Saved image: {image_filename}")
                            image_coordinates[i] = {
                                'path': image_path,  # Convert path to a file URL            # Store the path of the saved image
                                'coordinates': (x0, y0, x1, y1),   # Store coordinates
                                'page': page_num + 1    # Store page number (1-based index)
                            }
                            i += 1
                        except Exception as e:
                            print(e)

            else:
                print(f"Page {page_num + 1}: Image NOT found")
def main():
    pdf_path = pdf_file
    image_directory = saved_directory

    # Ensure the image directory exists
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)

    page_count = count_pdf_pages(pdf_path)

    extract_images_from_page(pdf_path, 0, image_directory)

def count_pdf_pages(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return len(reader.pages)

if __name__ == "__main__":
    main()