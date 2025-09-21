
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
    page_title="ImmunoGate: Dual Logic CAR-T Cell Therapy for PDAC",
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
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = 'light'

def apply_medical_styling():
    """Apply modern medical-themed CSS styling with dark/light mode support."""
    theme = st.session_state.theme_mode
    
    if theme == 'dark':
        primary_bg = "linear-gradient(135deg, #1a202c 0%, #2d3748 50%, #4a5568 100%)"
        card_bg = "rgba(45, 55, 72, 0.95)"
        text_primary = "#f7fafc"
        text_secondary = "#e2e8f0"
        border_color = "#4a5568"
        accent_color = "#63b3ed"
        accent_hover = "#4299e1"
        success_color = "#68d391"
        danger_color = "#fc8181"
        warning_color = "#f6e05e"
        sidebar_bg = "rgba(26, 32, 44, 0.98)"
        glass_bg = "rgba(45, 55, 72, 0.85)"
        shadow_color = "rgba(0, 0, 0, 0.4)"
    else:
        primary_bg = "linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 30%, #bae6fd 70%, #7dd3fc 100%)"
        card_bg = "rgba(255, 255, 255, 0.95)"
        text_primary = "#1e293b"
        text_secondary = "#64748b"
        border_color = "#e2e8f0"
        accent_color = "#0ea5e9"
        accent_hover = "#0284c7"
        success_color = "#10b981"
        danger_color = "#ef4444"
        warning_color = "#f59e0b"
        sidebar_bg = "rgba(255, 255, 255, 0.98)"
        glass_bg = "rgba(255, 255, 255, 0.85)"
        shadow_color = "rgba(0, 0, 0, 0.1)"
    
    st.markdown(f"""
    <style>
    /* Import Medical-grade Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root CSS Variables for Theme Management */
    :root {{
        --primary-bg: {primary_bg};
        --card-bg: {card_bg};
        --text-primary: {text_primary};
        --text-secondary: {text_secondary};
        --border-color: {border_color};
        --accent-color: {accent_color};
        --accent-hover: {accent_hover};
        --success-color: {success_color};
        --danger-color: {danger_color};
        --warning-color: {warning_color};
        --sidebar-bg: {sidebar_bg};
        --glass-bg: {glass_bg};
        --shadow-color: {shadow_color};
        --medical-blue: #1e40af;
        --medical-teal: #0d9488;
        --medical-green: #059669;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    /* Global Application Styling */
    .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: var(--primary-bg);
        min-height: 100vh;
        transition: var(--transition);
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{visibility: hidden;}}
    
    /* Theme Toggle Button */
    .theme-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 25px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        cursor: pointer;
        transition: var(--transition);
        box-shadow: 0 4px 12px var(--shadow-color);
        backdrop-filter: blur(10px);
    }}
    
    .theme-toggle:hover {{
        background: var(--accent-color);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px var(--shadow-color);
    }}
    
    /* Enhanced Medical Header */
    .medical-header {{
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 1rem 0 2rem 0;
        box-shadow: 0 10px 30px var(--shadow-color);
        border: 1px solid var(--border-color);
        position: relative;
        overflow: hidden;
        transition: var(--transition);
    }}
    
    .medical-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--medical-blue), var(--medical-teal), var(--medical-green));
    }}
    
    .medical-title {{
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--medical-blue) 0%, var(--medical-teal) 50%, var(--medical-green) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }}
    
    .medical-subtitle {{
        font-size: 1.25rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }}
    
    .disclaimer-badge {{
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 50%);
        color: #991b1b;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 2px solid #fca5a5;
        display: inline-block;
    }}
    
    /* Medical Card System */
    .medical-card {{
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px var(--shadow-color);
        border: 1px solid var(--border-color);
        transition: var(--transition);
        position: relative;
    }}
    
    .medical-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 20px 40px var(--shadow-color);
    }}
    
    .medical-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-color), var(--medical-teal));
        border-radius: 20px 20px 0 0;
    }}
    
    /* Enhanced Sidebar */
    .css-1d391kg {{
        background: var(--sidebar-bg) !important;
        backdrop-filter: blur(20px);
        border-radius: 0 20px 20px 0;
        box-shadow: 0 0 30px var(--shadow-color);
        border-right: 1px solid var(--border-color);
    }}
    
    .css-1lcbmhc {{
        background: transparent;
        padding-top: 2rem;
    }}
    
    /* Navigation Enhancement */
    .stRadio > div {{
        background: var(--glass-bg);
        border-radius: 15px;
        padding: 1.5rem;
        backdrop-filter: blur(15px);
        border: 1px solid var(--border-color);
    }}
    
    .stRadio > div > label {{
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        transition: var(--transition);
        cursor: pointer;
        font-weight: 500;
        font-size: 1rem;
        color: var(--text-primary);
        border: 1px solid transparent;
    }}
    
    .stRadio > div > label:hover {{
        background: var(--accent-color);
        color: white;
        transform: translateX(8px) scale(1.02);
        border-color: var(--accent-hover);
    }}
    
    /* Enhanced Button System */
    .stButton > button {{
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-hover) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: var(--transition);
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4);
        background: linear-gradient(135deg, var(--accent-hover) 0%, var(--medical-teal) 100%);
    }}
    
    .stButton > button:active {{
        transform: translateY(-1px);
    }}
    
    /* Primary Button Variant */
    .primary-button {{
        background: linear-gradient(135deg, var(--medical-blue) 0%, var(--medical-teal) 100%) !important;
        box-shadow: 0 4px 15px rgba(30, 64, 175, 0.3) !important;
    }}
    
    .success-button {{
        background: linear-gradient(135deg, var(--success-color) 0%, var(--medical-green) 100%) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }}
    
    .danger-button {{
        background: linear-gradient(135deg, var(--danger-color) 0%, #dc2626 100%) !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3) !important;
    }}
    
    /* Medical Metrics Cards */
    .metric-card {{
        background: var(--card-bg);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 25px var(--shadow-color);
        transition: var(--transition);
        border: 1px solid var(--border-color);
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--accent-color);
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 35px var(--shadow-color);
    }}
    
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--accent-color);
        margin-bottom: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
    }}
    
    .metric-label {{
        font-size: 1rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Enhanced Form Controls */
    .stSelectbox > div > div, .stMultiSelect > div > div {{
        background: var(--card-bg) !important;
        border-radius: 12px !important;
        border: 2px solid var(--border-color) !important;
        transition: var(--transition) !important;
        backdrop-filter: blur(10px) !important;
        color: var(--text-primary) !important;
    }}
    
    .stSelectbox > div > div:focus-within, .stMultiSelect > div > div:focus-within {{
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1) !important;
        transform: scale(1.02) !important;
    }}
    
    /* Enhanced DataFrames */
    .stDataFrame {{
        background: var(--card-bg);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 25px var(--shadow-color);
        backdrop-filter: blur(15px);
        border: 1px solid var(--border-color);
    }}
    
    /* Medical Alert System */
    .medical-alert {{
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-weight: 500;
        border-left: 4px solid;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px var(--shadow-color);
    }}
    
    .medical-alert.success {{
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
        border-left-color: var(--success-color);
        color: var(--success-color);
    }}
    
    .medical-alert.error {{
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
        border-left-color: var(--danger-color);
        color: var(--danger-color);
    }}
    
    .medical-alert.warning {{
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%);
        border-left-color: var(--warning-color);
        color: var(--warning-color);
    }}
    
    /* Antigen Selection Cards */
    .antigen-card {{
        background: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: var(--transition);
        position: relative;
        backdrop-filter: blur(10px);
    }}
    
    .antigen-card.tumor {{
        border-left: 4px solid var(--danger-color);
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, transparent 100%);
    }}
    
    .antigen-card.healthy {{
        border-left: 4px solid var(--success-color);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, transparent 100%);
    }}
    
    .antigen-card:hover {{
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 8px 20px var(--shadow-color);
    }}
    
    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: var(--glass-bg);
        border-radius: 15px;
        padding: 0.5rem;
        backdrop-filter: blur(15px);
        border: 1px solid var(--border-color);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: var(--transition);
        color: var(--text-primary);
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-hover) 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
    }}
    
    /* Plotly Chart Enhancements */
    .js-plotly-plot {{
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 25px var(--shadow-color);
        border: 1px solid var(--border-color);
    }}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .medical-title {{
            font-size: 2rem;
        }}
        
        .medical-card {{
            padding: 1.5rem;
            margin: 1rem 0;
        }}
        
        .metric-card {{
            padding: 1.5rem;
        }}
        
        .metric-value {{
            font-size: 2rem;
        }}
        
        .theme-toggle {{
            top: 10px;
            right: 10px;
            padding: 6px 12px;
            font-size: 12px;
        }}
    }}
    
    @media (max-width: 480px) {{
        .medical-title {{
            font-size: 1.75rem;
        }}
        
        .medical-subtitle {{
            font-size: 1rem;
        }}
        
        .medical-card {{
            padding: 1rem;
            border-radius: 15px;
        }}
        
        .metric-card {{
            padding: 1rem;
        }}
        
        .metric-value {{
            font-size: 1.5rem;
        }}
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--border-color);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--accent-color);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--accent-hover);
    }}
    
    /* Loading States */
    .loading-shimmer {{
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 2s infinite;
    }}
    
    @keyframes shimmer {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}
    
    /* Animation Classes */
    .fade-in {{
        animation: fadeIn 0.6s ease-out;
    }}
    
    .slide-up {{
        animation: slideUp 0.6s ease-out;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    @keyframes slideUp {{
        from {{ 
            opacity: 0;
            transform: translateY(20px); 
        }}
        to {{ 
            opacity: 1;
            transform: translateY(0); 
        }}
    }}
    
    /* Focus States for Accessibility */
    .stButton > button:focus,
    .stSelectbox > div > div:focus,
    .stMultiSelect > div > div:focus {{
        outline: 3px solid var(--accent-color);
        outline-offset: 2px;
    }}
    </style>
    """, unsafe_allow_html=True)

def toggle_theme():
    """Toggle between light and dark themes."""
    st.session_state.theme_mode = 'dark' if st.session_state.theme_mode == 'light' else 'light'

def create_theme_toggle():
    """Create theme toggle button."""
    theme_icon = "🌙" if st.session_state.theme_mode == 'light' else "☀️"
    theme_text = "Dark" if st.session_state.theme_mode == 'light' else "Light"
    
    st.markdown(f"""
    <button class="theme-toggle" onclick="window.parent.postMessage({{type: 'streamlit:themeToggle'}}, '*')">
        {theme_icon} {theme_text} Mode
    </button>
    """, unsafe_allow_html=True)

def reset_all_selections():
    """Reset all user selections and analysis results."""
    st.session_state.selected_tumor_antigens = []
    st.session_state.selected_healthy_antigens = []
    st.session_state.analysis_results = None
    st.rerun()

def create_medical_header():
    """Create medical-themed header with professional design."""
    st.markdown("""
    <div class="medical-header fade-in">
        <h1 class="medical-title">🧬 ImmunoGate</h1>
        <p class="medical-subtitle">Advanced Dual Logic CAR-T Cell Therapy Platform for PDAC</p>
        <div style="text-align: center; margin-top: 1.5rem;">
            <span class="disclaimer-badge">
                ⚠️ RESEARCH USE ONLY - Not for clinical diagnosis or treatment
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, icon="📊", color="accent"):
    """Create enhanced metric card with medical styling."""
    return f"""
    <div class="metric-card slide-up">
        <div style="font-size: 2.5rem; margin-bottom: 1rem; color: var(--{color}-color);">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
    </div>
    """

def main():
    apply_medical_styling()
    
    # Theme toggle in header
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("🔄", key="refresh_all", help="Reset All Selections"):
            reset_all_selections()
        
        # Theme toggle button
        theme_icon = "🌙" if st.session_state.theme_mode == 'light' else "☀️"
        if st.button(theme_icon, key="theme_toggle", help="Toggle Theme"):
            toggle_theme()
            st.rerun()
    
    # Medical header
    create_medical_header()
    
    # Enhanced sidebar navigation
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1.5rem 0; border-bottom: 2px solid var(--border-color); margin-bottom: 1.5rem;">
        <h3 style="color: var(--accent-color); font-weight: 700; margin: 0; font-size: 1.5rem;">Navigation Center</h3>
        <p style="color: var(--text-secondary); margin: 0.5rem 0 0 0; font-size: 0.9rem;">Select Analysis Module</p>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Choose Analysis Module:",
        ["🎯 Antigen Selection", "🔬 Logic Gate Analysis", "🧬 CAR-T Diagram"],
        key="navigation"
    )
    
    # Auto-refresh logic gate analysis and CAR-T diagram when antigens change
    if page in ["🔬 Logic Gate Analysis", "🧬 CAR-T Diagram"]:
        # Auto-generate analysis if antigens are selected
        if (st.session_state.selected_tumor_antigens or st.session_state.selected_healthy_antigens) and not st.session_state.analysis_results:
            with st.spinner("🧠 Auto-generating advanced analysis..."):
                try:
                    selected_antigens = {
                        'tumor': st.session_state.selected_tumor_antigens,
                        'healthy': st.session_state.selected_healthy_antigens
                    }
                    
                    analyzer = LogicGateAnalyzer(st.session_state.data_processor.df, selected_antigens)
                    truth_tables = analyzer.generate_all_truth_tables()
                    best_gate = analyzer.get_best_gate_recommendation(truth_tables)
                    selectivity_scores = best_gate['selectivity_scores']
                    
                    st.session_state.analysis_results = {
                        'truth_tables': truth_tables,
                        'selectivity_scores': selectivity_scores,
                        'best_gate': best_gate
                    }
                except Exception as e:
                    st.error(f"Auto-analysis error: {str(e)}")
    
    # Route to pages
    if page == "🎯 Antigen Selection":
        antigen_selection_page()
    elif page == "🔬 Logic Gate Analysis":
        logic_gate_analysis_page()
    elif page == "🧬 CAR-T Diagram":
        cart_diagram_page()

def antigen_selection_page():
    """Enhanced antigen selection page with medical UI."""
    st.markdown('<div class="medical-card slide-up">', unsafe_allow_html=True)
    st.markdown("### 🎯 Intelligent Biomarker Selection Platform")
    st.markdown("Advanced antigen selection system with real-time validation and clinical insights")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced dataset overview with animated metrics
    st.markdown('<div class="medical-card fade-in">', unsafe_allow_html=True)
    st.markdown("### 📊 Dataset Intelligence Dashboard")
    
    total_biomarkers = sum(len(biomarkers) for biomarkers in st.session_state.biomarkers_data.values())
    oncogenic_count = len(st.session_state.data_processor.get_oncogenic_biomarkers())
    category_count = len(st.session_state.biomarkers_data)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card("Total Biomarkers", total_biomarkers, "🧬", "medical-blue"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Categories", category_count, "📂", "medical-teal"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Oncogenic Markers", oncogenic_count, "🎯", "medical-green"), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced category selection
    st.markdown('<div class="medical-card slide-up">', unsafe_allow_html=True)
    st.markdown("### 🗂️ Biomarker Category Explorer")
    
    # Create category options with biomarker counts
    category_options = []
    for category, biomarkers in st.session_state.biomarkers_data.items():
        count = len(biomarkers)
        category_options.append(f"{category} ({count} biomarkers)")
    
    selected_category_with_count = st.selectbox(
        "Select Biomarker Category:",
        category_options,
        key="category_selector",
        help="Choose a biomarker category to explore available antigens"
    )
    
    # Extract actual category name (remove count)
    selected_category = selected_category_with_count.split(' (')[0] if selected_category_with_count else None
    
    if selected_category:
        biomarkers_in_category = st.session_state.biomarkers_data[selected_category]
        
        # Process indications
        processed_biomarkers = []
        for b in biomarkers_in_category:
            clean_indication = st.session_state.data_processor.clean_indication(b['indication'])
            processed_biomarkers.append({**b, 'indication_clean': clean_indication})
        
        # Enhanced selection interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔴 Tumor Target Antigens (Oncogenic ↑)")
            tumor_options = [b['biomarker_name'] for b in processed_biomarkers 
                           if b['indication_clean'] in ['↑', '↑/↓']]
            selected_tumor = st.multiselect(
                "Select targets for CAR-T activation:",
                tumor_options,
                default=[x for x in st.session_state.selected_tumor_antigens if x in tumor_options],
                key=f"tumor_{selected_category}",
                help="These antigens will trigger CAR-T cell activation and elimination"
            )
        
        with col2:
            st.markdown("#### 🟢 Healthy Cell Protection Antigens (Suppressors ↓)")
            healthy_options = [b['biomarker_name'] for b in processed_biomarkers 
                             if b['indication_clean'] in ['↓', '↑/↓']]
            selected_healthy = st.multiselect(
                "Select targets for tissue protection:",
                healthy_options,
                default=[x for x in st.session_state.selected_healthy_antigens if x in healthy_options],
                key=f"healthy_{selected_category}",
                help="These antigens will prevent CAR-T activation to protect healthy tissue"
            )
        
        # Update global selections
        st.session_state.selected_tumor_antigens = [
            x for x in st.session_state.selected_tumor_antigens 
            if x not in [b['biomarker_name'] for b in biomarkers_in_category]
        ] + selected_tumor
        
        st.session_state.selected_healthy_antigens = [
            x for x in st.session_state.selected_healthy_antigens 
            if x not in [b['biomarker_name'] for b in biomarkers_in_category]
        ] + selected_healthy
        
        # Clear analysis results when selections change
        if 'analysis_results' in st.session_state:
            st.session_state.analysis_results = None
        
        # Enhanced data display
        display_df = pd.DataFrame(biomarkers_in_category)
        if not display_df.empty:
            display_df = display_df[['biomarker_name', 'category', 'indication']].copy()
            st.markdown("#### 📋 Biomarker Clinical Profile")
            st.dataframe(display_df, width=None)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced selection summary
    st.markdown('<div class="medical-card slide-up">', unsafe_allow_html=True)
    st.markdown("### 📋 Current Selection Portfolio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 Selected Tumor Antigens")
        if st.session_state.selected_tumor_antigens:
            for i, antigen in enumerate(st.session_state.selected_tumor_antigens):
                st.markdown(f"""
                <div class="antigen-card tumor">
                    <strong>{i+1}. {antigen}</strong><br>
                    <span style="color: var(--danger-color); font-weight: 600;">🎯 ELIMINATION TARGET</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="medical-alert warning">
                <strong>No tumor antigens selected</strong><br>
                Select at least one tumor antigen to proceed with analysis.
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🟢 Selected Healthy Cell Antigens")
        if st.session_state.selected_healthy_antigens:
            for i, antigen in enumerate(st.session_state.selected_healthy_antigens):
                st.markdown(f"""
                <div class="antigen-card healthy">
                    <strong>{i+1}. {antigen}</strong><br>
                    <span style="color: var(--success-color); font-weight: 600;">🛡️ PROTECTION MARKER</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="medical-alert">
                <strong>No protection antigens selected</strong><br>
                Consider adding healthy cell markers for enhanced safety.
            </div>
            """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All Selections", type="secondary", use_container_width=True):
            st.session_state.selected_tumor_antigens = []
            st.session_state.selected_healthy_antigens = []
            st.session_state.analysis_results = None
            st.rerun()
    
    with col2:
        total_selected = len(st.session_state.selected_tumor_antigens) + len(st.session_state.selected_healthy_antigens)
        if total_selected > 0:
            st.markdown(f"""
            <div class="medical-alert success">
                <strong>✅ Selection Complete: {total_selected} antigens</strong><br>
                Ready for advanced logic gate analysis
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def logic_gate_analysis_page():
    """Enhanced logic gate analysis page."""
    st.markdown('<div class="medical-card slide-up">', unsafe_allow_html=True)
    st.markdown("### 🔬 Advanced Logic Gate Analysis Engine")
    st.markdown("AI-powered optimization of dual-target CAR-T therapy strategies with clinical insights")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not st.session_state.selected_tumor_antigens and not st.session_state.selected_healthy_antigens:
        st.markdown("""
        <div class="medical-alert warning">
            <h4 style="margin: 0 0 1rem 0;">⚠️ Insufficient Input Data</h4>
            <p style="margin: 0;">Navigate to <strong>Antigen Selection</strong> to begin biomarker selection and enable analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display selected antigens with medical styling
    st.markdown('<div class="medical-card fade-in">', unsafe_allow_html=True)
    st.markdown("### 🎯 Analysis Input Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 Primary Tumor Targets")
        if st.session_state.selected_tumor_antigens:
            for antigen in st.session_state.selected_tumor_antigens:
                st.markdown(f"""
                <div class="antigen-card tumor">
                    <strong>{antigen}</strong> → 🎯 <span style="color: var(--danger-color);">Elimination Signal</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("None selected")
    
    with col2:
        st.markdown("#### 🟢 Healthy Cell Antigens (HCA)")
        if st.session_state.selected_healthy_antigens:
            for antigen in st.session_state.selected_healthy_antigens:
                st.markdown(f"""
                <div class="antigen-card healthy">
                    <strong>{antigen}</strong> → 🛡️ <span style="color: var(--success-color);">Protection Signal</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("None selected")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis generation
    if not st.session_state.analysis_results:
        if st.button("🚀 Generate Clinical Analysis", type="primary", use_container_width=True):
            with st.spinner("🧠 Processing advanced AI algorithms..."):
                try:
                    selected_antigens = {
                        'tumor': st.session_state.selected_tumor_antigens,
                        'healthy': st.session_state.selected_healthy_antigens
                    }
                    
                    analyzer = LogicGateAnalyzer(st.session_state.data_processor.df, selected_antigens)
                    truth_tables = analyzer.generate_all_truth_tables()
                    best_gate = analyzer.get_best_gate_recommendation(truth_tables)
                    selectivity_scores = best_gate['selectivity_scores']
                    
                    st.session_state.analysis_results = {
                        'truth_tables': truth_tables,
                        'selectivity_scores': selectivity_scores,
                        'best_gate': best_gate
                    }
                    
                    st.markdown("""
                    <div class="medical-alert success">
                        <h4 style="margin: 0 0 1rem 0;">✅ Analysis Complete</h4>
                        <p style="margin: 0;">Advanced logic gate optimization completed with clinical recommendations.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                    
                except Exception as e:
                    st.markdown(f"""
                    <div class="medical-alert error">
                        <h4 style="margin: 0 0 1rem 0;">❌ Analysis Error</h4>
                        <p style="margin: 0;">System error during analysis: {str(e)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    return
    
    # Display results with enhanced styling
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # AI Recommendation section
        st.markdown('<div class="medical-card slide-up">', unsafe_allow_html=True)
        st.markdown("### 🏆 AI-Powered Clinical Recommendation")
        
        best_gate = results['best_gate']
        
        # Create recommendation card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, var(--success-color) 0%, var(--medical-green) 100%); color: white; padding: 2.5rem; border-radius: 20px; text-align: center; margin: 1.5rem 0; box-shadow: 0 15px 35px rgba(16, 185, 129, 0.3);">
            <h2 style="margin: 0 0 1rem 0; font-size: 3rem; font-weight: 800;">🏆 {best_gate['gate']} GATE</h2>
            <div style="font-size: 1.4rem; margin-bottom: 1.5rem; font-weight: 600;">
                <strong>Clinical Selectivity Score: {best_gate['score']:.3f}</strong>
            </div>
            <p style="margin: 0; font-size: 1.2rem; opacity: 0.95; line-height: 1.5;">{best_gate['explanation']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Safety note
        if 'safety_note' in best_gate:
            st.markdown(f"""
            <div class="medical-alert warning">
                <strong>🛡️ Clinical Safety Recommendation:</strong> {best_gate['safety_note']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Truth Tables section
        st.markdown('<div class="medical-card fade-in">', unsafe_allow_html=True)
        st.markdown("### 📋 Interactive Truth Tables & Logic Analysis")
        st.markdown("**Clinical Legend:** 1 = Antigen Present, 0 = Antigen Absent | **Output:** 🎯 = Activate CAR-T, ❌ = Deactivate")
        
        visualizer = TruthTableVisualizer()
        
        # Enhanced tabs
        tab_names = list(results['truth_tables'].keys())
        tabs = st.tabs([f"🔘 {gate} Gate Logic" for gate in tab_names])
        
        for i, (gate_name, truth_table) in enumerate(results['truth_tables'].items()):
            with tabs[i]:
                if gate_name == 'NOT':
                    fixed_not_fig = visualizer.create_fixed_not_truth_table()
                    st.plotly_chart(fixed_not_fig, width=None)
                else:
                    simplified_fig = visualizer.create_simplified_truth_table(truth_table, gate_name)
                    st.plotly_chart(simplified_fig, width=None)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Performance Analytics
        st.markdown('<div class="medical-card slide-up">', unsafe_allow_html=True)
        st.markdown("### 📈 Clinical Performance Analytics")
        selectivity_fig = visualizer.create_selectivity_comparison(results['selectivity_scores'])
        st.plotly_chart(selectivity_fig, width=None)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # PDAC Clinical Insights
        st.markdown('<div class="medical-card fade-in">', unsafe_allow_html=True)
        st.markdown("### 🩺 PDAC Clinical Implementation Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 🎯 **Therapeutic Optimization Strategies**
            - **AND gates:** Minimize off-target cytotoxicity
            - **OR gates:** Maximize tumor cell coverage
            - **NOT gates:** Implement safety circuit protection
            - **XOR gates:** Enable precise dual-target activation
            - **XNOR gates:** Advanced multi-conditional logic
            """)
        
        with col2:
            st.markdown("""
            #### 🩺 **Clinical Monitoring Protocol**
            - Real-time pancreatic enzyme monitoring
            - Cytokine release syndrome assessment
            - Systematic dose escalation protocols
            - Regular MRI/CT imaging surveillance
            - Biomarker-guided therapy adjustments
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)

def cart_diagram_page():
    """Enhanced CAR-T diagram page with medical UI."""
    st.markdown('<div class="medical-card slide-up">', unsafe_allow_html=True)
    st.markdown("### 🧬 Precision CAR-T Structure Designer")
    st.markdown("Generate publication-ready, personalized CAR-T diagrams optimized for your therapeutic strategy")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not st.session_state.selected_tumor_antigens:
        st.markdown("""
        <div class="medical-alert warning">
            <h4 style="margin: 0 0 1rem 0;">⚠️ Insufficient Target Data</h4>
            <p style="margin: 0;">Navigate to <strong>Antigen Selection</strong> to select tumor antigens for CAR-T design.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if len(st.session_state.selected_tumor_antigens) < 2:
        st.markdown("""
        <div class="medical-alert warning">
            <h4 style="margin: 0 0 1rem 0;">⚠️ Dual-Logic Requirements</h4>
            <p style="margin: 0;">Select at least <strong>2 tumor antigens</strong> to enable dual-logic CAR-T diagram generation.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Enhanced layout
    col_left, col_right = st.columns([3, 2])
    
    with col_right:
        st.markdown('<div class="medical-card fade-in">', unsafe_allow_html=True)
        st.markdown("### 🎯 Therapeutic Target Strategy")
        
        # Enhanced antigen display
        st.markdown("#### 🔴 Primary Elimination Targets")
        for i, antigen in enumerate(st.session_state.selected_tumor_antigens):
            st.markdown(f"""
            <div class="antigen-card tumor">
                <strong>Target {i+1}:</strong> {antigen}<br>
                <span style="color: var(--danger-color); font-weight: 600;">🎯 ELIMINATE</span>
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.selected_healthy_antigens:
            st.markdown("#### 🟢 Tissue Protection Markers")
            for i, antigen in enumerate(st.session_state.selected_healthy_antigens):
                st.markdown(f"""
                <div class="antigen-card healthy">
                    <strong>Safety {i+1}:</strong> {antigen}<br>
                    <span style="color: var(--success-color); font-weight: 600;">🛡️ PROTECT</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Configuration panel
        st.markdown('<div class="medical-card slide-up">', unsafe_allow_html=True)
        st.markdown("### ⚙️ CAR-T Design Configuration")
        
        st.markdown("""
        <div style="background: var(--glass-bg); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color);">
            <strong>Costimulatory Domain:</strong> 4-1BB (PDAC Optimized)<br>
            <strong>Design Standard:</strong> Clinical Publication Grade<br>
            <strong>Target Disease:</strong> Pancreatic Ductal Adenocarcinoma<br>
            <strong>Safety Profile:</strong> Dual-Logic Protection System
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced generate button
        if st.button("🚀 Generate CAR-T Design", type="primary", use_container_width=True):
            with st.spinner("🧬 Creating precision CAR-T architecture..."):
                selected_antigens = {
                    'tumor': st.session_state.selected_tumor_antigens,
                    'healthy': st.session_state.selected_healthy_antigens
                }
                
                diagram_gen = CARTDiagramGenerator(selected_antigens)
                svg_content = diagram_gen.generate_cart_diagram(
                    costimulatory_domain="4-1BB",
                    style="Standard"
                )
                
                st.session_state.cart_diagram = svg_content
                st.session_state.cart_config = {
                    'costimulatory': "4-1BB",
                    'style': "Standard"
                }
                
                st.markdown("""
                <div class="medical-alert success">
                    <strong>✅ CAR-T Design Generated Successfully</strong><br>
                    Your personalized therapeutic diagram is ready for clinical review.
                </div>
                """, unsafe_allow_html=True)
        
        # Design summary
        if 'cart_diagram' in st.session_state:
            st.markdown("### 📋 Design Specifications")
            
            st.markdown(f"""
            <div style="background: var(--glass-bg); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color); margin: 1rem 0;">
                <strong>🎯 Therapeutic Strategy:</strong> Dual-Logic CAR-T<br>
                <strong>🔴 Primary Targets:</strong> {', '.join(st.session_state.selected_tumor_antigens[:2])}<br>
                <strong>⚙️ Costimulatory:</strong> 4-1BB (Enhanced Persistence)<br>
                <strong>🛡️ Safety Profile:</strong> Healthy Tissue Sparing<br>
                <strong>🩺 Clinical Application:</strong> PDAC Immunotherapy
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="medical-alert">
                <strong>🩺 Clinical Advantage:</strong> This dual-logic design maximizes pancreatic tumor elimination while preserving critical organ functions through selective targeting mechanisms.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_left:
        st.markdown('<div class="medical-card fade-in">', unsafe_allow_html=True)
        
        if 'cart_diagram' in st.session_state:
            st.markdown("### 🧬 Your Precision CAR-T Architecture")
            
            # Enhanced diagram display with better sizing
            components.html(st.session_state.cart_diagram, height=520, scrolling=False)
            
            # Enhanced download options (removed report download)
            st.markdown("### 💾 Export Options")
            
            st.download_button(
                label="📥 Download SVG Vector",
                data=st.session_state.cart_diagram,
                file_name=f"immunogate_cart_design_{'-'.join(st.session_state.selected_tumor_antigens[:2])}.svg",
                mime="image/svg+xml",
                use_container_width=True
            )
            
        else:
            st.markdown("### 🎨 CAR-T Design Laboratory")
            
            st.markdown("""
            <div style="text-align: center; padding: 4rem; background: var(--glass-bg); border-radius: 20px; border: 2px dashed var(--border-color);">
                <div style="font-size: 5rem; margin-bottom: 1.5rem; color: var(--accent-color);">🧬</div>
                <h3 style="color: var(--accent-color); margin-bottom: 1.5rem; font-size: 2rem;">Ready for CAR-T Design</h3>
                <p style="font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 2rem; line-height: 1.6;">
                    Configure your therapeutic parameters and generate your personalized 
                    CAR-T structure diagram optimized for PDAC treatment.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Component overview
            st.markdown("""
            ### 🧬 CAR-T Component Architecture
            
            Your personalized clinical diagram will include:
            
            **🔍 scFv Recognition Domains**  
            Target-specific antibody fragments engineered for your selected tumor antigens
            
            **🔗 Flexible Hinge Region**  
            Optimized spacer region ensuring proper antigen binding geometry and accessibility
            
            **📡 Transmembrane Anchor**  
            Stable membrane integration ensuring persistent CAR expression on T-cells
            
            **💪 4-1BB Costimulatory Domain**  
            Enhanced T-cell activation, proliferation, and long-term persistence signals
            
            **⚡ CD3ζ Primary Signaling**  
            Core activation domain triggering immediate cytotoxic response pathways
            
            ---
            
            **🎯 Elimination Mechanism:** Tumor antigen recognition triggers immediate CAR-T activation  
            **🛡️ Safety Mechanism:** Healthy cell antigens provide protective override signals  
            **🩺 Clinical Outcome:** Selective PDAC elimination with preserved pancreatic function
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
