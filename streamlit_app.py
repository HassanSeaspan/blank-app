import streamlit as st
import Get_Images_Web  # This imports your script
import pandas as pd
from io import StringIO

# Your Streamlit app code
st.title("🎈 Streamlit Web App with External Script")

# Example: If Get_Images_Web.py has a function `main` that runs the script
if st.button('Run Image Extraction'):
    # import_document()
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
    # Get_Images_Web.main()  # Calls the main function from Get_Images_Web.py
