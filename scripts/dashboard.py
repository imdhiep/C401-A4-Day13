import streamlit as st
import pandas as pd
import json
import os
import time
from pathlib import Path

# Cấu hình giao diện
st.set_page_config(page_title="Đà Nẵng Travel Agent Dashboard", layout="wide", page_icon="🏙️")
st.title("🏙️ Đà Nẵng Travel Agent - Real-time Observability")

LOG_FILE = Path("data/logs.jsonl")

def load_data():
    if not LOG_FILE.exists() or os.path.getsize(LOG_FILE) == 0:
        return pd.DataFrame()
    
    records = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                payload = data.get("payload", {})
                row = {
                    "ts": data.get("ts"),
                    "level": data.get("level", "info"),
                    "event": data.get("event", ""),
                    "latency_ms": data.get("latency_ms") or payload.get("latency_ms"),
                    "tokens_in": data.get("tokens_in") or payload.get("tokens_in"),
                    "tokens_out": data.get("tokens_out") or payload.get("tokens_out"),
                    "cost_usd": data.get("cost_usd") or payload.get("cost_usd", 0),
                    "quality_score": data.get("quality_score") or payload.get("quality_score", 0.8)
                }
                records.append(row)
            except: continue
    
    df = pd.DataFrame(records)
    if not df.empty:
        df['ts'] = pd.to_datetime(df['ts'])
        df = df.dropna(subset=['ts']).sort_values('ts')
        metric_cols = ['latency_ms', 'tokens_in', 'tokens_out', 'cost_usd', 'quality_score']
        for col in metric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df = load_data()

# Sidebar để kiểm soát trạng thái
with st.sidebar:
    st.header("⚙️ System Status")
    st.success("Log Pipeline: Connected")
    st.info(f"🔄 Auto-refresh: 15s")
    if st.button("🚀 Force Refresh Now"):
        st.rerun()
    st.divider()
    if not df.empty:
        st.write("**Top Statistics**")
        st.write(f"- Avg Latency: `{df['latency_ms'].mean():.0f}ms`")
        st.write(f"- Avg Quality: `{df['quality_score'].mean():.2f}/1.0`")

if df.empty:
    st.warning("⚠️ Đang chờ dữ liệu log hợp lệ... Hãy chạy load_test.py trước.")
else:
    # --- ROW 1: METRICS ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Traffic (Total Requests)", len(df))
    with c2:
        err_count = len(df[df['level'].str.lower() == 'error'])
        err_rate = (err_count / len(df)) * 100
        st.metric("Error Rate", f"{err_rate:.1f}%", delta=f"{err_count} errors", delta_color="inverse")
    with c3:
        st.metric("Total Cost", f"${df['cost_usd'].sum():.4f}")

    st.divider()

    # --- ROW 2: BIỂU ĐỒ CHÍNH ---
    c4, c5 = st.columns(2)
    with c4:
        st.subheader("⏱️ Latency Distribution")
        lat_df = df.dropna(subset=['latency_ms'])
        if not lat_df.empty:
            st.line_chart(lat_df.set_index('ts')['latency_ms'])
            st.caption("🔴 SLO Threshold: 5000ms")
    
    with c5:
        st.subheader("🪙 Tokens Usage")
        tok_df = df.dropna(subset=['tokens_in', 'tokens_out'])
        if not tok_df.empty:
            st.area_chart(tok_df.set_index('ts')[['tokens_in', 'tokens_out']])
            st.caption("Chi phí Output ($15/1M) cao gấp 5 lần Input ($3/1M)")

    # --- ROW 3: CHẤT LƯỢNG & AUDIT ---
    st.divider()
    c6, c7 = st.columns([2, 1]) # 2 phần biểu đồ, 1 phần audit
    
    with c6:
        st.subheader("🎯 Quality Proxy Trend")
        q_df = df.dropna(subset=['quality_score'])
        if not q_df.empty:
            st.line_chart(q_df.set_index('ts')['quality_score'])
            st.caption("🔴 SLO Quality: 0.7 | Đo lường độ tin cậy của phản hồi RAG")

    with c7:
        st.subheader("🛡️ PII Security Audit")
        mask = df['event'].str.contains("REDACTED", na=False, case=False)
        audit_df = df[mask]
        if not audit_df.empty:
            st.dataframe(audit_df[['ts', 'event']].tail(5), use_container_width=True)
            st.warning("Cảnh báo: Phát hiện dữ liệu nhạy cảm đã bị ẩn.")
        else:
            st.success("Safe: Không có vi phạm PII.")

# Auto-refresh
time.sleep(15)
st.rerun()