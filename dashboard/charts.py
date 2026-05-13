"""
Charts for Dashboard Visualization
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
from datetime import datetime
from utils.constants import COLORS

def render_telemetry_charts(telemetry_history: List[Dict]):
    """Render live telemetry charts"""
    
    if not telemetry_history or len(telemetry_history) < 2:
        st.info("Waiting for telemetry data...")
        return
    
    st.markdown("<h2 style='color: #00FF00;'>LIVE TELEMETRY CHARTS</h2>", unsafe_allow_html=True)
    
    # Extract timestamps and values
    timestamps = [item["timestamp"].strftime("%H:%M:%S") if hasattr(item["timestamp"], 'strftime') else str(item["timestamp"]) for item in telemetry_history]
    
    # Battery Voltage Chart
    col1, col2 = st.columns(2)
    
    with col1:
        battery_values = [item["data"].get("battery_voltage", 0) for item in telemetry_history]
        
        fig_battery = go.Figure()
        fig_battery.add_trace(go.Scatter(
            x=timestamps,
            y=battery_values,
            mode='lines+markers',
            name='Battery Voltage',
            line=dict(color='#00FFFF', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 255, 0.1)',
        ))
        
        fig_battery.add_hline(y=22.0, line_dash="dash", line_color="#FFAA00", annotation_text="Warning", annotation_position="right")
        fig_battery.add_hline(y=20.0, line_dash="dash", line_color="#FF0000", annotation_text="Critical", annotation_position="right")
        
        fig_battery.update_layout(
            title="Battery Voltage (V)",
            xaxis_title="Time",
            yaxis_title="Voltage (V)",
            hovermode='x unified',
            template="plotly_dark",
            margin=dict(l=0, r=0, t=40, b=0),
            height=300,
        )
        
        st.plotly_chart(fig_battery, use_container_width=True)
    
    with col2:
        temp_values = [item["data"].get("internal_temp", 0) for item in telemetry_history]
        
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=timestamps,
            y=temp_values,
            mode='lines+markers',
            name='Internal Temperature',
            line=dict(color='#FF6B6B', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.1)',
        ))
        
        fig_temp.add_hline(y=70.0, line_dash="dash", line_color="#FFAA00", annotation_text="Warning", annotation_position="right")
        fig_temp.add_hline(y=80.0, line_dash="dash", line_color="#FF0000", annotation_text="Critical", annotation_position="right")
        
        fig_temp.update_layout(
            title="Internal Temperature (°C)",
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            hovermode='x unified',
            template="plotly_dark",
            margin=dict(l=0, r=0, t=40, b=0),
            height=300,
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Signal Strength and Solar Output
    col3, col4 = st.columns(2)
    
    with col3:
        signal_values = [item["data"].get("signal_strength", -60) for item in telemetry_history]
        
        fig_signal = go.Figure()
        fig_signal.add_trace(go.Scatter(
            x=timestamps,
            y=signal_values,
            mode='lines+markers',
            name='Signal Strength',
            line=dict(color='#FFD700', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 215, 0, 0.1)',
        ))
        
        fig_signal.add_hline(y=-85.0, line_dash="dash", line_color="#FFAA00", annotation_text="Warning", annotation_position="right")
        fig_signal.add_hline(y=-95.0, line_dash="dash", line_color="#FF0000", annotation_text="Critical", annotation_position="right")
        
        fig_signal.update_layout(
            title="Signal Strength (dBm)",
            xaxis_title="Time",
            yaxis_title="Signal (dBm)",
            hovermode='x unified',
            template="plotly_dark",
            margin=dict(l=0, r=0, t=40, b=0),
            height=300,
        )
        
        st.plotly_chart(fig_signal, use_container_width=True)
    
    with col4:
        solar_values = [item["data"].get("solar_output", 100) for item in telemetry_history]
        
        fig_solar = go.Figure()
        fig_solar.add_trace(go.Scatter(
            x=timestamps,
            y=solar_values,
            mode='lines+markers',
            name='Solar Output',
            line=dict(color='#FFD700', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 215, 0, 0.1)',
        ))
        
        fig_solar.update_layout(
            title="Solar Panel Output (W)",
            xaxis_title="Time",
            yaxis_title="Power (W)",
            hovermode='x unified',
            template="plotly_dark",
            margin=dict(l=0, r=0, t=40, b=0),
            height=300,
        )
        
        st.plotly_chart(fig_solar, use_container_width=True)

def render_orientation_chart(telemetry_history: List[Dict]):
    """Render orientation deviation chart"""
    
    if not telemetry_history:
        return
    
    timestamps = [item["timestamp"].strftime("%H:%M:%S") if hasattr(item["timestamp"], 'strftime') else str(item["timestamp"]) for item in telemetry_history]
    orientation_values = [item["data"].get("orientation_deviation", 0) for item in telemetry_history]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=orientation_values,
        mode='lines+markers',
        name='Orientation Deviation',
        line=dict(color='#00FF00', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 0, 0.1)',
    ))
    
    fig.add_hline(y=15.0, line_dash="dash", line_color="#FFAA00", annotation_text="Warning", annotation_position="right")
    fig.add_hline(y=25.0, line_dash="dash", line_color="#FF0000", annotation_text="Critical", annotation_position="right")
    
    fig.update_layout(
        title="Orientation Deviation (°)",
        xaxis_title="Time",
        yaxis_title="Deviation (°)",
        hovermode='x unified',
        template="plotly_dark",
        height=350,
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_power_balance_chart(telemetry_history: List[Dict]):
    """Render power balance chart (generation vs consumption)"""
    
    if not telemetry_history:
        return
    
    timestamps = [item["timestamp"].strftime("%H:%M:%S") if hasattr(item["timestamp"], 'strftime') else str(item["timestamp"]) for item in telemetry_history]
    solar_values = [item["data"].get("solar_output", 0) for item in telemetry_history]
    consumption_values = [item["data"].get("power_consumption", 0) for item in telemetry_history]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=solar_values,
        mode='lines',
        name='Solar Generation',
        line=dict(color='#FFD700', width=2),
        fill='tozeroy',
    ))
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=consumption_values,
        mode='lines',
        name='Power Consumption',
        line=dict(color='#FF6B6B', width=2),
        fill='tozeroy',
    ))
    
    fig.update_layout(
        title="Power Balance (Generation vs Consumption)",
        xaxis_title="Time",
        yaxis_title="Power (W)",
        hovermode='x unified',
        template="plotly_dark",
        height=350,
    )
    
    st.plotly_chart(fig, use_container_width=True)
