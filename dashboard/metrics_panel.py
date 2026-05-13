"""
Metrics Panel for Dashboard Display
"""

import streamlit as st
from typing import Dict, Tuple
from utils.constants import COLORS
from utils.helpers import get_subsystem_health, format_telemetry_value

def render_health_card(subsystem_name: str, status: str, health_percentage: float):
    """Render a subsystem health card"""
    
    # Determine color based on status
    if status == "HEALTHY":
        color = "#00FF00"
    elif status == "WARNING":
        color = "#FFAA00"
    else:
        color = "#FF0000"
    
    # Create card HTML
    card_html = f"""
    <div style="
        background-color: {COLORS['card_bg']};
        border: 2px solid {color};
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
    ">
        <h3 style="color: #ffffff; margin: 0 0 10px 0;">{subsystem_name}</h3>
        <div style="font-size: 28px; font-weight: bold; color: {color}; margin: 10px 0;">
            {health_percentage:.1f}%
        </div>
        <div style="color: {color}; font-weight: bold; letter-spacing: 2px;">
            {status}
        </div>
    </div>
    """
    
    return card_html

def render_subsystem_overview(telemetry: Dict[str, float]):
    """Render subsystem health overview"""
    
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #00FF00; text-shadow: 0 0 10px #00FF00;'>SUBSYSTEM HEALTH OVERVIEW</h2>", unsafe_allow_html=True)
    
    # Get health for all subsystems
    health_data = get_subsystem_health(telemetry)
    
    # Create columns for cards
    cols = st.columns(5)
    
    subsystems_order = ["power", "thermal", "communication", "aocs", "payload"]
    subsystem_names = {
        "power": "Power",
        "thermal": "Thermal",
        "communication": "Comm",
        "aocs": "AOCS",
        "payload": "Payload",
    }
    
    for idx, (subsys_key, col) in enumerate(zip(subsystems_order, cols)):
        status, health_pct = health_data.get(subsys_key, ("UNKNOWN", 0.0))
        subsys_name = subsystem_names.get(subsys_key, subsys_key)
        
        with col:
            card_html = render_health_card(subsys_name, status, health_pct)
            st.markdown(card_html, unsafe_allow_html=True)

def render_detailed_metrics(telemetry: Dict[str, float]):
    """Render detailed telemetry metrics in expandable sections"""
    
    st.markdown("---")
    st.markdown("<h2 style='color: #00FF00;'>DETAILED TELEMETRY</h2>", unsafe_allow_html=True)
    
    # Power System
    with st.expander("🔋 Power System", expanded=True):
        cols = st.columns(2)
        with cols[0]:
            st.metric(
                "Battery Voltage",
                format_telemetry_value(telemetry.get("battery_voltage", 28.0), "battery_voltage"),
                delta=None
            )
            st.metric(
                "Solar Panel Output",
                format_telemetry_value(telemetry.get("solar_output", 100.0), "solar_output"),
                delta=None
            )
        with cols[1]:
            st.metric(
                "Battery Current",
                format_telemetry_value(telemetry.get("battery_current", 10.0), "battery_current"),
                delta=None
            )
            st.metric(
                "Power Consumption",
                format_telemetry_value(telemetry.get("power_consumption", 50.0), "power_consumption"),
                delta=None
            )
    
    # Thermal System
    with st.expander("🌡️ Thermal System", expanded=True):
        cols = st.columns(2)
        with cols[0]:
            st.metric(
                "Internal Temperature",
                format_telemetry_value(telemetry.get("internal_temp", 25.0), "internal_temp"),
                delta=None
            )
            st.metric(
                "Thermal Load",
                format_telemetry_value(telemetry.get("thermal_load", 40.0), "thermal_load"),
                delta=None
            )
        with cols[1]:
            st.metric(
                "Subsystem Temperature",
                format_telemetry_value(telemetry.get("subsystem_temp", 20.0), "subsystem_temp"),
                delta=None
            )
    
    # Communication System
    with st.expander("📡 Communication System", expanded=True):
        cols = st.columns(2)
        with cols[0]:
            st.metric(
                "Signal Strength",
                format_telemetry_value(telemetry.get("signal_strength", -60.0), "signal_strength"),
                delta=None
            )
            st.metric(
                "Antenna Alignment",
                format_telemetry_value(telemetry.get("antenna_alignment", 180.0), "antenna_alignment"),
                delta=None
            )
        with cols[1]:
            st.metric(
                "Transmission Quality",
                format_telemetry_value(telemetry.get("transmission_quality", 90.0), "transmission_quality"),
                delta=None
            )
    
    # AOCS System
    with st.expander("🛰️ AOCS System", expanded=True):
        cols = st.columns(2)
        with cols[0]:
            st.metric(
                "Gyro Drift",
                format_telemetry_value(telemetry.get("gyro_drift", 0.0), "gyro_drift"),
                delta=None
            )
            st.metric(
                "Orientation Deviation",
                format_telemetry_value(telemetry.get("orientation_deviation", 5.0), "orientation_deviation"),
                delta=None
            )
        with cols[1]:
            st.metric(
                "Actuator Status",
                format_telemetry_value(telemetry.get("actuator_status", 100.0), "actuator_status"),
                delta=None
            )
