# main.py
import streamlit as st
import app
import home
from home import *
from app import *

# st.set_page_config(page_title="Enhanced WiFi Speed Checker", layout="centered")

# Sidebar navigation
PAGES = {
    "Home": home,
    "Speed Test": app
}

# Sidebar menu
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# Display the selected page
page = PAGES[selection]
page()
