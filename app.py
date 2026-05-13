"""
Satellite Monitoring and Fault Diagnosis Simulator
Main Streamlit Application
"""

import streamlit as st
import time
from datetime import datetime
from typing import Dict

# Import all modules
from reasoner.ontology_loader import get_ontology_loader
from reasoner.ontology_updater import get_ontology_updater
from reasoner.reasoning_engine import get_reasoning_engine
from simulator.telemetry_generator import get_telemetry_generator
from utils.logger import get_logger
from utils.constants import COLORS, SCENARIOS
from dashboard.metrics_panel import render_subsystem_overview, render_detailed_metrics
from dashboard.charts import render_telemetry_charts, render_orientation_chart, render_power_balance_chart
from dashboard.alerts import render_fault_console, render_fault_summary, render_alert_badges
from dashboard.subsystem_view import (
    render_power_subsystem,
    render_thermal_subsystem,
    render_communication_subsystem,
    render_aocs_subsystem
)
from dashboard.ontology_inspector import (
    render_ontology_stats,
    render_individuals_browser,
    render_inferred_faults,
    render_reasoning_rules,
    render_ontology_relationships
)

# Configure Streamlit
st.set_page_config(
    page_title="Satellite Monitoring & Diagnosis",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom theme
st.markdown(f"""
<style>
    :root {{
        --primary-color: #00FF00;
        --background-color: {COLORS['background']};
        --secondary-background-color: {COLORS['card_bg']};
        --text-color: {COLORS['text_primary']};
    }}
    
    body {{
        background-color: {COLORS['background']};
        color: {COLORS['text_primary']};
    }}
    
    .stApp {{
        background-color: {COLORS['background']};
    }}
    
    .main {{
        background-color: {COLORS['background']};
    }}
    
    .stSidebar {{
        background-color: {COLORS['card_bg']};
    }}
    
    /* Glowing text effect */
    h1, h2, h3 {{
        text-shadow: 0 0 10px #00FF00;
    }}
    
    /* Custom metrics styling */
    .metric-value {{
        font-size: 24px;
        font-weight: bold;
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ontology_loaded' not in st.session_state:
    st.session_state.ontology_loaded = False
if 'telemetry' not in st.session_state:
    st.session_state.telemetry = {}
if 'active_faults' not in st.session_state:
    st.session_state.active_faults = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'update_counter' not in st.session_state:
    st.session_state.update_counter = 0

# Get module instances
logger = get_logger()
ontology_loader = get_ontology_loader()
ontology_updater = get_ontology_updater()
reasoning_engine = get_reasoning_engine()
telemetry_generator = get_telemetry_generator()

# Initialize ontology on first load
if not st.session_state.ontology_loaded:
    with st.spinner("Loading ontology..."):
        if ontology_loader.load():
            st.session_state.ontology_loaded = True
            logger.info("Ontology initialization successful", "App")
        else:
            st.error("Failed to load ontology")
            st.stop()

def update_system():
    """Update telemetry, ontology, and reasoning"""
    try:
        # Generate telemetry
        telemetry = telemetry_generator.generate_telemetry()
        st.session_state.telemetry = telemetry
        
        # Update ontology with telemetry
        ontology_updater.update_telemetry(telemetry, "Satellite1")
        
        # Perform reasoning
        faults = reasoning_engine.infer_faults(telemetry, "Satellite1")
        st.session_state.active_faults = faults
        
        st.session_state.update_counter += 1
        
        return True
    except Exception as e:
        logger.error(f"Error during system update: {str(e)}", "App")
        return False

# Sidebar controls
st.sidebar.markdown("---")
st.sidebar.markdown("## ⚙️ SIMULATOR CONTROLS")
st.sidebar.markdown("---")

# Scenario selection
st.sidebar.markdown("### 📋 Scenario Selection")
scenario_options = telemetry_generator.get_available_scenarios()
scenario_names = {key: SCENARIOS.get(key, key) for key in scenario_options}

current_scenario = telemetry_generator.get_active_scenario()
selected_scenario = st.sidebar.selectbox(
    "Choose Scenario",
    scenario_options,
    format_func=lambda x: scenario_names[x],
    index=scenario_options.index(current_scenario) if current_scenario in scenario_options else 0
)

if selected_scenario != current_scenario:
    telemetry_generator.set_scenario(selected_scenario)
    st.sidebar.success(f"Scenario changed to: {scenario_names[selected_scenario]}")

# Simulation controls
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Simulation Settings")

refresh_interval = st.sidebar.slider(
    "Refresh Interval (seconds)",
    min_value=0.5,
    max_value=5.0,
    value=1.0,
    step=0.5
)

st.session_state.auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)

if st.sidebar.button("Manual Update", use_container_width=True):
    update_system()
    st.rerun()

if st.sidebar.button("Reset System", use_container_width=True):
    telemetry_generator.reset()
    logger.clear()
    st.session_state.active_faults = []
    st.success("System reset successfully")
    st.rerun()

# System statistics
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Statistics")
stats = telemetry_generator.get_statistics()
st.sidebar.metric("Updates", stats["update_count"])
st.sidebar.metric("Active Faults", len(st.session_state.active_faults))
if stats["last_update"]:
    st.sidebar.text(f"Last: {stats['last_update'].strftime('%H:%M:%S')}")

# Navigation tabs
st.sidebar.markdown("---")
st.sidebar.markdown("### 🗂️ Navigation")

tab = st.sidebar.radio(
    "Select View",
    ["🏠 Dashboard", "📊 Detailed View", "🔬 Ontology Inspector", "📋 System Logs"]
)

# Main title
st.markdown("""
<div style='text-align: center; margin: 20px 0;'>
    <h1 style='color: #00FF00; text-shadow: 0 0 20px #00FF00; font-size: 3em;'>🛰️ SATELLITE MONITORING</h1>
    <h2 style='color: #00CCFF; text-shadow: 0 0 10px #00CCFF;'>Semantic Fault Diagnosis & Digital Twin</h2>
</div>
""", unsafe_allow_html=True)

# Update system
if st.session_state.auto_refresh:
    # Create placeholder for auto-refresh
    placeholder = st.empty()
    
    while st.session_state.auto_refresh:
        update_system()
        
        # Display based on selected tab
        if tab == "🏠 Dashboard":
            # Fault Summary
            render_fault_summary(st.session_state.active_faults)
            
            # Subsystem Overview
            render_subsystem_overview(st.session_state.telemetry)
            
            # Fault Alert Badges
            if st.session_state.active_faults:
                st.markdown("---")
                render_alert_badges(st.session_state.active_faults)
            
            # Fault Console
            logs = logger.get_logs(limit=20)
            render_fault_console(st.session_state.active_faults, logs)
            
            # Live Charts
            st.markdown("---")
            telemetry_history = telemetry_generator.get_telemetry_history(limit=60)
            render_telemetry_charts(telemetry_history)
        
        elif tab == "📊 Detailed View":
            # Detailed Metrics
            render_detailed_metrics(st.session_state.telemetry)
            
            st.markdown("---")
            st.markdown("### ⚡ Subsystem Deep Analysis")
            
            subsys_tab = st.tabs(["Power", "Thermal", "Communication", "AOCS"])
            
            with subsys_tab[0]:
                render_power_subsystem(st.session_state.telemetry)
            
            with subsys_tab[1]:
                render_thermal_subsystem(st.session_state.telemetry)
            
            with subsys_tab[2]:
                render_communication_subsystem(st.session_state.telemetry)
            
            with subsys_tab[3]:
                render_aocs_subsystem(st.session_state.telemetry)
            
            # Charts
            st.markdown("---")
            telemetry_history = telemetry_generator.get_telemetry_history(limit=60)
            
            col1, col2 = st.columns(2)
            with col1:
                render_orientation_chart(telemetry_history)
            with col2:
                render_power_balance_chart(telemetry_history)
        
        elif tab == "🔬 Ontology Inspector":
            st.markdown("### 🔍 Semantic Ontology Analysis")
            
            inspector_tab = st.tabs(["Statistics", "Classes", "Individuals", "Inferred Faults", "Rules"])
            
            with inspector_tab[0]:
                render_ontology_stats()
            
            with inspector_tab[1]:
                render_ontology_relationships()
            
            with inspector_tab[2]:
                render_individuals_browser()
            
            with inspector_tab[3]:
                render_inferred_faults()
            
            with inspector_tab[4]:
                render_reasoning_rules()
        
        elif tab == "📋 System Logs":
            st.markdown("### 📋 System Event Logs")
            
            logs = logger.get_logs(limit=100)
            
            if logs:
                # Filter options
                col1, col2 = st.columns(2)
                with col1:
                    filter_level = st.multiselect(
                        "Filter by Level",
                        ["INFO", "WARNING", "ERROR", "FAULT"],
                        default=["INFO", "WARNING", "ERROR", "FAULT"]
                    )
                
                with col2:
                    filter_component = st.multiselect(
                        "Filter by Component",
                        list(set([log["component"] for log in logs])),
                        default=None
                    )
                
                # Display logs
                filtered_logs = [
                    log for log in logs
                    if log["level"] in filter_level and 
                    (not filter_component or log["component"] in filter_component)
                ]
                
                if filtered_logs:
                    for log in reversed(filtered_logs[-50:]):  # Show last 50
                        timestamp = log["timestamp"]
                        level = log["level"]
                        component = log["component"]
                        message = log["message"]
                        
                        if level == "FAULT":
                            color = "#FF0000"
                        elif level == "ERROR":
                            color = "#FF3300"
                        elif level == "WARNING":
                            color = "#FFAA00"
                        else:
                            color = "#00FF00"
                        
                        log_line = f"<span style='color: {color}; font-weight: bold;'>[{timestamp}]</span> <span style='color: #888;'>[{component}]</span> {message}"
                        st.markdown(log_line, unsafe_allow_html=True)
            else:
                st.info("No logs yet")
        
        # Auto-refresh with sleep
        time.sleep(refresh_interval)
else:
    # Manual mode - show once and stop
    update_system()
    
    if tab == "🏠 Dashboard":
        render_fault_summary(st.session_state.active_faults)
        render_subsystem_overview(st.session_state.telemetry)
        if st.session_state.active_faults:
            st.markdown("---")
            render_alert_badges(st.session_state.active_faults)
        logs = logger.get_logs(limit=20)
        render_fault_console(st.session_state.active_faults, logs)
        st.markdown("---")
        telemetry_history = telemetry_generator.get_telemetry_history(limit=60)
        render_telemetry_charts(telemetry_history)
    
    elif tab == "📊 Detailed View":
        render_detailed_metrics(st.session_state.telemetry)
        st.markdown("---")
        st.markdown("### ⚡ Subsystem Deep Analysis")
        
        subsys_tab = st.tabs(["Power", "Thermal", "Communication", "AOCS"])
        
        with subsys_tab[0]:
            render_power_subsystem(st.session_state.telemetry)
        with subsys_tab[1]:
            render_thermal_subsystem(st.session_state.telemetry)
        with subsys_tab[2]:
            render_communication_subsystem(st.session_state.telemetry)
        with subsys_tab[3]:
            render_aocs_subsystem(st.session_state.telemetry)
        
        st.markdown("---")
        telemetry_history = telemetry_generator.get_telemetry_history(limit=60)
        col1, col2 = st.columns(2)
        with col1:
            render_orientation_chart(telemetry_history)
        with col2:
            render_power_balance_chart(telemetry_history)
    
    elif tab == "🔬 Ontology Inspector":
        st.markdown("### 🔍 Semantic Ontology Analysis")
        inspector_tab = st.tabs(["Statistics", "Classes", "Individuals", "Inferred Faults", "Rules"])
        
        with inspector_tab[0]:
            render_ontology_stats()
        with inspector_tab[1]:
            render_ontology_relationships()
        with inspector_tab[2]:
            render_individuals_browser()
        with inspector_tab[3]:
            render_inferred_faults()
        with inspector_tab[4]:
            render_reasoning_rules()
    
    elif tab == "📋 System Logs":
        st.markdown("### 📋 System Event Logs")
        logs = logger.get_logs(limit=100)
        
        if logs:
            for log in reversed(logs[-50:]):
                timestamp = log["timestamp"]
                level = log["level"]
                component = log["component"]
                message = log["message"]
                
                if level == "FAULT":
                    color = "#FF0000"
                elif level == "ERROR":
                    color = "#FF3300"
                elif level == "WARNING":
                    color = "#FFAA00"
                else:
                    color = "#00FF00"
                
                log_line = f"<span style='color: {color}; font-weight: bold;'>[{timestamp}]</span> <span style='color: #888;'>[{component}]</span> {message}"
                st.markdown(log_line, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px; margin-top: 40px;'>
    <p>Semantic Satellite Monitoring & Fault Diagnosis Simulator</p>
    <p>Powered by Ontology Reasoning (OWL/SWRL) & Streamlit</p>
</div>
""", unsafe_allow_html=True)
