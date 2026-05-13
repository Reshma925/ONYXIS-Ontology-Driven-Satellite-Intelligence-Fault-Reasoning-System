"""
Subsystem Detailed View
"""

import streamlit as st
from typing import Dict
from utils.helpers import format_telemetry_value, get_health_status

def render_power_subsystem(telemetry: Dict[str, float]):
    """Render detailed power subsystem view"""
    
    st.markdown("### ⚡ Power System Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Generation & Storage")
        
        solar_output = telemetry.get("solar_output", 100.0)
        battery_voltage = telemetry.get("battery_voltage", 28.0)
        battery_current = telemetry.get("battery_current", 10.0)
        
        # Solar output gauge
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px;'>
            <div style='color: #FFD700; font-weight: bold;'>Solar Panel Output</div>
            <div style='font-size: 24px; color: #FFD700; font-weight: bold;'>{solar_output:.1f} W</div>
            <div style='width: 100%; background-color: #333; border-radius: 4px; height: 8px; margin-top: 8px; overflow: hidden;'>
                <div style='width: {min(100, (solar_output/150)*100)}%; height: 100%; background-color: #FFD700; border-radius: 4px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Battery status
        status, _ = get_health_status(battery_voltage, "battery_voltage")
        status_color = "#00FF00" if status == "HEALTHY" else "#FFAA00" if status == "WARNING" else "#FF0000"
        
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px; margin-top: 10px;'>
            <div style='color: {status_color}; font-weight: bold;'>Battery Voltage</div>
            <div style='font-size: 24px; color: {status_color}; font-weight: bold;'>{battery_voltage:.1f} V</div>
            <div style='color: {status_color}; font-size: 12px;'>{status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Consumption & Balance")
        
        power_consumption = telemetry.get("power_consumption", 50.0)
        balance = solar_output - power_consumption
        balance_color = "#00FF00" if balance > 0 else "#FF0000"
        
        # Power consumption
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px;'>
            <div style='color: #FF6B6B; font-weight: bold;'>Power Consumption</div>
            <div style='font-size: 24px; color: #FF6B6B; font-weight: bold;'>{power_consumption:.1f} W</div>
            <div style='width: 100%; background-color: #333; border-radius: 4px; height: 8px; margin-top: 8px; overflow: hidden;'>
                <div style='width: {min(100, (power_consumption/100)*100)}%; height: 100%; background-color: #FF6B6B; border-radius: 4px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Power balance
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px; margin-top: 10px;'>
            <div style='color: {balance_color}; font-weight: bold;'>Power Balance</div>
            <div style='font-size: 24px; color: {balance_color}; font-weight: bold;'>{balance:+.1f} W</div>
            <div style='color: {balance_color}; font-size: 12px;'>{"Surplus" if balance > 0 else "Deficit"}</div>
        </div>
        """, unsafe_allow_html=True)

def render_thermal_subsystem(telemetry: Dict[str, float]):
    """Render detailed thermal subsystem view"""
    
    st.markdown("### 🌡️ Thermal System Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Temperatures")
        
        internal_temp = telemetry.get("internal_temp", 25.0)
        subsystem_temp = telemetry.get("subsystem_temp", 20.0)
        
        int_status, _ = get_health_status(internal_temp, "internal_temp")
        int_color = "#00FF00" if int_status == "HEALTHY" else "#FFAA00" if int_status == "WARNING" else "#FF0000"
        
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px;'>
            <div style='color: {int_color}; font-weight: bold;'>Internal Temperature</div>
            <div style='font-size: 24px; color: {int_color}; font-weight: bold;'>{internal_temp:.1f}°C</div>
            <div style='color: {int_color}; font-size: 12px;'>{int_status}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px; margin-top: 10px;'>
            <div style='color: #00CCFF; font-weight: bold;'>Subsystem Temperature</div>
            <div style='font-size: 24px; color: #00CCFF; font-weight: bold;'>{subsystem_temp:.1f}°C</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Thermal Load")
        
        thermal_load = telemetry.get("thermal_load", 40.0)
        load_status, _ = get_health_status(thermal_load, "thermal_load")
        load_color = "#00FF00" if thermal_load < 70 else "#FFAA00" if thermal_load < 85 else "#FF0000"
        
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px;'>
            <div style='color: {load_color}; font-weight: bold;'>Thermal Load</div>
            <div style='font-size: 24px; color: {load_color}; font-weight: bold;'>{thermal_load:.1f}%</div>
            <div style='width: 100%; background-color: #333; border-radius: 4px; height: 12px; margin-top: 8px; overflow: hidden;'>
                <div style='width: {thermal_load}%; height: 100%; background: linear-gradient(90deg, #00FF00, #FFAA00, #FF0000); border-radius: 4px;'></div>
            </div>
            <div style='color: {load_color}; font-size: 12px; margin-top: 8px;'>{load_status}</div>
        </div>
        """, unsafe_allow_html=True)

def render_communication_subsystem(telemetry: Dict[str, float]):
    """Render detailed communication subsystem view"""
    
    st.markdown("### 📡 Communication System Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Signal Quality")
        
        signal_strength = telemetry.get("signal_strength", -60.0)
        transmission_quality = telemetry.get("transmission_quality", 90.0)
        
        sig_status, _ = get_health_status(signal_strength, "signal_strength")
        sig_color = "#00FF00" if sig_status == "HEALTHY" else "#FFAA00" if sig_status == "WARNING" else "#FF0000"
        
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px;'>
            <div style='color: {sig_color}; font-weight: bold;'>Signal Strength</div>
            <div style='font-size: 24px; color: {sig_color}; font-weight: bold;'>{signal_strength:.1f} dBm</div>
            <div style='color: {sig_color}; font-size: 12px;'>{sig_status}</div>
        </div>
        """, unsafe_allow_html=True)
        
        tq_color = "#00FF00" if transmission_quality > 80 else "#FFAA00" if transmission_quality > 50 else "#FF0000"
        
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px; margin-top: 10px;'>
            <div style='color: {tq_color}; font-weight: bold;'>Transmission Quality</div>
            <div style='font-size: 24px; color: {tq_color}; font-weight: bold;'>{transmission_quality:.1f}%</div>
            <div style='width: 100%; background-color: #333; border-radius: 4px; height: 8px; margin-top: 8px; overflow: hidden;'>
                <div style='width: {transmission_quality}%; height: 100%; background: linear-gradient(90deg, #FF0000, #FFAA00, #00FF00); border-radius: 4px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Antenna Status")
        
        antenna_alignment = telemetry.get("antenna_alignment", 180.0)
        
        # Polar plot representation
        deviation_from_optimal = abs(antenna_alignment - 180.0)
        align_color = "#00FF00" if deviation_from_optimal < 30 else "#FFAA00" if deviation_from_optimal < 60 else "#FF0000"
        
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px;'>
            <div style='color: {align_color}; font-weight: bold;'>Antenna Alignment</div>
            <div style='font-size: 24px; color: {align_color}; font-weight: bold;'>{antenna_alignment:.1f}°</div>
            <div style='color: {align_color}; font-size: 12px;'>Deviation: {deviation_from_optimal:.1f}° from optimal</div>
        </div>
        """, unsafe_allow_html=True)

def render_aocs_subsystem(telemetry: Dict[str, float]):
    """Render detailed AOCS subsystem view"""
    
    st.markdown("### 🛰️ AOCS System Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Gyroscope Status")
        
        gyro_drift = telemetry.get("gyro_drift", 0.0)
        gyro_color = "#00FF00" if abs(gyro_drift) < 0.5 else "#FFAA00" if abs(gyro_drift) < 0.8 else "#FF0000"
        
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px;'>
            <div style='color: {gyro_color}; font-weight: bold;'>Gyroscope Drift</div>
            <div style='font-size: 24px; color: {gyro_color}; font-weight: bold;'>{gyro_drift:+.3f} deg/s</div>
            <div style='color: {gyro_color}; font-size: 12px;'>Within {"Nominal" if abs(gyro_drift) < 0.5 else "Acceptable" if abs(gyro_drift) < 0.8 else "Critical"} Range</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Attitude Control")
        
        orientation_deviation = telemetry.get("orientation_deviation", 5.0)
        orient_color = "#00FF00" if orientation_deviation < 10 else "#FFAA00" if orientation_deviation < 20 else "#FF0000"
        
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px;'>
            <div style='color: {orient_color}; font-weight: bold;'>Orientation Deviation</div>
            <div style='font-size: 24px; color: {orient_color}; font-weight: bold;'>{orientation_deviation:.2f}°</div>
            <div style='width: 100%; background-color: #333; border-radius: 4px; height: 8px; margin-top: 8px; overflow: hidden;'>
                <div style='width: {min(100, orientation_deviation*3)}%; height: 100%; background: linear-gradient(90deg, #00FF00, #FFAA00, #FF0000); border-radius: 4px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    col3, _ = st.columns(2)
    with col3:
        st.markdown("#### Actuator Status")
        
        actuator_status = telemetry.get("actuator_status", 100.0)
        act_color = "#00FF00" if actuator_status > 85 else "#FFAA00" if actuator_status > 50 else "#FF0000"
        
        st.markdown(f"""
        <div style='padding: 10px; background-color: #1a1f3a; border-radius: 8px;'>
            <div style='color: {act_color}; font-weight: bold;'>Actuator Status</div>
            <div style='font-size: 24px; color: {act_color}; font-weight: bold;'>{actuator_status:.1f}%</div>
            <div style='width: 100%; background-color: #333; border-radius: 4px; height: 8px; margin-top: 8px; overflow: hidden;'>
                <div style='width: {actuator_status}%; height: 100%; background: linear-gradient(90deg, #FF0000, #FFAA00, #00FF00); border-radius: 4px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
