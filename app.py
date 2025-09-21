import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import json
import base64
from io import BytesIO
from data_processor import DataProcessor
from logic_gates import LogicGateAnalyzer
from cart_diagram import CARTDiagramGenerator
from visualizations import TruthTableVisualizer

# Set page configuration
st.set_page_config(
    page_title="CAR-T Design Tool for PDAC",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor('pancreatic_biomarkers.csv')
if 'biomarkers_data' not in st.session_state:
    st.session_state.biomarkers_data = st.session_state.data_processor.get_categories_with_biomarkers()
if 'selected_tumor_antigens' not in st.session_state:
    st.session_state.selected_tumor_antigens = []
if 'selected_healthy_antigens' not in st.session_state:
    st.session_state.selected_healthy_antigens = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None


def reset_all_selections():
    """Reset all user selections and analysis results."""
    st.session_state.selected_tumor_antigens = []
    st.session_state.selected_healthy_antigens = []
    st.session_state.analysis_results = None
    st.rerun()

def main():
    # Top right controls: Refresh button only
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("🔄", key="refresh_all", help="Reset All Selections"):
            reset_all_selections()
    
    st.title("🧬 CAR-T Design Tool for PDAC")
    st.markdown("### Dual-Logic CAR-T Strategy Designer for Pancreatic Ductal Adenocarcinoma")
    
    # Ethics disclaimer
    st.error("⚠️ **RESEARCH USE ONLY** - This tool is for research purposes only and is not intended for clinical use or medical diagnosis.")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Section",
        ["🎯 Antigen Selection", "🔬 Logic Gate Analysis", "🧬 CAR-T Diagram"]
    )
    
    if page == "🎯 Antigen Selection":
        antigen_selection_page()
    elif page == "🔬 Logic Gate Analysis":
        logic_gate_analysis_page()
    elif page == "🧬 CAR-T Diagram":
        cart_diagram_page()

def antigen_selection_page():
    st.header("🎯 Antigen Selection")
    st.markdown("Select biomarkers from the comprehensive pancreatic cancer dataset")
    
    # Dataset overview
    st.subheader("📊 Dataset Overview")
    total_biomarkers = sum(len(biomarkers) for biomarkers in st.session_state.biomarkers_data.values())
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Biomarkers", total_biomarkers)
    with col2:
        st.metric("Categories", len(st.session_state.biomarkers_data))
    with col3:
        oncogenic_count = len(st.session_state.data_processor.get_oncogenic_biomarkers())
        st.metric("Oncogenic Markers", oncogenic_count)
    
    # Tabular display of biomarkers by category
    st.subheader("🗂️ Biomarker Categories")
    
    # Category selection
    selected_category = st.selectbox(
        "Select Category to View:",
        list(st.session_state.biomarkers_data.keys()),
        key="category_selector"
    )
    
    if selected_category:
        biomarkers_in_category = st.session_state.biomarkers_data[selected_category]
        
        # Create DataFrame for display
        display_df = pd.DataFrame(biomarkers_in_category)
        if not display_df.empty:
            display_df = display_df[['biomarker_name', 'category', 'indication']].copy()
            display_df['Select'] = False
            display_df.index = range(len(display_df))
            
            # Display the table with selection
            st.write(f"**{selected_category}** ({len(biomarkers_in_category)} biomarkers)")
            
            # Process indications using clean method
            processed_biomarkers = []
            for b in biomarkers_in_category:
                clean_indication = st.session_state.data_processor.clean_indication(b['indication'])
                processed_biomarkers.append({**b, 'indication_clean': clean_indication})
            
            # Multiselect for tumor antigens (oncogenic: ↑ or context-dependent ↑/↓)
            tumor_options = [b['biomarker_name'] for b in processed_biomarkers 
                           if b['indication_clean'] in ['↑', '↑/↓']]
            selected_tumor = st.multiselect(
                "Select Tumor Antigens (↑ oncogenic):",
                tumor_options,
                default=[x for x in st.session_state.selected_tumor_antigens if x in tumor_options],
                key=f"tumor_{selected_category}"
            )
            
            # Multiselect for healthy cell antigens (tumor suppressors: ↓ or context-dependent ↑/↓)
            healthy_options = [b['biomarker_name'] for b in processed_biomarkers 
                             if b['indication_clean'] in ['↓', '↑/↓']]
            selected_healthy = st.multiselect(
                "Select Healthy Cell Antigens (↓ suppressor):",
                healthy_options,
                default=[x for x in st.session_state.selected_healthy_antigens if x in healthy_options],
                key=f"healthy_{selected_category}"
            )
            
            # Update global selections
            # Remove previous selections from this category and add new ones
            st.session_state.selected_tumor_antigens = [
                x for x in st.session_state.selected_tumor_antigens 
                if x not in [b['biomarker_name'] for b in biomarkers_in_category]
            ] + selected_tumor
            
            st.session_state.selected_healthy_antigens = [
                x for x in st.session_state.selected_healthy_antigens 
                if x not in [b['biomarker_name'] for b in biomarkers_in_category]
            ] + selected_healthy
            
            # Display table
            st.dataframe(display_df[['biomarker_name', 'category', 'indication']], width='stretch')
    
    # Selection summary
    st.subheader("📋 Current Selection Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Selected Tumor Antigens:**")
        if st.session_state.selected_tumor_antigens:
            for antigen in st.session_state.selected_tumor_antigens:
                st.write(f"• {antigen}")
        else:
            st.write("None selected")
    
    with col2:
        st.write("**Selected Healthy Cell Antigens:**")
        if st.session_state.selected_healthy_antigens:
            for antigen in st.session_state.selected_healthy_antigens:
                st.write(f"• {antigen}")
        else:
            st.write("None selected")
    
    # Clear selections button
    if st.button("🗑️ Clear All Selections"):
        st.session_state.selected_tumor_antigens = []
        st.session_state.selected_healthy_antigens = []
        st.rerun()

def logic_gate_analysis_page():
    st.header("🔬 Truth Table & Logic Gate Analysis")
    
    if not st.session_state.selected_tumor_antigens:
        st.warning("⚠️ Please select tumor antigens first in the Antigen Selection page.")
        return
    
    # Display selected antigens for analysis
    st.subheader("🎯 Selected Antigens for Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Tumor Antigens:**")
        for antigen in st.session_state.selected_tumor_antigens:
            st.write(f"• {antigen}")
    
    with col2:
        st.write("**Healthy Cell Antigens (HCA):**")
        for antigen in st.session_state.selected_healthy_antigens:
            st.write(f"• {antigen}")
    
    # Determine recommended gate based on selection logic
    def get_recommended_gate():
        has_tumor = len(st.session_state.selected_tumor_antigens) > 0
        has_healthy = len(st.session_state.selected_healthy_antigens) > 0
        
        if has_tumor and has_healthy:
            return "AND"
        elif has_tumor and not has_healthy:
            return "OR"
        elif not has_tumor and has_healthy:
            return "NOT"
        else:
            return "XNOR"
    
    recommended_gate = get_recommended_gate()
    
    # Display recommendation
    st.subheader("🏆 Recommended Logic Gate")
    col_rec1, col_rec2 = st.columns([1, 3])
    with col_rec1:
        st.metric("Gate", recommended_gate)
    with col_rec2:
        if recommended_gate == "AND":
            st.write("✅ **AND Gate**: Both tumor antigen AND healthy cell antigen must be present for activation")
        elif recommended_gate == "OR":
            st.write("✅ **OR Gate**: Either tumor antigen can trigger activation")
        elif recommended_gate == "NOT":
            st.write("✅ **NOT Gate**: Activates when healthy cell antigen is absent")
        else:
            st.write("✅ **XNOR Gate**: Balanced targeting strategy")
    
    # Display truth tables
    st.subheader("📋 Truth Tables")
    
    # Special handling for NOT gate - always show fixed truth table
    if recommended_gate == "NOT":
        st.markdown("**NOT Gate Truth Table (Fixed):**")
        not_table_data = {
            'Input (HCA)': [0, 1],
            'Y (Output)': [1, 0],
            'Explanation': ['Activate (kill)', 'Deactivate (off)']
        }
        not_df = pd.DataFrame(not_table_data)
        st.dataframe(not_df, width='stretch')
    else:
        # Generate analysis for other gates
        if st.button("🚀 Generate Logic Gate Analysis"):
            with st.spinner("Analyzing logic gates..."):
                selected_antigens = {
                    'tumor': st.session_state.selected_tumor_antigens,
                    'healthy': st.session_state.selected_healthy_antigens
                }
                
                analyzer = LogicGateAnalyzer(st.session_state.data_processor.df, selected_antigens)
                truth_tables = analyzer.generate_all_truth_tables()
                
                st.session_state.analysis_results = {
                    'truth_tables': truth_tables,
                    'recommended_gate': recommended_gate
                }
        
        # Display results for non-NOT gates
        if st.session_state.analysis_results and 'truth_tables' in st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            # Show truth table for recommended gate
            if recommended_gate in results['truth_tables']:
                truth_table = results['truth_tables'][recommended_gate]
                
                st.markdown(f"**{recommended_gate} Gate Truth Table:**")
                
                # Create display table
                display_data = []
                for i, inputs in enumerate(truth_table['inputs']):
                    input_str = ' '.join(str(x) for x in inputs)
                    output = truth_table['outputs'][i]
                    cell_type = truth_table['cell_types'][i]
                    action = "Kill" if output == 1 else "Off"
                    
                    display_data.append({
                        'Inputs': input_str,
                        'Output': output,
                        'Cell Type': cell_type,
                        'Action': action
                    })
                
                truth_df = pd.DataFrame(display_data)
                st.dataframe(truth_df, width='stretch')

def cart_diagram_page():
    st.header("🧬 Personalized CAR-T Structure for PDAC")
    
    if not st.session_state.selected_tumor_antigens:
        st.warning("⚠️ Please select tumor antigens first in the Antigen Selection page.")
        return
    
    # Enhanced layout with side-by-side components
    col_left, col_right = st.columns([3, 2])
    
    with col_right:
        # Selected antigens summary with enhanced visual indicators
        st.subheader("🎯 Target Strategy")
        
        # Tumor antigens with kill indicators
        st.markdown("**🔴 Tumor Antigens (Kill Targets):**")
        for antigen in st.session_state.selected_tumor_antigens:
            st.markdown(f"- 🎯 {antigen} → **KILL**")
        
        # Healthy cell antigens with protection indicators
        if st.session_state.selected_healthy_antigens:
            st.markdown("**🟢 Healthy Cell Antigens (Protect):**")
            for antigen in st.session_state.selected_healthy_antigens:
                st.markdown(f"- 🛡️ {antigen} → **PROTECT**")
        
        # Enhanced generate button
        if st.button("🚀 Generate Personalized CAR-T", type="primary", use_container_width=True):
            with st.spinner("Creating your personalized CAR-T design..."):
                # Prepare antigen data
                selected_antigens = {
                    'tumor': st.session_state.selected_tumor_antigens,
                    'healthy': st.session_state.selected_healthy_antigens
                }
                
                # Generate diagram with default settings
                diagram_gen = CARTDiagramGenerator(selected_antigens)
                svg_content = diagram_gen.generate_cart_diagram(
                    costimulatory_domain="4-1BB",
                    style="Standard"
                )
                
                # Store for display in left column
                st.session_state.cart_diagram = svg_content
        
        # PDAC-specific design summary
        if 'cart_diagram' in st.session_state:
            st.subheader("📋 PDAC Design Summary")
            
            st.markdown(f"**🎯 Strategy:** Dual-Logic CAR-T")
            st.markdown(f"**🔴 Primary Targets:** {', '.join(st.session_state.selected_tumor_antigens)}")
            st.markdown(f"**⚙️ Costimulatory:** 4-1BB")
            st.markdown(f"**🛡️ Safety Profile:** Designed to spare healthy pancreatic tissue")
            
            # PDAC-specific notes
            st.info("👉 **PDAC Note:** This dual-logic design targets heterogeneous pancreatic tumors while minimizing damage to critical pancreatic functions.")
    
    with col_left:
        # Display diagram if generated
        if 'cart_diagram' in st.session_state:
            st.subheader("🧬 Your Personalized CAR-T Structure")
            components.html(st.session_state.cart_diagram, height=650)
            
            # Download options
            st.subheader("💾 Export Options")
            st.download_button(
                label="💾 Download SVG",
                data=st.session_state.cart_diagram,
                file_name=f"cart_design_{'-'.join(st.session_state.selected_tumor_antigens)}.svg",
                mime="image/svg+xml"
            )
        else:
            # Placeholder when no diagram is generated
            st.info("📍 Click 'Generate Personalized CAR-T' on the right to see your personalized diagram here.")
            
            # Show example or instructional content
            st.markdown("""
            ### 🧬 CAR-T Components Overview
            
            Your personalized diagram will include:
            
            - **🔍 scFv Domains**: Target-specific antibody fragments for your selected antigens
            - **🔗 Hinge Region**: Flexible spacer for optimal antigen binding
            - **📡 Transmembrane**: Anchors CAR to T-cell surface
            - **💪 Costimulatory**: Enhances T-cell activation and persistence
            - **⚡ Signaling Domain**: Triggers T-cell cytotoxic response
            
            **🎯 Kill Action**: Shown for tumor antigens with targeting arrows
            **🛡️ Protect Action**: Indicated for healthy cell antigens with safety symbols
            """)

if __name__ == "__main__":
    main()