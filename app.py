import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import time

# 1. Config & Premium Styling
st.set_page_config(page_title="FinSecure Enterprise", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-bottom: 5px solid #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 130px; display: flex; flex-direction: column; justify-content: center;
        text-align: center; margin-bottom: 20px; transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: scale(1.03); background-color: #f8fafc; }
    .metric-value { font-size: 24px; font-weight: bold; color: #1e3a8a; }
    .metric-label { font-size: 16px; color: #64748b; margin-bottom: 5px; }
    .stApp {background-color: #f1f5f9;}
    .empty-state { text-align: center; color: #94a3b8; padding: 50px; border: 2px dashed #cbd5e1; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ FinSecure Enterprise: Real-Time Fraud Monitor")
st.markdown("---")

# Session Data for tracking transactions
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['ID', 'Amount', 'Status', 'Timestamp'])

# 2. Sidebar Controls
st.sidebar.header("⚙️ System Controls")
run_stream = st.sidebar.button("🚀 Execute Live Monitoring")
status_filter = st.sidebar.multiselect("Filter Data", ["🚨 HIGH RISK (FRAUD)", "✅ LEGIT"])

# CSV Export functionality
csv = st.session_state.history.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Download Logs (CSV)", csv, "transaction_logs.csv", "text/csv")

# 3. Stream Simulation Logic (Dynamic Fraud Logic)
if run_stream:
    progress_bar = st.progress(0)
    for i in range(20):
        # Dynamic Random Logic: प्रत्येक वेळी रँडमली ठरवा (साधारण २०% प्रमाण)
        if np.random.rand() < 0.20:
            amt = float(np.random.uniform(50000, 90000))
            status = "🚨 HIGH RISK (FRAUD)"
        else:
            amt = float(np.random.uniform(100, 40000))
            status = "✅ LEGIT"
        
        # Update Session State
        new_entry = {'ID': 1000 + i, 'Amount': amt, 'Status': status, 'Timestamp': datetime.datetime.now().strftime("%H:%M:%S")}
        st.session_state.history = pd.concat([pd.DataFrame([new_entry]), st.session_state.history], ignore_index=True)
        
        # UI Notifications
        if status == "🚨 HIGH RISK (FRAUD)": st.toast(f'⚠️ ALERT: Fraud Detected on Tx: {1000 + i}', icon='🚨')
        progress_bar.progress((i + 1) / 20)
        time.sleep(0.3)

# 4. KPI Row (Performance Metrics)
if not st.session_state.history.empty:
    total_tx = len(st.session_state.history)
    fraud_count = len(st.session_state.history[st.session_state.history['Status'] == "🚨 HIGH RISK (FRAUD)"])
    secure_count = total_tx - fraud_count
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Transactions</div><div class="metric-value">{total_tx}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Fraud Detected</div><div class="metric-value">{fraud_count}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Secure Transactions</div><div class="metric-value">{secure_count}</div></div>', unsafe_allow_html=True)

# 5. Charts & Logs
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("📊 Distribution")
    if not st.session_state.history.empty:
        st.bar_chart(st.session_state.history['Status'].value_counts())
    else:
        st.markdown('<div class="empty-state">Waiting for Real-Time Stream...<br>Click "Execute" to start</div>', unsafe_allow_html=True)

with col2:
    st.subheader("📋 Transaction Logs")
    df_display = st.session_state.history
    if status_filter: df_display = df_display[df_display['Status'].isin(status_filter)]
    st.dataframe(df_display, use_container_width=True)

st.subheader("📈 Financial Flow Trend")
if not st.session_state.history.empty:
    st.line_chart(st.session_state.history['Amount'])
else:
    st.markdown('<div class="empty-state">No financial data available yet.</div>', unsafe_allow_html=True)
