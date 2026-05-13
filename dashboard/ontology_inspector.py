"""
Ontology Inspector for Semantic Debugging
"""

import streamlit as st
from typing import List, Dict
from reasoner.ontology_loader import get_ontology_loader
from reasoner.ontology_updater import get_ontology_updater

def render_ontology_stats():
    """Render ontology statistics"""
    
    st.markdown("### 📊 Ontology Statistics")
    
    loader = get_ontology_loader()
    
    if not loader.is_loaded:
        st.warning("Ontology not loaded")
        return
    
    try:
        classes = loader.get_all_classes()
        individuals = loader.get_all_individuals()
        properties = loader.get_all_properties()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Classes", len(classes))
        with col2:
            st.metric("Individuals", len(individuals))
        with col3:
            st.metric("Properties", len(properties))
    
    except Exception as e:
        st.error(f"Error loading ontology stats: {e}")

def render_individuals_browser():
    """Browse ontology individuals and their properties"""
    
    st.markdown("### 👥 Individuals Browser")
    
    loader = get_ontology_loader()
    updater = get_ontology_updater()
    
    if not loader.is_loaded:
        st.warning("Ontology not loaded")
        return
    
    try:
        individuals = loader.get_all_individuals()
        individual_names = [str(ind).split("#")[-1].strip("'") for ind in individuals]
        
        if individual_names:
            selected_individual = st.selectbox("Select Individual", individual_names)
            
            if selected_individual:
                # Get the actual individual object
                ind = loader.get_individual(selected_individual)
                
                if ind:
                    st.markdown(f"#### {selected_individual}")
                    
                    # Display types/classes
                    st.markdown("**Types (Classes):**")
                    types_list = [str(t).split("#")[-1].strip("'") for t in ind.is_a]
                    if types_list:
                        for t in types_list:
                            st.write(f"  - {t}")
                    else:
                        st.write("  (No explicit types)")
                    
                    # Display properties
                    st.markdown("**Properties:**")
                    try:
                        # Get all properties of the individual
                        for prop_name in dir(ind):
                            if not prop_name.startswith("_"):
                                try:
                                    prop_value = getattr(ind, prop_name)
                                    if prop_value and not callable(prop_value):
                                        st.write(f"  - {prop_name}: {prop_value}")
                                except:
                                    pass
                    except Exception as e:
                        st.write(f"  (Error reading properties: {e})")
    
    except Exception as e:
        st.error(f"Error browsing individuals: {e}")

def render_inferred_faults():
    """Display currently inferred faults from reasoning engine"""
    
    st.markdown("### 🔴 Inferred Faults (Ontology)")
    
    from reasoner.reasoning_engine import get_reasoning_engine
    
    reasoning_engine = get_reasoning_engine()
    active_faults = reasoning_engine.get_active_faults()
    
    if not active_faults:
        st.success("✓ No faults inferred")
    else:
        for fault in active_faults:
            fault_details = reasoning_engine.get_fault_details(fault)
            
            severity = fault_details.get("severity", "UNKNOWN")
            description = fault_details.get("description", "No description")
            
            if severity == "CRITICAL":
                color = "#FF0000"
                icon = "🚨"
            elif severity == "SEVERE":
                color = "#FF3300"
                icon = "⚠️"
            else:
                color = "#FFAA00"
                icon = "⚡"
            
            fault_html = f"""
            <div style='
                background-color: #1a1f3a;
                border-left: 4px solid {color};
                padding: 12px;
                margin: 8px 0;
                border-radius: 4px;
                color: #ffffff;
            '>
                <div style='color: {color}; font-weight: bold; margin-bottom: 4px;'>{icon} {fault} [{severity}]</div>
                <div style='font-size: 12px; color: #cccccc;'>{description}</div>
            </div>
            """
            st.markdown(fault_html, unsafe_allow_html=True)

def render_reasoning_rules():
    """Display active reasoning rules"""
    
    st.markdown("### 🧠 Semantic Reasoning Rules")
    
    from reasoner.swrl_rules import get_rule_documentation
    
    rules_doc = get_rule_documentation()
    
    for category, rules in rules_doc.items():
        with st.expander(f"📋 {category.replace('_', ' ').title()}"):
            for rule in rules:
                st.write(f"• {rule}")

def render_ontology_relationships():
    """Display ontology class hierarchy and relationships"""
    
    st.markdown("### 🔗 Class Hierarchy")
    
    loader = get_ontology_loader()
    
    if not loader.is_loaded:
        st.warning("Ontology not loaded")
        return
    
    try:
        classes = loader.get_all_classes()
        class_names = [str(cls).split("#")[-1].strip("'") for cls in classes]
        
        # Group by prefix (simple categorization)
        categories = {}
        for cls_name in class_names:
            # Try to extract category from class name
            if any(x in cls_name for x in ["Power", "Battery", "Solar", "Energy"]):
                cat = "Power System"
            elif any(x in cls_name for x in ["Thermal", "Temperature", "Heat"]):
                cat = "Thermal System"
            elif any(x in cls_name for x in ["Communication", "Signal", "Transmission", "Antenna"]):
                cat = "Communication System"
            elif any(x in cls_name for x in ["AOCS", "Attitude", "Gyro", "Actuator", "Orientation"]):
                cat = "AOCS System"
            elif any(x in cls_name for x in ["Fault", "Failure", "Error"]):
                cat = "Faults & Failures"
            else:
                cat = "Other"
            
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(cls_name)
        
        # Display hierarchically
        for category, cls_list in sorted(categories.items()):
            with st.expander(f"📦 {category}", expanded=(category == "Faults & Failures")):
                for cls_name in sorted(cls_list):
                    st.write(f"  • {cls_name}")
    
    except Exception as e:
        st.error(f"Error displaying class hierarchy: {e}")
