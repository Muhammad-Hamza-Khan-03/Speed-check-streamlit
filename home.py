import streamlit as st
import time
from PIL import Image

# Page Config and Custom CSS Styling
# st.set_page_config(page_title="Enhanced WiFi Speed Checker", layout="wide")

# Custom CSS for styling
def home():
    st.markdown("""
        <style>
            .title {
                font-size: 3rem;
                font-weight: bold;
                color: #2c3e50;
                text-align: center;
                margin-bottom: 2rem;
            }
            .intro-text {
                font-size: 1.1rem;
                color: #34495e;
                text-align: center;
                margin-bottom: 2rem;
                line-height: 1.6;
            }
            .call-to-action {
                font-size: 1.2rem;
                text-align: center;
                color: #2980b9;
                margin-top: 2rem;
                font-weight: bold;
            }
            .feature {
                font-size: 1.1rem;
                color: #34495e;
                text-align: left;
                margin: 1rem;
            }
            .stButton > button {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.5rem 1rem;
                font-size: 1rem;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                background-color: #2980b9;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                transform: translateY(-2px);
            }
            .animated-background {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #3498db, #9b59b6);
                animation: background-animation 10s infinite linear;
                z-index: -1;
            }
            @keyframes background-animation {
                0% { background-position: 0 0; }
                100% { background-position: 100% 100%; }
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Add an animated background for cool visuals
    st.markdown('<div class="animated-background"></div>', unsafe_allow_html=True)
    # image = Image.open('signals.jpg')  # Replace with the correct path to your image
    # st.image(image, caption="Internet Speed Test in Action", use_column_width=True)
    image = "speed.svg"  # Replace with the correct path to your SVG image
    st.image(image, caption="Internet Speed Test in Action", use_column_width=True)
    # Main title
    st.markdown("<div class='title'>Welcome to the Enhanced WiFi Speed Checker</div>", unsafe_allow_html=True)
    
    # Introduction text
    st.markdown("""
        <div class="intro-text">
            This app helps you test your internet speed in real-time and visualize the results. Whether you're troubleshooting your WiFi, monitoring connection performance, or just curious about your internet speeds, this tool makes it easy and interactive!
        </div>
    """, unsafe_allow_html=True)
    
    # Fun animation or progress bar while showing the features
    with st.spinner('Loading cool features...'):
        time.sleep(1)
    
    # Call to Action Button
    st.markdown("<div class='call-to-action'>Test Your Speed Now and See Real-Time Results!</div>", unsafe_allow_html=True)
    
    # Feature List - Display features vertically
    st.markdown("<div class='feature'>", unsafe_allow_html=True)
    
    st.markdown("""
        <h4 style="color: #2980b9;">Speed Test</h4>
        <p>Instantly check your download and upload speeds in Mbps.</p>
        <hr>
        <h4 style="color: #2980b9;">History Tracking</h4>
        <p>Keep track of your internet speed over time with dynamic charts.</p>
        <hr>
        <h4 style="color: #2980b9;">Server Selection</h4>
        <p>Choose a server manually or let the app auto-select the best one.</p>
        <hr>
        <h4 style="color: #2980b9;">Location Information</h4>
        <p>See your public IP, location, and ISP details for better insight.</p>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Optional: Add an image to make the homepage more visually appealing
    
    # Footer with links to other pages or sections
    
    
    # Button to navigate to the next page (Speed Test page)
    st.button("Go to Speed Test", on_click=lambda: st.experimental_rerun())
