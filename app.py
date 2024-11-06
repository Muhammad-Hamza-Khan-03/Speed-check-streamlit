import streamlit as st
import speedtest
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import time
import threading
import requests
import socket

# Page Config and Custom CSS Styling
st.set_page_config(page_title="Real-Time Speed Checker", layout="wide")

st.markdown(
    """
    <style>
    .title {
        font-size: 36px;
        color: #FF6347;
        text-align: center;
        font-weight: bold;
        margin-top: -20px;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #FF6347;
        color: white;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        height: 45px;
    }
    .stButton>button:hover {
        background-color: #FF4500;
    }
    .gauge-container {
        text-align: center;
    }
    .history-container {
        padding-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">📊 Real-Time Internet Speed Checker</div>', unsafe_allow_html=True)

# Intro
st.write("Measure your download and upload speeds in real-time and track the results over time with custom settings.")

# Initialize speed test instance
st_test = speedtest.Speedtest()

# Speed Test Server Selection
st.sidebar.header("Settings")
st.sidebar.subheader("Choose Speed Test Server")

# Fetch and show available servers
try:
    servers = st_test.get_servers()
    server_list = {}
    
    # Building a list of server IDs and their names
    for server_group in servers.values():
        for server in server_group:
            server_list[server['id']] = server['sponsor'] + " - " + server['name']
    
    # Dropdown to select server by ID
    selected_server_id = st.sidebar.selectbox("Server", options=list(server_list.keys()), format_func=lambda x: server_list[x])
    
except Exception as e:
    st.error(f"Error loading servers: {e}")
    servers = None
    selected_server_id = None

# Fetch public IP address and location
def get_ip_and_location():
    try:
        ip_info = requests.get('https://api64.ipify.org?format=json').json()
        ip = ip_info['ip']
        
        # Get location info via ip-api.com
        location_info = requests.get(f'http://ip-api.com/json/{ip}').json()
        city = location_info.get('city', 'N/A')
        region = location_info.get('regionName', 'N/A')
        country = location_info.get('country', 'N/A')
        isp = location_info.get('isp', 'N/A')
        return ip, city, region, country, isp
    except Exception as e:
        st.error(f"Could not fetch IP or location: {e}")
        return None, None, None, None, None


# Get Local IP address (private IP)
def get_local_ip():
    return socket.gethostbyname(socket.gethostname())

# Display the IP and Location Info
ip, city, region, country, isp = get_ip_and_location()
local_ip = get_local_ip()

if ip:
    st.sidebar.subheader("Your IP and Location")
    st.sidebar.write(f"IP: {ip}")
    st.sidebar.write(f"City: {city}")
    st.sidebar.write(f"Region: {region}")
    st.sidebar.write(f"Country: {country}")
    st.sidebar.write(f"ISP: {isp}")
   

# User-defined refresh rate
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", min_value=1, max_value=10, value=5)

# Function to get speeds
def check_speed():
    # Verify if the server is available
    if servers and selected_server_id in server_list:
        st_test.get_best_server([server for server_group in servers.values() for server in server_group if server['id'] == selected_server_id])
    download_speed = round(st_test.download() / 1_000_000, 2)  # Convert to Mbps
    upload_speed = round(st_test.upload() / 1_000_000, 2)
    ping = st_test.results.ping  # Ping (in ms)
    return download_speed, upload_speed, ping

# Create gauge chart
def create_gauge_chart(speed, title, gauge_max=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=speed,
        title={'text': title, 'font': {'size': 24}},
        gauge={'axis': {'range': [0, gauge_max]},
               'bar': {'color': "#FF6347"},
               'steps': [
                   {'range': [0, gauge_max * 0.5], 'color': "lightgray"},
                   {'range': [gauge_max * 0.5, gauge_max], 'color': "gray"}]}
    ))
    fig.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
    return fig

# Real-time data setup
download_speeds = []
upload_speeds = []
ping_values = []
timestamps = []

# UI setup
toggle_button = st.button("Start Speed Test")

col1, col2 = st.columns(2)

# Display gauge charts
download_gauge = col1.empty()
upload_gauge = col2.empty()

# Initialize bar chart placeholders
st.subheader("Speed History")
history_chart = st.empty()

# Global flag to control the running state
if 'running' not in st.session_state:
    st.session_state.running = False

# Toggle start/stop button
def toggle_test():
    if st.session_state.running:
        st.session_state.running = False
    else:
        st.session_state.running = True
        start_thread()

def start_thread():
    """Start the speed test in a new thread."""
    with st.spinner("Running Speed Test... Please wait!"):
        while st.session_state.running:
            # Get speed measurements
            download_speed, upload_speed, ping = check_speed()
            
            # Append data to lists
            download_speeds.append(download_speed)
            upload_speeds.append(upload_speed)
            ping_values.append(ping)
            timestamps.append(datetime.now().strftime("%H:%M:%S"))
            
            # Update gauges
            download_gauge.plotly_chart(create_gauge_chart(download_speed, "Download Speed (Mbps)"), use_container_width=True,width=500,height = 300)
            upload_gauge.plotly_chart(create_gauge_chart(upload_speed, "Upload Speed (Mbps)"), use_container_width=True,width=500,height = 300)
            
            # Display best connectivity (ping)
            st.sidebar.write(f"Best Connectivity (Ping): {ping} ms")
            
            # Update history bar chart with latest data
            df = pd.DataFrame({'Timestamp': timestamps, 'Download Speed (Mbps)': download_speeds, 'Upload Speed (Mbps)': upload_speeds})
            df.set_index('Timestamp', inplace=True)
            
            # Create bar chart for the history
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df.index, y=df['Download Speed (Mbps)'], name='Download Speed (Mbps)', marker_color='blue'))
            fig.add_trace(go.Bar(x=df.index, y=df['Upload Speed (Mbps)'], name='Upload Speed (Mbps)', marker_color='orange'))
            
            # Update layout and display
            fig.update_layout(
                barmode='group',
                title="Speed Test History (Last Few Tests)",
                xaxis_title="Timestamp",
                yaxis_title="Speed (Mbps)",
                xaxis_tickangle=45,
                template="plotly_dark"
            )
            history_chart.plotly_chart(fig)

            # Wait before the next speed check
            time.sleep(refresh_rate/10)

# When the button is clicked, toggle the test state and thread
toggle_button and toggle_test()
