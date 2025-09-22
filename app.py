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
    page_title="ImmunoGate: Dual Logic CAR-T Therapy for PDAC",
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
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def apply_theme():
    """Apply custom CSS for theme."""
    if st.session_state.theme == 'dark':
        st.markdown("""
        <style>
        .stApp {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        .theme-toggle {
            position: fixed;
            top: 10px;
            right: 20px;
            z-index: 999;
            background-color: #333;
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            color: white;
            cursor: pointer;
        }
        .stSelectbox > div > div {
            background-color: #333;
            color: white;
        }
        .stDataFrame {
            background-color: #2d2d2d;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .theme-toggle {
            position: fixed;
            top: 10px;
            right: 20px;
            z-index: 999;
            background-color: #f0f2f6;
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            color: #333;
            cursor: pointer;
        }
        </style>
        """, unsafe_allow_html=True)

def toggle_theme():
    """Toggle between light and dark theme."""
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

def reset_all_selections():
    """Reset all user selections and analysis results."""
    st.session_state.selected_tumor_antigens = []
    st.session_state.selected_healthy_antigens = []
    st.session_state.analysis_results = None
    st.rerun()

def main():
    apply_theme()
    
    # Top right controls: Refresh button only
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("🔄", key="refresh_all", help="Reset All Selections"):
            reset_all_selections()
    
    st.title("🧬 ImmunoGate: Dual Logic CAR-T Therapy for PDAC")
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
    st.header("🔬 Logic Gate Analysis")
    
    if not st.session_state.selected_tumor_antigens and not st.session_state.selected_healthy_antigens:
        st.warning("⚠️ Please select antigens first in the Antigen Selection page.")
        return
    
    # Display selected antigens
    st.subheader("🎯 Selected Antigens for Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Tumor Antigens:**")
        if st.session_state.selected_tumor_antigens:
            for antigen in st.session_state.selected_tumor_antigens:
                st.write(f"• {antigen}")
        else:
            st.write("None selected")
    
    with col2:
        st.write("**Healthy Cell Antigens (HCA):**")
        if st.session_state.selected_healthy_antigens:
            for antigen in st.session_state.selected_healthy_antigens:
                st.write(f"• {antigen}")
        else:
            st.write("None selected")
    
    # Generate logic gate analysis
    if st.button("🚀 Generate Logic Gate Analysis"):
        with st.spinner("Analyzing logic gates..."):
            try:
                # Create analyzer
                selected_antigens = {
                    'tumor': st.session_state.selected_tumor_antigens,
                    'healthy': st.session_state.selected_healthy_antigens
                }
                
                analyzer = LogicGateAnalyzer(st.session_state.data_processor.df, selected_antigens)
                
                # Generate analysis
                truth_tables = analyzer.generate_all_truth_tables()
                best_gate = analyzer.get_best_gate_recommendation(truth_tables)
                selectivity_scores = best_gate['selectivity_scores']
                
                st.session_state.analysis_results = {
                    'truth_tables': truth_tables,
                    'selectivity_scores': selectivity_scores,
                    'best_gate': best_gate
                }
                st.success("✅ Analysis completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                return
    
    # Display results
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Recommendation section
        st.subheader("🏆 Recommended Logic Gate")
        best_gate = results['best_gate']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Best Gate", best_gate['gate'])
        with col2:
            st.metric("Selectivity Score", f"{best_gate['score']:.3f}")
        with col3:
            st.info(f"🛡️ {best_gate.get('safety_note', 'Standard monitoring recommended.')}")
        
        st.write("**Explanation:**", best_gate['explanation'])
        
        # Truth Tables section
        st.subheader("📋 Truth Tables with Your Antigens")
        st.markdown("**Legend:** 1 = Present, 0 = Absent | **🎯** = Kill, **❌** = Off")
        
        visualizer = TruthTableVisualizer()
        
        # Display truth tables in tabs
        tab_names = list(results['truth_tables'].keys())
        tabs = st.tabs([f"{gate} Gate" for gate in tab_names])
        
        for i, (gate_name, truth_table) in enumerate(results['truth_tables'].items()):
            with tabs[i]:
                if gate_name == 'NOT':
                    # Show fixed NOT gate truth table regardless of input
                    fixed_not_fig = visualizer.create_fixed_not_truth_table()
                    st.plotly_chart(fixed_not_fig, use_container_width=True)
                else:
                    simplified_fig = visualizer.create_simplified_truth_table(truth_table, gate_name)
                    st.plotly_chart(simplified_fig, use_container_width=True)
        
        # Gate Performance section
        st.subheader("📈 Gate Performance")
        selectivity_fig = visualizer.create_selectivity_comparison(results['selectivity_scores'])
        st.plotly_chart(selectivity_fig, use_container_width=True)
        
        # PDAC Insights section
        st.subheader("🩺 PDAC Insights")
        st.markdown("""
        **Best Practice for PDAC:**
        - AND gates minimize off-target effects
        - OR gates increase tumor coverage
        - Monitor pancreatic enzymes during therapy
        - Consider dose escalation protocols
        """)

def cart_diagram_page():
    st.header("🧬 Personalized CAR-T Structure for PDAC")
    
    if not st.session_state.selected_tumor_antigens:
        st.warning("⚠️ Please select tumor antigens first in the Antigen Selection page.")
        return
    
    if len(st.session_state.selected_tumor_antigens) < 2:
        st.warning("⚠️ Please select at least 2 tumor antigens for CAR-T diagram generation.")
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
        
        # CAR-T Configuration (simplified)
        st.subheader("⚙️ CAR-T Configuration")
        
        costimulatory_domain = "4-1BB"  # Fixed to 4-1BB for PDAC
        diagram_style = "Standard"  # Fixed style
        
        # Enhanced generate button
        if st.button("🚀 Generate Personalized CAR-T", type="primary", use_container_width=True):
            with st.spinner("Creating your personalized CAR-T design..."):
                # Prepare antigen data
                selected_antigens = {
                    'tumor': st.session_state.selected_tumor_antigens,
                    'healthy': st.session_state.selected_healthy_antigens
                }
                
                # Generate diagram
                diagram_gen = CARTDiagramGenerator(selected_antigens)
                svg_content = diagram_gen.generate_cart_diagram(
                    costimulatory_domain=costimulatory_domain,
                    style=diagram_style
                )
                
                # Store for display in left column
                st.session_state.cart_diagram = svg_content
                st.session_state.cart_config = {
                    'costimulatory': costimulatory_domain,
                    'style': diagram_style
                }
        
        # PDAC-specific design summary
        if 'cart_diagram' in st.session_state:
            st.subheader("📋 PDAC Design Summary")
            config = st.session_state.cart_config
            
            st.markdown(f"**🎯 Strategy:** Dual-Logic CAR-T")
            st.markdown(f"**🔴 Primary Targets:** {', '.join(st.session_state.selected_tumor_antigens[:2])}")
            st.markdown(f"**⚙️ Costimulatory:** 4-1BB (Optimized for PDAC)")
            st.markdown(f"**🛡️ Safety Profile:** Designed to spare healthy pancreatic tissue")
            
            # PDAC-specific notes
            st.info("👉 **PDAC Note:** This dual-logic design targets heterogeneous pancreatic tumors while minimizing damage to critical pancreatic functions.")
    
    with col_left:
        # Display diagram if generated
        if 'cart_diagram' in st.session_state:
            st.subheader("🧬 Your Personalized CAR-T Structure")
            # Adjust height to fit better in the available space
            components.html(st.session_state.cart_diagram, height=500, scrolling=False)
            
            # Download options
            st.subheader("💾 Export Options")
            st.download_button(
                label="💾 Download SVG",
                data=st.session_state.cart_diagram,
                file_name=f"cart_design_{'-'.join(st.session_state.selected_tumor_antigens[:2])}.svg",
                mime="image/svg+xml"
            )
        else:
            # Placeholder when no diagram is generated
            st.info("📍 Configure your CAR-T parameters on the right and click 'Generate' to see your personalized diagram here.")
            
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
