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
st.set_page_config(page_title="Enhanced WiFi Speed Checker", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        .title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 2rem;
        }
        .start-button {
            display: flex;
            justify-content: center;
            margin-top: 1rem;
            margin-bottom: 2rem;
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
    </style>
""", unsafe_allow_html=True)

# Main title
st.markdown("<div class='title'>Internet Speed Checker</div>", unsafe_allow_html=True)

# Initialize Speedtest
st_test = speedtest.Speedtest()

# Sidebar configuration
st.sidebar.header("Settings")
server_mode = st.sidebar.radio("Server Selection Mode", ["Auto", "Manual"])

# Fetch public IP address and location info
def get_ip_and_location():
    try:
        ip_info = requests.get('https://api64.ipify.org?format=json').json()
        ip = ip_info['ip']
        
        # Get location info
        location_info = requests.get(f'http://ip-api.com/json/{ip}').json()
        city = location_info.get('city', 'N/A')
        region = location_info.get('regionName', 'N/A')
        country = location_info.get('country', 'N/A')
        isp = location_info.get('isp', 'N/A')
        return ip, city, region, country, isp
    except:
        return None, None, None, None, None

# Fetch connected WiFi network name (only for local network)
def get_connected_wifi():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        return local_ip
    except:
        return "Unavailable"

# Display IP and Location Info
ip, city, region, country, isp = get_ip_and_location()
local_ip = get_connected_wifi()
if ip:
    st.sidebar.subheader("Your IP and Location")
    st.sidebar.write(f"Public IP: {ip}")
    st.sidebar.write(f"Local IP: {local_ip}")
    st.sidebar.write(f"Location: {city}, {region}, {country}")
    st.sidebar.write(f"ISP: {isp}")

# Server Selection Dropdown based on server mode
if server_mode == "Manual":
    try:
        servers = st_test.get_servers()
        server_list = {server['id']: f"{server['sponsor']} - {server['name']}" for server_group in servers.values() for server in server_group}
        selected_server_id = st.sidebar.selectbox("Select Server", options=list(server_list.keys()), format_func=lambda x: server_list[x])
    except Exception as e:
        st.error(f"Could not load servers: {e}")
else:
    st_test.get_best_server()
    selected_server_id = st_test.results.server['id']

# Speed Check Function
def check_speed():
    if server_mode == "Manual" and selected_server_id:
        # Use manually selected server
        best_server = [s for group in servers.values() for s in group if s['id'] == selected_server_id]
        st_test.get_best_server(best_server)
    download = round(st_test.download() / 1_000_000, 2)
    upload = round(st_test.upload() / 1_000_000, 2)
    ping = st_test.results.ping
    return download, upload, ping

# Initial gauge charts for download and upload
def empty_gauge_chart(title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=0,
        title={'text': title},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#e0e0e0"}}
    ))
    fig.update_layout(height=200, width=250, margin=dict(t=0, b=0, l=0, r=0))
    return fig

download_gauge = st.empty()
upload_gauge = st.empty()
download_gauge.plotly_chart(empty_gauge_chart("Download Speed (Mbps)"), use_container_width=True)
upload_gauge.plotly_chart(empty_gauge_chart("Upload Speed (Mbps)"), use_container_width=True)

# History Tracking
download_speeds, upload_speeds, pings, timestamps = [], [], [], []

# Toggle Start/Stop Button
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
def toggle_button():
    st.session_state.is_running = not st.session_state.is_running
start_button = st.button("Start" if not st.session_state.is_running else "Stop", on_click=toggle_button)

# Update gauge and history chart in real-time
def update_charts():
    while st.session_state.is_running:
        download, upload, ping = check_speed()
        download_speeds.append(download)
        upload_speeds.append(upload)
        pings.append(ping)
        timestamps.append(datetime.now().strftime("%H:%M:%S"))

        # Update gauges
        download_gauge.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=download,
            title={'text': "Download Speed (Mbps)"}
        )), use_container_width=True)

        upload_gauge.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=upload,
            title={'text': "Upload Speed (Mbps)"}
        )), use_container_width=True)

        # Update history chart
        df = pd.DataFrame({"Time": timestamps, "Download": download_speeds, "Upload": upload_speeds})
        fig = go.Figure(data=[
            go.Scatter(x=df['Time'], y=df['Download'], mode='lines', name="Download", line=dict(color='blue')),
            go.Scatter(x=df['Time'], y=df['Upload'], mode='lines', name="Upload", line=dict(color='orange'))
        ])
        fig.update_layout(title="Speed Test History", xaxis_title="Time", yaxis_title="Speed (Mbps)")
        st.plotly_chart(fig)
        # time.sleep(1)

# Run the test in real-time when button is toggled
if st.session_state.is_running:
    update_charts()