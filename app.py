import streamlit as st
import speedtest
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import time
import threading
import requests
import socket

try:
    from pywifi import PyWiFi, const
except ImportError:
    st.error("PyWiFi library is not installed. Run `pip install pywifi` to enable Wi-Fi connectivity features.")

# Page Config and Custom CSS Styling
st.set_page_config(page_title="Test Your Internet Speed", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
    }
    .stButton > button {
        background-color: #3498db;
        color: white;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📊 Real-Time Internet Speed Checker with Wi-Fi Connector</div>', unsafe_allow_html=True)

# Initialize Speed Test instance
st_test = speedtest.Speedtest()

# Sidebar for settings and Wi-Fi connector
st.sidebar.header("Settings")
st.sidebar.subheader("Choose Speed Test Server")

# Fetch available servers
try:
    servers = st_test.get_servers()
    server_list = {s['id']: s['sponsor'] + " - " + s['name'] for s_list in servers.values() for s in s_list}
    selected_server_id = st.sidebar.selectbox("Server", options=list(server_list.keys()), format_func=lambda x: server_list[x])
except Exception as e:
    st.error(f"Error loading servers: {e}")
    servers, selected_server_id = None, None

# Fetch public IP and location
def get_ip_and_location():
    try:
        ip = requests.get('https://api64.ipify.org?format=json').json()['ip']
        loc = requests.get(f'http://ip-api.com/json/{ip}').json()
        return ip, loc.get('city', 'N/A'), loc.get('regionName', 'N/A'), loc.get('country', 'N/A'), loc.get('isp', 'N/A')
    except:
        return None, None, None, None, None

ip, city, region, country, isp = get_ip_and_location()
if ip:
    st.sidebar.write(f"IP: {ip}\nCity: {city}\nRegion: {region}\nCountry: {country}\nISP: {isp}")

# User-defined refresh rate
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", min_value=1, max_value=10, value=2)

# Wi-Fi Connection and Connected Network Stats
def get_wifi_networks():
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(2)
    scan_results = iface.scan_results()
    networks = [{"ssid": network.ssid, "signal": network.signal} for network in scan_results if network.ssid]
    return sorted(networks, key=lambda x: x["signal"], reverse=True)

def connect_to_wifi(ssid, password=""):
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]
    profile = wifi.Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password
    iface.remove_all_network_profiles()
    iface.add_network_profile(profile)
    iface.connect(iface.add_network_profile(profile))
    time.sleep(5)
    return iface.status() == const.IFACE_CONNECTED

def get_connected_network_info():
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]
    if iface.status() == const.IFACE_CONNECTED:
        connected_network = iface.network_profiles()[0]  # Retrieves the first profile (active)
        ssid = connected_network.ssid
        signal = iface.scan_results()[0].signal  # Retrieves signal strength
        return ssid, signal
    return None, None

st.sidebar.subheader("Connected Network Stats")
ssid, signal = get_connected_network_info()
if ssid:
    st.sidebar.write(f"Connected SSID: {ssid}")
    st.sidebar.write(f"Signal Strength: {signal}%")
else:
    st.sidebar.write("No active Wi-Fi connection detected.")

st.sidebar.subheader("Wi-Fi Connector")
try:
    wifi_networks = get_wifi_networks()
    for network in wifi_networks:
        st.sidebar.write(f"{network['ssid']} - Signal: {network['signal']}")
        if st.sidebar.button(f"Connect to {network['ssid']}"):
            password = st.sidebar.text_input(f"Enter password for {network['ssid']}", type="password")
            if connect_to_wifi(network['ssid'], password):
                st.sidebar.success(f"Connected to {network['ssid']}")
            else:
                st.sidebar.error(f"Failed to connect to {network['ssid']}")
except:
    st.sidebar.error("Could not retrieve Wi-Fi networks. Ensure pywifi is installed and compatible with your device.")

# Speed Test and History Tracking
download_speeds, upload_speeds, ping_values, timestamps = [], [], [], []

def check_speed():
    st_test.get_best_server([s for s_list in servers.values() for s in s_list if s['id'] == selected_server_id])
    return round(st_test.download() / 1_000_000, 2), round(st_test.upload() / 1_000_000, 2), st_test.results.ping

def create_gauge_chart(speed, title, gauge_max=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=speed,
        title={'text': title},
        gauge={'axis': {'range': [0, gauge_max]}, 'bar': {'color': "#3B82F6"}}
    ))
    fig.update_layout(height=200, width=250, paper_bgcolor="white")
    return fig

st.header("Start Speed Test")
toggle_button = st.button("Click Here to Start or Stop")

# Line Chart for Historical Data
st.subheader("Speed History")
history_chart = st.empty()

if 'running' not in st.session_state:
    st.session_state.running = False

def toggle_test():
    st.session_state.running = not st.session_state.running
    if st.session_state.running:
        run_speed_test()

def run_speed_test():
    while st.session_state.running:
        download_speed, upload_speed, ping = check_speed()
        download_speeds.append(download_speed)
        upload_speeds.append(upload_speed)
        ping_values.append(ping)
        timestamps.append(datetime.now().strftime("%H:%M:%S"))
        
        # Gauge Charts
        col1, col2 = st.columns(2)
        col1.plotly_chart(create_gauge_chart(download_speed, "Download Speed (Mbps)"), use_container_width=True)
        col2.plotly_chart(create_gauge_chart(upload_speed, "Upload Speed (Mbps)"), use_container_width=True)
        
        # Line Chart for Historical Data
        df = pd.DataFrame({
            'Timestamp': timestamps, 
            'Download Speed': download_speeds, 
            'Upload Speed': upload_speeds
        }).set_index('Timestamp')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Download Speed'], name='Download Speed (Mbps)', line=dict(color='royalblue')))
        fig.add_trace(go.Scatter(x=df.index, y=df['Upload Speed'], name='Upload Speed (Mbps)', line=dict(color='orange')))
        fig.update_layout(title="Speed Test History", xaxis_title="Time", yaxis_title="Speed (Mbps)", template="plotly_dark")
        history_chart.plotly_chart(fig)

        time.sleep(refresh_rate)

toggle_button and toggle_test()
