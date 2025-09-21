import streamlit as st
import pandas as pd
import numpy as np
import json
import base64
from io import BytesIO
import zipfile
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
    st.session_state.data_processor = None
if 'biomarkers_df' not in st.session_state:
    st.session_state.biomarkers_df = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

def main():
    st.title("🧬 CAR-T Design Tool for PDAC")
    st.markdown("### Dual-Logic CAR-T Strategy Designer for Pancreatic Ductal Adenocarcinoma")
    
    # Ethics disclaimer
    st.error("⚠️ **RESEARCH USE ONLY** - This tool is for research purposes only and is not intended for clinical use or medical diagnosis.")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Data Upload", "Antigen Selection", "Logic Gate Analysis", "CAR-T Diagram", "Results & Download"]
    )
    
    if page == "Data Upload":
        data_upload_page()
    elif page == "Antigen Selection":
        antigen_selection_page()
    elif page == "Logic Gate Analysis":
        logic_gate_analysis_page()
    elif page == "CAR-T Diagram":
        cart_diagram_page()
    elif page == "Results & Download":
        results_download_page()

def data_upload_page():
    st.header("📁 Data Upload & Validation")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload biomarker dataset (CSV)",
        type=['csv'],
        help="CSV file should contain: biomarker_name, category, indication (↑ oncogenic, ↓ suppressor)"
    )
    
    # Sample data option
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load Sample Dataset"):
            st.session_state.biomarkers_df = pd.read_csv("sample_data.csv")
            st.session_state.data_processor = DataProcessor(st.session_state.biomarkers_df)
            st.success("Sample dataset loaded successfully!")
    
    with col2:
        if st.button("View Sample Data Format"):
            sample_df = pd.read_csv("sample_data.csv")
            st.dataframe(sample_df.head())
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.data_processor = DataProcessor(df)
            
            # Validate dataset
            validation_result = st.session_state.data_processor.validate_dataset()
            
            if validation_result['valid']:
                st.session_state.biomarkers_df = df
                st.success("✅ Dataset uploaded and validated successfully!")
                
                # Display dataset info
                st.subheader("Dataset Overview")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Biomarkers", len(df))
                with col2:
                    st.metric("Categories", int(df['category'].nunique()))
                with col3:
                    oncogenic_count = len(df[df['indication'].str.contains('↑', na=False)])
                    st.metric("Oncogenic Markers", oncogenic_count)
                
                # Display data
                st.dataframe(df)
                
            else:
                st.error(f"❌ Dataset validation failed: {validation_result['error']}")
                
        except Exception as e:
            st.error(f"Error loading dataset: {str(e)}")

def antigen_selection_page():
    st.header("🎯 Antigen Pair Selection")
    
    if st.session_state.biomarkers_df is None:
        st.warning("Please upload a dataset first.")
        return
    
    df = st.session_state.biomarkers_df
    
    st.subheader("Select Tumor Antigens")
    col1, col2 = st.columns(2)
    
    with col1:
        tumor_antigen_1 = st.selectbox(
            "Tumor Antigen 1",
            options=df['biomarker_name'].tolist(),
            key="tumor_ag1"
        )
        
    with col2:
        tumor_antigen_2 = st.selectbox(
            "Tumor Antigen 2",
            options=[marker for marker in df['biomarker_name'].tolist() if marker != tumor_antigen_1],
            key="tumor_ag2"
        )
    
    st.subheader("Select Healthy Cell Antigens")
    col3, col4 = st.columns(2)
    
    with col3:
        healthy_antigen_1 = st.selectbox(
            "Healthy Cell Antigen 1",
            options=df['biomarker_name'].tolist(),
            key="healthy_ag1"
        )
        
    with col4:
        healthy_antigen_2 = st.selectbox(
            "Healthy Cell Antigen 2",
            options=[marker for marker in df['biomarker_name'].tolist() if marker != healthy_antigen_1],
            key="healthy_ag2"
        )
    
    # Display selected antigens
    if st.button("Confirm Antigen Selection"):
        st.session_state.selected_antigens = {
            'tumor': [tumor_antigen_1, tumor_antigen_2],
            'healthy': [healthy_antigen_1, healthy_antigen_2]
        }
        
        st.success("✅ Antigen selection confirmed!")
        
        # Display selection summary
        st.subheader("Selection Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Tumor Antigens:**")
            for ag in st.session_state.selected_antigens['tumor']:
                antigen_info = df[df['biomarker_name'] == ag].iloc[0]
                st.write(f"• {ag} ({antigen_info['category']}) - {antigen_info['indication']}")
        
        with col2:
            st.write("**Healthy Cell Antigens:**")
            for ag in st.session_state.selected_antigens['healthy']:
                antigen_info = df[df['biomarker_name'] == ag].iloc[0]
                st.write(f"• {ag} ({antigen_info['category']}) - {antigen_info['indication']}")

def logic_gate_analysis_page():
    st.header("🔬 Truth Table & Logic Gate Analysis")
    
    if not hasattr(st.session_state, 'selected_antigens'):
        st.warning("Please select antigens first.")
        return
    
    # Initialize logic gate analyzer
    analyzer = LogicGateAnalyzer(st.session_state.biomarkers_df, st.session_state.selected_antigens)
    
    # Generate truth tables
    if st.button("Generate Truth Tables & Analysis"):
        with st.spinner("Analyzing logic gates..."):
            # Generate truth tables for all gates
            truth_tables = analyzer.generate_all_truth_tables()
            
            # Calculate selectivity scores
            selectivity_scores = analyzer.calculate_selectivity_scores(truth_tables)
            
            # Get best gate recommendation
            best_gate = analyzer.get_best_gate_recommendation(selectivity_scores)
            
            st.session_state.analysis_results = {
                'truth_tables': truth_tables,
                'selectivity_scores': selectivity_scores,
                'best_gate': best_gate
            }
    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Display best gate recommendation
        st.subheader("🏆 Best Logic Gate Recommendation")
        best_gate = results['best_gate']
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Recommended Gate", best_gate['gate'])
            st.metric("Selectivity Score", f"{best_gate['score']:.3f}")
        
        with col2:
            st.write("**Explanation:**")
            st.write(best_gate['explanation'])
        
        # Display selectivity scores for all gates
        st.subheader("📊 Selectivity Score Rankings")
        scores_df = pd.DataFrame([
            {'Gate': gate, 'Selectivity Score': score, 'Rank': idx + 1}
            for idx, (gate, score) in enumerate(
                sorted(results['selectivity_scores'].items(), key=lambda x: x[1], reverse=True)
            )
        ])
        st.dataframe(scores_df)
        
        # Display truth tables
        st.subheader("📋 Truth Tables")
        visualizer = TruthTableVisualizer()
        
        for gate_name, truth_table in results['truth_tables'].items():
            with st.expander(f"{gate_name} Truth Table"):
                fig = visualizer.create_truth_table_heatmap(truth_table, gate_name)
                st.plotly_chart(fig, use_container_width=True)

def cart_diagram_page():
    st.header("🧬 CAR-T Structure Diagram")
    
    if not hasattr(st.session_state, 'selected_antigens'):
        st.warning("Please select antigens first.")
        return
    
    # Initialize diagram generator
    diagram_gen = CARTDiagramGenerator(st.session_state.selected_antigens)
    
    # Customization options
    st.subheader("Diagram Customization")
    col1, col2 = st.columns(2)
    
    with col1:
        costimulatory_domain = st.selectbox(
            "Costimulatory Domain",
            options=["CD28", "4-1BB"],
            help="Select the costimulatory domain for the CAR-T construct"
        )
    
    with col2:
        diagram_style = st.selectbox(
            "Diagram Style",
            options=["Standard", "Detailed", "Simplified"],
            help="Choose the level of detail for the diagram"
        )
    
    if st.button("Generate CAR-T Diagram"):
        with st.spinner("Generating personalized CAR-T diagram..."):
            # Generate SVG diagram
            svg_content = diagram_gen.generate_cart_diagram(
                costimulatory_domain=costimulatory_domain,
                style=diagram_style
            )
            
            # Display diagram
            st.subheader("Personalized CAR-T Structure")
            st.components.v1.html(svg_content, height=600)
            
            # Store diagram for download
            st.session_state.cart_diagram_svg = svg_content
            
            # Generate PNG version
            png_data = diagram_gen.svg_to_png(svg_content)
            st.session_state.cart_diagram_png = png_data
            
            # Display download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download SVG",
                    data=svg_content,
                    file_name="cart_diagram.svg",
                    mime="image/svg+xml"
                )
            
            with col2:
                st.download_button(
                    label="Download PNG",
                    data=png_data,
                    file_name="cart_diagram.png",
                    mime="image/png"
                )

def results_download_page():
    st.header("📥 Results & Download")
    
    if not hasattr(st.session_state, 'analysis_results'):
        st.warning("Please complete the analysis first.")
        return
    
    st.subheader("Available Downloads")
    
    # Prepare download data
    results = st.session_state.analysis_results
    
    # Truth tables as CSV
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download Truth Tables (CSV)"):
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for gate_name, truth_table in results['truth_tables'].items():
                    csv_data = pd.DataFrame(truth_table).to_csv(index=False)
                    zip_file.writestr(f"{gate_name}_truth_table.csv", csv_data)
            
            st.download_button(
                label="Download ZIP",
                data=zip_buffer.getvalue(),
                file_name="truth_tables.zip",
                mime="application/zip"
            )
    
    with col2:
        if st.button("Download Analysis Results (JSON)"):
            json_data = {
                'selected_antigens': st.session_state.selected_antigens,
                'selectivity_scores': results['selectivity_scores'],
                'best_gate': results['best_gate'],
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            }
            
            st.download_button(
                label="Download JSON",
                data=json.dumps(json_data, indent=2),
                file_name="analysis_results.json",
                mime="application/json"
            )
    
    with col3:
        if hasattr(st.session_state, 'cart_diagram_svg'):
            st.download_button(
                label="Download CAR-T Diagram (SVG)",
                data=st.session_state.cart_diagram_svg,
                file_name="cart_diagram.svg",
                mime="image/svg+xml"
            )
    
    # Summary report
    st.subheader("Analysis Summary")
    
    if hasattr(st.session_state, 'selected_antigens'):
        st.write("**Selected Antigens:**")
        st.write(f"Tumor: {', '.join(st.session_state.selected_antigens['tumor'])}")
        st.write(f"Healthy: {', '.join(st.session_state.selected_antigens['healthy'])}")
        
        st.write("**Best Logic Gate:**")
        best_gate = results['best_gate']
        st.write(f"Gate: {best_gate['gate']}")
        st.write(f"Selectivity Score: {best_gate['score']:.3f}")
        st.write(f"Explanation: {best_gate['explanation']}")

if __name__ == "__main__":
    main()
