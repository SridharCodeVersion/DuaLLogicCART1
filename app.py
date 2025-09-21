
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
if 'dark_theme' not in st.session_state:
    st.session_state.dark_theme = False

def apply_modern_styling():
    """Apply modern, professional CSS styling with animations and responsive design."""
    # Get current theme from session state
    is_dark_theme = st.session_state.get('dark_theme', False)
    
    st.markdown(f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {{
        --primary-color: #0073e6;
        --primary-hover: #005bb5;
        --secondary-color: #00a86b;
        --success-color: #10b981;
        --danger-color: #ef4444;
        --warning-color: #f59e0b;
        --info-color: #3b82f6;
        --medical-blue: #0073e6;
        --medical-green: #00a86b;
        --medical-teal: #20b2aa;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }}
    
    /* Theme-specific variables */
    {''.join([
        f"""
        /* Dark theme variables */
        :root {{
            --bg-primary: #0a0e1a;
            --bg-secondary: #1a2332;
            --bg-card: rgba(26, 35, 50, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #b0c4de;
            --border-color: #2d3748;
            --gradient-primary: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #1d4ed8 100%);
            --gradient-secondary: linear-gradient(135deg, #0d9488 0%, #0f766e 50%, #115e59 100%);
            --medical-bg: linear-gradient(135deg, #0a0e1a 0%, #1a2332 25%, #2d3748 75%, #1a2332 100%);
        }}
        """ if is_dark_theme else f"""
        /* Light theme variables */
        :root {{
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --bg-card: rgba(255, 255, 255, 0.9);
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --gradient-primary: linear-gradient(135deg, #0073e6 0%, #005bb5 50%, #004494 100%);
            --gradient-secondary: linear-gradient(135deg, #00a86b 0%, #008f5a 50%, #007849 100%);
            --medical-bg: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 25%, #bae6fd 75%, #e0f2fe 100%);
        }}
        """
    ])}
    
    /* Global styling */
    .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--medical-bg);
        min-height: 100vh;
        position: relative;
    }}
    
    /* Medical background pattern overlay */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(0, 115, 230, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(0, 168, 107, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(32, 178, 170, 0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Show sidebar toggle button */
    .stSidebar > div:first-child {{
        background: var(--bg-card);
        border-right: 2px solid var(--border-color);
    }}
    
    /* Make sidebar toggle visible */
    button[data-testid="collapsedControl"] {{
        background: var(--bg-card) !important;
        border: 2px solid var(--medical-blue) !important;
        border-radius: 50% !important;
        box-shadow: var(--shadow-lg) !important;
        color: var(--medical-blue) !important;
        font-size: 1.2rem !important;
        width: 40px !important;
        height: 40px !important;
        margin: 1rem !important;
        transition: all 0.3s ease !important;
    }}
    
    button[data-testid="collapsedControl"]:hover {{
        background: var(--medical-blue) !important;
        color: white !important;
        transform: scale(1.1) !important;
    }}
    
    /* Theme toggle button */
    .theme-toggle {{
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 9999;
        background: var(--bg-card);
        border: 2px solid var(--medical-blue);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-lg);
        font-size: 1.5rem;
    }}
    
    .theme-toggle:hover {{
        background: var(--medical-blue);
        color: white;
        transform: scale(1.1);
    }}
    
    /* Custom header */
    .main-header {{
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0 2rem 0;
        box-shadow: var(--shadow-lg);
        border: 2px solid var(--border-color);
        animation: slideInDown 0.6s ease-out;
        color: var(--text-primary);
    }}
    
    .main-title {{
        font-size: 2.5rem;
        font-weight: 700;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }}
    
    .main-subtitle {{
        font-size: 1.1rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 1rem;
        animation: fadeInUp 0.8s ease-out 0.4s both;
    }}
    
    /* Medical-themed cards */
    .glass-card {{
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-lg);
        border: 2px solid var(--border-color);
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
        color: var(--text-primary);
    }}
    
    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px var(--medical-blue) / 0.2;
        border-color: var(--medical-blue);
    }}
    
    /* Enhanced sidebar */
    .css-1d391kg {{
        background: var(--bg-card) !important;
        backdrop-filter: blur(20px);
        border-radius: 0 20px 20px 0;
        box-shadow: var(--shadow-lg);
        border-right: 2px solid var(--border-color);
    }}
    
    /* Sidebar content */
    .stSidebar .stMarkdown {{
        color: var(--text-primary);
    }}
    
    /* Navigation styling */
    .stRadio > div {{
        background: var(--bg-card);
        border-radius: 15px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid var(--border-color);
    }}
    
    .stRadio > div > label {{
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin: 0.25rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
        font-weight: 500;
        color: var(--text-primary) !important;
    }}
    
    .stRadio > div > label:hover {{
        background: var(--medical-blue) !important;
        color: white !important;
        transform: translateX(5px);
    }}
    
    .stRadio > div > label[aria-checked="true"] {{
        background: var(--gradient-primary) !important;
        color: white !important;
    }}
    
    /* Enhanced buttons */
    .stButton > button {
        background: var(--gradient-primary);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        background: var(--gradient-secondary);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Primary button variant */
    .primary-button {
        background: var(--gradient-primary) !important;
        border: 2px solid transparent !important;
        background-clip: padding-box !important;
    }
    
    .success-button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    }
    
    .danger-button {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    }
    
    /* Enhanced metrics */
    .metric-card {{
        background: var(--bg-card);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
        border: 2px solid var(--border-color);
        color: var(--text-primary);
    }}
    
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
        border-color: var(--medical-blue);
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: var(--medical-blue);
        margin-bottom: 0.5rem;
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Enhanced selectboxes and inputs */
    .stSelectbox > div > div, .stMultiSelect > div > div {{
        background: var(--bg-card) !important;
        border-radius: 12px;
        border: 2px solid var(--border-color) !important;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        color: var(--text-primary) !important;
    }}
    
    .stSelectbox > div > div:focus-within, .stMultiSelect > div > div:focus-within {{
        border-color: var(--medical-blue) !important;
        box-shadow: 0 0 0 3px var(--medical-blue) / 0.1 !important;
    }}
    
    /* Enhanced dataframes */
    .stDataFrame {{
        background: var(--bg-card);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: var(--shadow-md);
        backdrop-filter: blur(10px);
        border: 2px solid var(--border-color);
    }}
    
    /* Text color fixes */
    .stMarkdown, .stText {{
        color: var(--text-primary) !important;
    }}
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
        color: var(--text-primary) !important;
    }}
    
    /* Info/warning/error boxes */
    .stInfo, .stWarning, .stError, .stSuccess {{
        background: var(--bg-card) !important;
        border: 2px solid var(--border-color) !important;
        color: var(--text-primary) !important;
    }}
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    /* Loading animations */
    .loading-pulse {
        animation: pulse 2s infinite;
    }
    
    /* Success/Error states */
    .success-alert {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 1rem;
        color: #065f46;
        animation: slideInLeft 0.5s ease-out;
    }
    
    .error-alert {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #ef4444;
        border-radius: 12px;
        padding: 1rem;
        color: #991b1b;
        animation: slideInLeft 0.5s ease-out;
    }
    
    .warning-alert {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem;
        color: #92400e;
        animation: slideInLeft 0.5s ease-out;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
        
        .glass-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
    }
    
    @media (max-width: 480px) {
        .main-title {
            font-size: 1.5rem;
        }
        
        .main-subtitle {
            font-size: 1rem;
        }
        
        .glass-card {
            padding: 0.75rem;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gradient-primary);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-hover);
    }
    
    /* Plotly chart enhancements */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: var(--shadow-md);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 0.5rem;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-primary);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def reset_all_selections():
    """Reset all user selections and analysis results."""
    st.session_state.selected_tumor_antigens = []
    st.session_state.selected_healthy_antigens = []
    st.session_state.analysis_results = None
    st.rerun()

def create_modern_header():
    """Create modern header with glassmorphism design."""
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🧬 ImmunoGate</h1>
        <p class="main-subtitle">Dual Logic CAR-T Cell Therapy for PDAC</p>
        <div style="text-align: center; margin-top: 1rem;">
            <span style="background: rgba(239, 68, 68, 0.1); color: #dc2626; padding: 0.5rem 1rem; border-radius: 25px; font-weight: 600; font-size: 0.9rem;">
                ⚠️ RESEARCH USE ONLY - Not for clinical diagnosis
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, icon="📊"):
    """Create animated metric card."""
    return f"""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
    </div>
    """

def main():
    apply_modern_styling()
    
    # Theme toggle button (fixed position)
    theme_icon = "🌙" if not st.session_state.dark_theme else "☀️"
    theme_text = "Dark Mode" if not st.session_state.dark_theme else "Light Mode"
    
    st.markdown(f"""
    <div class="theme-toggle" onclick="toggleTheme()" title="Toggle {theme_text}">
        {theme_icon}
    </div>
    
    <script>
    function toggleTheme() {{
        // This will be handled by Streamlit rerun
        window.parent.postMessage({{type: 'theme-toggle'}}, '*');
    }}
    </script>
    """, unsafe_allow_html=True)
    
    # Theme toggle handling
    col_theme1, col_theme2, col_theme3 = st.columns([1, 1, 1])
    with col_theme3:
        if st.button(f"{theme_icon} {theme_text}", key="theme_toggle", help=f"Switch to {theme_text}"):
            st.session_state.dark_theme = not st.session_state.dark_theme
            st.rerun()
    
    # Modern header
    create_modern_header()
    
    # Top controls with modern styling
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("🔄", key="refresh_all", help="Reset All Selections"):
            reset_all_selections()
    
    # Modern sidebar navigation
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0; border-bottom: 2px solid rgba(255,255,255,0.1); margin-bottom: 1rem;">
        <h3 style="color: #6366f1; font-weight: 700; margin: 0;">Navigation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Navigation Menu",
        ["🎯 Antigen Selection", "🔬 Logic Gate Analysis", "🧬 CAR-T Diagram"],
        key="navigation",
        label_visibility="collapsed"
    )
    
    # Auto-refresh logic gate analysis and CAR-T diagram when antigens change
    if page in ["🔬 Logic Gate Analysis", "🧬 CAR-T Diagram"]:
        # Auto-generate analysis if antigens are selected
        if (st.session_state.selected_tumor_antigens or st.session_state.selected_healthy_antigens) and not st.session_state.analysis_results:
            with st.spinner("Auto-generating analysis..."):
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
    """Enhanced antigen selection page with modern UI."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Intelligent Antigen Selection")
    st.markdown("Select biomarkers from our comprehensive pancreatic cancer dataset with real-time validation")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced dataset overview with animated metrics
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Dataset Intelligence")
    
    total_biomarkers = sum(len(biomarkers) for biomarkers in st.session_state.biomarkers_data.values())
    oncogenic_count = len(st.session_state.data_processor.get_oncogenic_biomarkers())
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card("Total Biomarkers", total_biomarkers, "🧬"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Categories", len(st.session_state.biomarkers_data), "📂"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Oncogenic Markers", oncogenic_count, "🎯"), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced category selection
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🗂️ Smart Category Explorer")
    
    selected_category = st.selectbox(
        "Select Category to Explore:",
        list(st.session_state.biomarkers_data.keys()),
        key="category_selector",
        help="Choose a biomarker category to view and select antigens"
    )
    
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
            st.markdown("#### 🔴 Tumor Antigens (Oncogenic ↑)")
            tumor_options = [b['biomarker_name'] for b in processed_biomarkers 
                           if b['indication_clean'] in ['↑', '↑/↓']]
            selected_tumor = st.multiselect(
                "Select targets for CAR-T activation:",
                tumor_options,
                default=[x for x in st.session_state.selected_tumor_antigens if x in tumor_options],
                key=f"tumor_{selected_category}",
                help="These antigens will trigger CAR-T cell activation"
            )
        
        with col2:
            st.markdown("#### 🟢 Healthy Cell Antigens (Suppressors ↓)")
            healthy_options = [b['biomarker_name'] for b in processed_biomarkers 
                             if b['indication_clean'] in ['↓', '↑/↓']]
            selected_healthy = st.multiselect(
                "Select targets for protection:",
                healthy_options,
                default=[x for x in st.session_state.selected_healthy_antigens if x in healthy_options],
                key=f"healthy_{selected_category}",
                help="These antigens will prevent CAR-T activation"
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
            st.markdown("#### 📋 Biomarker Details")
            st.dataframe(display_df, width='stretch')
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced selection summary
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Current Selection Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 Selected Tumor Antigens")
        if st.session_state.selected_tumor_antigens:
            for i, antigen in enumerate(st.session_state.selected_tumor_antigens):
                st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px;">
                    <strong>{i+1}. {antigen}</strong> → 🎯 <span style="color: #ef4444;">KILL TARGET</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No tumor antigens selected yet")
    
    with col2:
        st.markdown("#### 🟢 Selected Healthy Cell Antigens")
        if st.session_state.selected_healthy_antigens:
            for i, antigen in enumerate(st.session_state.selected_healthy_antigens):
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px;">
                    <strong>{i+1}. {antigen}</strong> → 🛡️ <span style="color: #10b981;">PROTECT</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No healthy cell antigens selected yet")
    
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
            st.success(f"✅ {total_selected} antigens selected - Ready for analysis!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def logic_gate_analysis_page():
    """Enhanced logic gate analysis page."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔬 Advanced Logic Gate Analysis")
    st.markdown("AI-powered analysis of optimal logic gates for dual-target CAR-T therapy")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not st.session_state.selected_tumor_antigens and not st.session_state.selected_healthy_antigens:
        st.markdown("""
        <div class="warning-alert">
            <h4 style="margin: 0 0 1rem 0;">⚠️ No Antigens Selected</h4>
            <p style="margin: 0;">Please select antigens first in the <strong>Antigen Selection</strong> page to begin analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display selected antigens with modern styling
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Analysis Input Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 Tumor Antigens")
        if st.session_state.selected_tumor_antigens:
            for antigen in st.session_state.selected_tumor_antigens:
                st.markdown(f"• **{antigen}** → 🎯 Kill Signal")
        else:
            st.write("None selected")
    
    with col2:
        st.markdown("#### 🟢 Healthy Cell Antigens (HCA)")
        if st.session_state.selected_healthy_antigens:
            for antigen in st.session_state.selected_healthy_antigens:
                st.markdown(f"• **{antigen}** → 🛡️ Protection Signal")
        else:
            st.write("None selected")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis generation
    if not st.session_state.analysis_results:
        if st.button("🚀 Generate Advanced Analysis", type="primary", use_container_width=True):
            with st.spinner("🧠 AI analyzing optimal logic gates..."):
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
                    <div class="success-alert">
                        <h4 style="margin: 0 0 1rem 0;">✅ Analysis Complete!</h4>
                        <p style="margin: 0;">Advanced logic gate analysis has been successfully generated with AI recommendations.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                    
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-alert">
                        <h4 style="margin: 0 0 1rem 0;">❌ Analysis Error</h4>
                        <p style="margin: 0;">Error during analysis: {str(e)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    return
    
    # Display results with enhanced styling
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # AI Recommendation section
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🏆 AI-Powered Gate Recommendation")
        
        best_gate = results['best_gate']
        
        # Create recommendation card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 2rem; border-radius: 20px; text-align: center; margin: 1rem 0;">
            <h2 style="margin: 0 0 1rem 0; font-size: 2.5rem;">🏆 {best_gate['gate']} GATE</h2>
            <div style="font-size: 1.2rem; margin-bottom: 1rem;">
                <strong>Selectivity Score: {best_gate['score']:.3f}</strong>
            </div>
            <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">{best_gate['explanation']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Safety note
        if 'safety_note' in best_gate:
            st.info(f"🛡️ **Safety Recommendation:** {best_gate['safety_note']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Truth Tables section
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Interactive Truth Tables")
        st.markdown("**Legend:** 1 = Present, 0 = Absent | **🎯** = Kill, **❌** = Off")
        
        visualizer = TruthTableVisualizer()
        
        # Enhanced tabs
        tab_names = list(results['truth_tables'].keys())
        tabs = st.tabs([f"🔘 {gate} Gate" for gate in tab_names])
        
        for i, (gate_name, truth_table) in enumerate(results['truth_tables'].items()):
            with tabs[i]:
                if gate_name == 'NOT':
                    fixed_not_fig = visualizer.create_fixed_not_truth_table()
                    st.plotly_chart(fixed_not_fig, use_container_width=True)
                else:
                    simplified_fig = visualizer.create_simplified_truth_table(truth_table, gate_name)
                    st.plotly_chart(simplified_fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Performance Analytics
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📈 Performance Analytics")
        selectivity_fig = visualizer.create_selectivity_comparison(results['selectivity_scores'])
        st.plotly_chart(selectivity_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # PDAC Clinical Insights
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🩺 PDAC Clinical Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 🎯 **Therapy Optimization**
            - **AND gates** minimize off-target effects
            - **OR gates** increase tumor coverage
            - **NOT gates** provide safety switches
            - **XOR gates** enable precise targeting
            """)
        
        with col2:
            st.markdown("""
            #### 🩺 **Clinical Monitoring**
            - Monitor pancreatic enzyme levels
            - Track cytokine release syndrome
            - Implement dose escalation protocols
            - Regular imaging assessments
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)

def cart_diagram_page():
    """Enhanced CAR-T diagram page with modern UI."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🧬 Personalized CAR-T Structure Designer")
    st.markdown("Generate publication-ready CAR-T diagrams tailored to your selected antigens")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not st.session_state.selected_tumor_antigens:
        st.markdown("""
        <div class="warning-alert">
            <h4 style="margin: 0 0 1rem 0;">⚠️ Insufficient Data</h4>
            <p style="margin: 0;">Please select tumor antigens first in the <strong>Antigen Selection</strong> page.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if len(st.session_state.selected_tumor_antigens) < 2:
        st.markdown("""
        <div class="warning-alert">
            <h4 style="margin: 0 0 1rem 0;">⚠️ Minimum Requirements</h4>
            <p style="margin: 0;">Please select at least <strong>2 tumor antigens</strong> for dual-logic CAR-T diagram generation.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Enhanced layout
    col_left, col_right = st.columns([3, 2])
    
    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Target Strategy Overview")
        
        # Enhanced antigen display
        st.markdown("#### 🔴 Primary Kill Targets")
        for i, antigen in enumerate(st.session_state.selected_tumor_antigens):
            st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; padding: 0.75rem; margin: 0.5rem 0; border-radius: 10px;">
                <strong>Target {i+1}:</strong> {antigen} → <span style="color: #ef4444;">🎯 ELIMINATE</span>
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.selected_healthy_antigens:
            st.markdown("#### 🟢 Protection Targets")
            for i, antigen in enumerate(st.session_state.selected_healthy_antigens):
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; padding: 0.75rem; margin: 0.5rem 0; border-radius: 10px;">
                    <strong>Guard {i+1}:</strong> {antigen} → <span style="color: #10b981;">🛡️ PROTECT</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Configuration panel
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ CAR-T Configuration")
        
        st.markdown("**Costimulatory Domain:** 4-1BB (Optimized for PDAC)")
        st.markdown("**Design Style:** Professional Publication Ready")
        
        # Enhanced generate button
        if st.button("🚀 Generate CAR-T Design", type="primary", use_container_width=True):
            with st.spinner("🧬 Creating personalized CAR-T structure..."):
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
                
                st.success("✅ CAR-T design generated successfully!")
        
        # Design summary
        if 'cart_diagram' in st.session_state:
            st.markdown("### 📋 Design Specifications")
            
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                <strong>🎯 Strategy:</strong> Dual-Logic CAR-T<br>
                <strong>🔴 Primary Targets:</strong> {', '.join(st.session_state.selected_tumor_antigens[:2])}<br>
                <strong>⚙️ Costimulatory:</strong> 4-1BB (PDAC Optimized)<br>
                <strong>🛡️ Safety Profile:</strong> Healthy tissue sparing
            </div>
            """, unsafe_allow_html=True)
            
            st.info("👉 **PDAC Advantage:** This dual-logic design maximizes tumor elimination while preserving critical pancreatic functions.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        if 'cart_diagram' in st.session_state:
            st.markdown("### 🧬 Your Personalized CAR-T Structure")
            
            # Enhanced diagram display
            components.html(st.session_state.cart_diagram, height=520, scrolling=False)
            
            # Enhanced download options
            st.markdown("### 💾 Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Download SVG",
                    data=st.session_state.cart_diagram,
                    file_name=f"immunogate_cart_design_{'-'.join(st.session_state.selected_tumor_antigens[:2])}.svg",
                    mime="image/svg+xml",
                    use_container_width=True
                )
            
            with col2:
                # Create summary report
                summary_report = f"""
                ImmunoGate CAR-T Design Report
                =============================
                
                Design ID: {'-'.join(st.session_state.selected_tumor_antigens[:2])}
                Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                Target Antigens:
                {chr(10).join([f"- {antigen} (Kill)" for antigen in st.session_state.selected_tumor_antigens])}
                
                Protection Antigens:
                {chr(10).join([f"- {antigen} (Protect)" for antigen in st.session_state.selected_healthy_antigens]) if st.session_state.selected_healthy_antigens else "None"}
                
                Configuration:
                - Costimulatory Domain: 4-1BB
                - Target Disease: PDAC
                - Safety Profile: Dual-logic protection
                
                Generated by ImmunoGate v1.0
                """
                
                st.download_button(
                    label="📄 Design Report",
                    data=summary_report,
                    file_name=f"immunogate_report_{'-'.join(st.session_state.selected_tumor_antigens[:2])}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        else:
            st.markdown("### 🎨 CAR-T Design Studio")
            
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: rgba(255, 255, 255, 0.05); border-radius: 15px; border: 2px dashed rgba(255, 255, 255, 0.3);">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🧬</div>
                <h3 style="color: #6366f1; margin-bottom: 1rem;">Ready to Create Your CAR-T Design</h3>
                <p style="font-size: 1.1rem; color: #64748b; margin-bottom: 2rem;">
                    Configure your parameters on the right and click <strong>"Generate CAR-T Design"</strong> 
                    to create your personalized diagram.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Component overview
            st.markdown("""
            ### 🧬 CAR-T Component Architecture
            
            Your personalized diagram will include:
            
            - **🔍 scFv Domains**: Target-specific antibody fragments for your selected antigens
            - **🔗 Hinge Region**: Flexible spacer optimizing antigen binding geometry  
            - **📡 Transmembrane**: Membrane anchor ensuring stable CAR expression
            - **💪 4-1BB Costimulatory**: Enhanced T-cell activation and persistence
            - **⚡ CD3ζ Signaling**: Primary activation signal for cytotoxic response
            
            **🎯 Kill Mechanism**: Tumor antigens trigger immediate activation  
            **🛡️ Safety Mechanism**: Healthy cell antigens provide protection override
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
