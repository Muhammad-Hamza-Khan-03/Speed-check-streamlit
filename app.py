import streamlit as st
import speedtest
import plotly.graph_objects as go
import psutil
from datetime import datetime
import pandas as pd
import time
import threading
import requests
import socket

# Page Config and Custom CSS Styling
st.set_page_config(page_title="Advanced WiFi Speed Checker", layout="wide")

# Section Headers
st.markdown("<div class='title'>📊 Advanced WiFi Speed Checker</div>", unsafe_allow_html=True)

# Intro
st.write("Measure download, upload speeds, diagnose network issues, and track device usage.")

# Initialize Speedtest instance
st_test = speedtest.Speedtest()

# Sidebar Settings
st.sidebar.header("Settings")
selected_server_id = st.sidebar.selectbox("Choose Server", options=['Auto', 'Manual'])
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", min_value=1, max_value=10, value=2)

# IP and Location Info
def get_ip_location():
    try:
        ip = requests.get('https://api64.ipify.org?format=json').json()['ip']
        location = requests.get(f'http://ip-api.com/json/{ip}').json()
        return ip, location
    except:
        return None, None

ip, location = get_ip_location()
if ip:
    st.sidebar.subheader("Network Info")
    st.sidebar.write(f"Public IP: {ip}")
    st.sidebar.write(f"Location: {location.get('city')}, {location.get('country')}")
    st.sidebar.write(f"ISP: {location.get('isp')}")

# Speed Test Function
def check_speed():
    st_test.get_best_server()
    download = round(st_test.download() / 1_000_000, 2)
    upload = round(st_test.upload() / 1_000_000, 2)
    ping = st_test.results.ping
    return download, upload, ping

# Device Usage Monitor (Real-time data usage per process)
def device_usage():
    usage = {p.name(): p.memory_info().rss / 1024**2 for p in psutil.process_iter(['name'])}
    return sorted(usage.items(), key=lambda x: x[1], reverse=True)[:5]

# Network History Tracking
download_speeds, upload_speeds, pings, timestamps = [], [], [], []

# Containers for Real-time Speed Check
st.header("Start Speed Test")
download_gauge = st.empty()
upload_gauge = st.empty()
history_chart = st.empty()

# Function to update gauges and chart
def update_charts():
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
    history_chart.plotly_chart(fig)

# Start Speed Test Button
if st.button("Run Speed Test"):
    while True:
        update_charts()
        time.sleep(refresh_rate)

# Device Usage
st.subheader("Top Device Data Usage (MB)")
for process, usage in device_usage():
    st.write(f"{process}: {usage:.2f} MB")

# ISP Plan Comparison
st.sidebar.subheader("ISP Plan Comparison")
st.sidebar.write("Enter your plan speeds:")
isp_download = st.sidebar.number_input("Download Speed (Mbps)", value=100.0)
isp_upload = st.sidebar.number_input("Upload Speed (Mbps)", value=50.0)

# Alerts for ISP Comparison
if download_speeds and any(d < 0.8 * isp_download for d in download_speeds[-3:]):
    st.warning("Download speed below 80% of ISP Plan!")
if upload_speeds and any(u < 0.8 * isp_upload for u in upload_speeds[-3:]):
    st.warning("Upload speed below 80% of ISP Plan!")
