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

def main():
    apply_theme()
    
    # Theme toggle button
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("🌓", key="theme_toggle", help="Toggle Dark/Light Mode"):
            toggle_theme()
            st.rerun()
    
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
            st.dataframe(display_df[['biomarker_name', 'category', 'indication']], use_container_width=True)
    
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
    
    if len(st.session_state.selected_tumor_antigens) < 2:
        st.warning("⚠️ Please select at least 2 tumor antigens for logic gate analysis.")
        return
    
    # Show constraint message if more than 2 selected
    if len(st.session_state.selected_tumor_antigens) > 2:
        st.info(f"ℹ️ Logic gate analysis uses the first 2 tumor antigens for binary logic gates. Selected: {st.session_state.selected_tumor_antigens[:2]}")
    
    # Display selected antigens for analysis
    st.subheader("🎯 Selected Antigens for Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Tumor Antigens (for Binary Logic):**")
        for i, antigen in enumerate(st.session_state.selected_tumor_antigens[:2]):
            st.write(f"• Input {chr(65+i)}: {antigen}")
    
    with col2:
        st.write("**Healthy Cell Antigens:**")
        for antigen in st.session_state.selected_healthy_antigens:
            st.write(f"• {antigen}")
    
    # Generate logic gate analysis
    if st.button("🚀 Generate Logic Gate Analysis"):
        with st.spinner("Analyzing logic gates..."):
            # Create analyzer with proper data structure
            selected_antigens = {
                'tumor': st.session_state.selected_tumor_antigens[:2],  # Use first 2 for binary logic
                'healthy': st.session_state.selected_healthy_antigens
            }
            
            analyzer = LogicGateAnalyzer(st.session_state.data_processor.df, selected_antigens)
            
            # Generate analysis
            truth_tables = analyzer.generate_all_truth_tables()
            selectivity_scores = analyzer.calculate_selectivity_scores(truth_tables)
            best_gate = analyzer.get_best_gate_recommendation(selectivity_scores)
            
            st.session_state.analysis_results = {
                'truth_tables': truth_tables,
                'selectivity_scores': selectivity_scores,
                'best_gate': best_gate
            }
    
    # Display results
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Best gate recommendation
        st.subheader("🏆 Best Logic Gate Recommendation")
        best_gate = results['best_gate']
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Recommended Gate", best_gate['gate'])
            st.metric("Selectivity Score", f"{best_gate['score']:.3f}")
        
        with col2:
            st.write("**Explanation:**")
            st.write(best_gate['explanation'])
        
        # Selectivity scores comparison
        st.subheader("📊 Logic Gate Selectivity Comparison")
        scores_df = pd.DataFrame([
            {'Gate': gate, 'Selectivity Score': f"{score:.3f}", 'Rank': idx + 1}
            for idx, (gate, score) in enumerate(
                sorted(results['selectivity_scores'].items(), key=lambda x: x[1], reverse=True)
            )
        ])
        st.dataframe(scores_df, use_container_width=True)
        
        # Truth tables
        st.subheader("📋 Truth Tables")
        
        for gate_name, truth_table in results['truth_tables'].items():
            with st.expander(f"📈 {gate_name} Gate Truth Table"):
                # Create tabular display
                table_data = []
                inputs = truth_table['inputs']
                outputs = truth_table['outputs']
                probabilities = truth_table['probabilities']
                cell_types = truth_table['cell_types']
                
                for i in range(len(inputs)):
                    input_str = ''.join(map(str, inputs[i]))
                    table_data.append({
                        'Input Pattern': input_str,
                        'Hard Logic Output': outputs[i],
                        'Probabilistic Output': f"{probabilities[i]:.3f}",
                        'Cell Type': cell_types[i]
                    })
                
                truth_df = pd.DataFrame(table_data)
                st.dataframe(truth_df, use_container_width=True)
                
                # Visualize with heatmap
                visualizer = TruthTableVisualizer()
                fig = visualizer.create_truth_table_heatmap(truth_table, gate_name)
                st.plotly_chart(fig, use_container_width=True)

def cart_diagram_page():
    st.header("🧬 CAR-T Structure Diagram")
    
    if not st.session_state.selected_tumor_antigens:
        st.warning("⚠️ Please select tumor antigens first in the Antigen Selection page.")
        return
    
    if len(st.session_state.selected_tumor_antigens) < 2:
        st.warning("⚠️ Please select at least 2 tumor antigens for CAR-T diagram generation.")
        return
    
    # Selected antigens summary
    st.subheader("🎯 Selected Antigens for CAR-T Design")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Tumor Antigens (Target for Killing):**")
        for antigen in st.session_state.selected_tumor_antigens:
            st.write(f"🔴 {antigen}")
    
    with col2:
        st.write("**Healthy Cell Antigens (Protect from Killing):**")
        for antigen in st.session_state.selected_healthy_antigens:
            st.write(f"🟢 {antigen}")
    
    # Diagram customization
    st.subheader("⚙️ Diagram Customization")
    col1, col2 = st.columns(2)
    
    with col1:
        costimulatory_domain = st.selectbox(
            "Costimulatory Domain:",
            options=["CD28", "4-1BB"],
            help="Select the costimulatory domain for the CAR-T construct"
        )
    
    with col2:
        diagram_style = st.selectbox(
            "Diagram Style:",
            options=["Standard", "Detailed", "Simplified"],
            help="Choose the level of detail for the diagram"
        )
    
    if st.button("🚀 Generate CAR-T Diagram"):
        with st.spinner("Generating personalized CAR-T diagram..."):
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
            
            # Display diagram
            st.subheader("🧬 Personalized CAR-T Structure")
            components.html(svg_content, height=600)
            
            # Information about the design
            st.subheader("📋 CAR-T Design Summary")
            st.write(f"**Target Strategy:** Dual-logic CAR-T for PDAC")
            st.write(f"**Primary Targets:** {', '.join(st.session_state.selected_tumor_antigens[:2])}")
            st.write(f"**Costimulatory Domain:** {costimulatory_domain}")
            st.write(f"**Design Principle:** Selectively target tumor cells expressing oncogenic markers while sparing healthy cells with tumor suppressor expression")

if __name__ == "__main__":
    main()