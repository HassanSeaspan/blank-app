import streamlit as st
import Get_Images_Web  # This imports your script

# Your Streamlit app code
st.title("🎈 Streamlit Web App with External Script")

# Example: If Get_Images_Web.py has a function `main` that runs the script
if st.button('Run Image Extraction'):
    Get_Images_Web.main()  # Calls the main function from Get_Images_Web.py
