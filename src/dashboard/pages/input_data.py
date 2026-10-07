# src/dashboard/pages/input_data.py
import streamlit as st
from datetime import datetime, time
from src.database import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from src.dashboard.operations import ingest_new_site, ingest_network_measurement, ingest_pipeline_incident

UGANDA_DISTRICTS = ["Kampala", "Wakiso", "Entebbe", "Gulu", "Mbarara", "Jinja", "Mbale", "Masaka", "Hoima"]
UGANDA_REGIONS = ["Central", "Eastern", "Northern", "Western", "Kampala Metropolitan"]
SITE_TYPES = ["Macro Tower", "Micro Cell Node", "Indoor Active DAS", "Rooftop Hub"]
SEVERITY_LEVELS = ["LOW", "WARNING", "MINOR", "MAJOR", "CRITICAL"]
INCIDENT_STATUSES = ["OPEN", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED"]

SessionLocal = sessionmaker(bind=engine)

def render_input_page():
    st.title("📥 Interactive Data Input & Ingestion Page")
    st.caption("Secure operational interface feeding domain tables natively through structured validation architectures.")
    
    info_type = st.selectbox(
        "Choose Operational Information Type to Log:",
        ["Site Information", "Network Measurement", "Incident Information"],
        index=0
    )
    
    st.divider()
    db_session = SessionLocal()
    
    try:
        # --- SITE FORM ---
        if info_type == "Site Information":
            st.subheader("🏢 SITE INFORMATION")
            with st.form("site_form", clear_on_submit=True):
                site_name = st.text_input("Site Name", placeholder="Kampala Central Tower Hub")
                col1, col2 = st.columns(2)
                with col1:
                    district = st.selectbox("District", UGANDA_DISTRICTS)
                    region = st.selectbox("Region", UGANDA_REGIONS)
                    site_type = st.selectbox("Site Type", SITE_TYPES)
                with col2:
                    latitude = st.number_input("Latitude", min_value=-1.5, max_value=4.5, value=0.3136, format="%.6f")
                    longitude = st.number_input("Longitude", min_value=29.5, max_value=35.5, value=32.5811, format="%.6f")
                    status = st.selectbox("Status", ["Active", "Maintenance", "Provisioning"])
                
                if st.form_submit_button("Save Site"):
                    payload = {
                        "name": site_name.strip(), "district": district, "region": region,
                        "latitude": latitude, "longitude": longitude, "site_type": site_type, "status": status
                    }
                    success, message, new_id = ingest_new_site(db_session, payload)
                    if success:
                        st.success(f"{message} Site ID: {new_id}")
                    else:
                        st.error(message)

        # --- MEASUREMENT FORM ---
        elif info_type == "Network Measurement":
            st.subheader("📊 NETWORK MEASUREMENT")
            active_nodes = db_session.execute(text("SELECT id, name, district FROM sites ORDER BY name;")).fetchall()
            site_map = {f"{node.name} ({node.district}) [ID: {node.id}]": node.id for node in active_nodes}
            
            if not site_map:
                st.warning("⚠️ Zero telemetry target points registered. Please insert a baseline Site Node first.")
                return
                
            with st.form("measurement_form", clear_on_submit=True):
                target_site = st.selectbox("Site", list(site_map.keys()))
                col1, col2 = st.columns(2)
                with col1:
                    dl_speed = st.number_input("Download Speed (Mbps)", min_value=0.0, value=25.4)
                    ul_speed = st.number_input("Upload Speed (Mbps)", min_value=0.0, value=12.1)
                    latency = st.number_input("Latency (ms)", min_value=1.0, value=35.0)
                with col2:
                    packet_loss = st.number_input("Packet Loss (%)", min_value=0.0, max_value=100.0, value=0.05, format="%.4f")
                    rsrp = st.number_input("Signal Strength (dBm)", min_value=-140, max_value=-40, value=-82)
                
                if st.form_submit_button("Save Measurement"):
                    payload = {
                        "site_id": site_map[target_site], "download_speed": dl_speed,
                        "upload_speed": ul_speed, "latency": latency, "packet_loss": packet_loss, "signal_strength": rsrp
                    }
                    success, message = ingest_network_measurement(db_session, payload)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        # --- INCIDENT FORM ---
        elif info_type == "Incident Information":
            st.subheader("🚨 INCIDENT INFORMATION")
            active_nodes = db_session.execute(text("SELECT id, name, district FROM sites ORDER BY name;")).fetchall()
            site_map = {f"{node.name} ({node.district}) [ID: {node.id}]": node.id for node in active_nodes}
            
            if not site_map:
                st.warning("⚠️ Zero incident target nodes registered. Please insert a baseline Site Node first.")
                return

            with st.form("incident_form", clear_on_submit=True):
                target_site = st.selectbox("Site", list(site_map.keys()))
                title = st.text_input("Title")
                description = st.text_area("Description")
                
                col1, col2 = st.columns(2)
                with col1:
                    severity = st.selectbox("Severity", SEVERITY_LEVELS)
                    status = st.selectbox("Status", INCIDENT_STATUSES)
                with col2:
                    start_date = st.date_input("Started Date", value=datetime.today())
                    start_time = st.time_input("Started Time", value=time(9, 0))
                    
                    has_resolution = st.checkbox("Has Resolution Timestamp?", value=False)
                    res_date = st.date_input("Resolved Date", value=datetime.today(), disabled=not has_resolution)
                    res_time = st.time_input("Resolved Time", value=time(17, 0), disabled=not has_resolution)
                
                notes = st.text_area("Notes")
                
                if st.form_submit_button("Save Incident"):
                    started_at = datetime.combine(start_date, start_time)
                    resolved_at = datetime.combine(res_date, res_time) if has_resolution else None
                    
                    payload = {
                        "site_id": site_map[target_site], "title": title.strip(), "description": description.strip(),
                        "severity": severity, "status": status, "started_at": started_at, "resolved_at": resolved_at,
                        "notes": notes.strip() if notes else None
                    }
                    success, message = ingest_pipeline_incident(db_session, payload)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    finally:
        db_session.close()

if __name__ == "__main__":
    render_input_page()
