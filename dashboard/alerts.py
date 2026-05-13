"""
Alerts and Fault Console
"""

import streamlit as st
from typing import List, Dict
from datetime import datetime
from utils.constants import COLORS
from utils.logger import get_logger

def render_fault_console(faults: List[str], logs: List[Dict]):
    """Render live fault console with scrolling alerts"""
    
    st.markdown("---")
    st.markdown("<h2 style='color: #FF0000; text-shadow: 0 0 10px #FF0000;'>🚨 FAULT CONSOLE</h2>", unsafe_allow_html=True)
    
    if not faults and not logs:
        st.info("No faults detected. System operating normally.")
        return
    
    # Display recent faults
    if faults:
        st.markdown("#### Active Faults")
        for fault in faults:
            fault_html = f"""
            <div style="
                background: linear-gradient(90deg, #FF0000, #FF3300);
                border-left: 4px solid #FF0000;
                padding: 12px;
                margin: 8px 0;
                border-radius: 4px;
                color: #ffffff;
                font-weight: bold;
                letter-spacing: 1px;
            ">
                ⚠️ {fault}
            </div>
            """
            st.markdown(fault_html, unsafe_allow_html=True)
    
    # Display recent logs
    if logs:
        st.markdown("#### Recent System Events")
        
        # Create scrollable container
        log_container = st.container()
        
        with log_container:
            for log in logs[-20:]:  # Show last 20 logs
                timestamp = log.get("timestamp", "??:??:??")
                level = log.get("level", "INFO")
                message = log.get("message", "")
                component = log.get("component", "System")
                
                # Determine color based on level
                if level == "FAULT":
                    color = "#FF0000"
                    prefix = "🚨"
                elif level == "ERROR":
                    color = "#FF3300"
                    prefix = "❌"
                elif level == "WARNING":
                    color = "#FFAA00"
                    prefix = "⚠️"
                else:
                    color = "#00FF00"
                    prefix = "✓"
                
                log_html = f"""
                <div style="
                    background-color: {COLORS['card_bg']};
                    border-left: 3px solid {color};
                    padding: 10px;
                    margin: 4px 0;
                    border-radius: 4px;
                    font-size: 12px;
                    font-family: monospace;
                ">
                    <span style="color: {color}; font-weight: bold;">{prefix} [{timestamp}]</span>
                    <span style="color: #888888;"> [{component}]</span>
                    <span style="color: #ffffff;"> {message}</span>
                </div>
                """
                st.markdown(log_html, unsafe_allow_html=True)

def render_fault_summary(faults: List[str]):
    """Render fault summary widget"""
    
    if not faults:
        summary_html = """
        <div style="
            background: linear-gradient(135deg, #00FF00, #00CC00);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            color: #000000;
            font-weight: bold;
            font-size: 18px;
        ">
            ✓ SYSTEM NOMINAL - ALL SUBSYSTEMS GREEN
        </div>
        """
    else:
        fault_count = len(faults)
        critical_count = sum(1 for f in faults if "Critical" in f)
        
        summary_html = f"""
        <div style="
            background: linear-gradient(135deg, #FF0000, #CC0000);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            color: #ffffff;
            font-weight: bold;
            font-size: 18px;
        ">
            🚨 FAULT ALERT - {fault_count} ACTIVE FAULT(S)
            <br/>
            <span style="font-size: 14px; opacity: 0.9;">
                {critical_count} Critical | {fault_count - critical_count} Warning
            </span>
        </div>
        """
    
    st.markdown(summary_html, unsafe_allow_html=True)

def render_alert_badges(faults: List[str]):
    """Render alert badges in columns"""
    
    if not faults:
        return
    
    # Group faults by type
    fault_categories = {
        "Power": [f for f in faults if "Battery" in f or "Solar" in f or "Power" in f],
        "Thermal": [f for f in faults if "Thermal" in f],
        "Communication": [f for f in faults if "Communication" in f or "Transmission" in f],
        "AOCS": [f for f in faults if "Attitude" in f or "Gyro" in f or "Actuator" in f],
    }
    
    active_categories = {k: v for k, v in fault_categories.items() if v}
    
    if active_categories:
        cols = st.columns(len(active_categories))
        for col, (category, fault_list) in zip(cols, active_categories.items()):
            with col:
                badge_html = f"""
                <div style="
                    background: linear-gradient(135deg, #FF3300, #FF0000);
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                    color: #ffffff;
                    font-weight: bold;
                ">
                    {category}<br/>
                    <span style="font-size: 24px; font-weight: bold;">{len(fault_list)}</span>
                </div>
                """
                st.markdown(badge_html, unsafe_allow_html=True)
