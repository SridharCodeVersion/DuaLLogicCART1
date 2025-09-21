# CAR-T Design Tool for PDAC

A production-ready, web-based tool for designing dual-logic CAR-T strategies for Pancreatic Ductal Adenocarcinoma (PDAC) using biomarker datasets.

## 🔬 Features

- **Dataset Upload & Validation**: Upload CSV biomarker datasets with automatic validation
- **Interactive Antigen Selection**: Select tumor and healthy cell antigens from dropdown menus
- **Logic Gate Analysis**: Generate truth tables for AND/OR/NOT/XOR/XNOR gates with hard and probabilistic calculations
- **Selectivity Scoring**: Rank gates by selectivity score (tumor kill / healthy kill ratio)
- **CAR-T Diagram Generation**: Create personalized CAR-T structure diagrams with labeled components
- **Downloadable Results**: Export truth tables, analysis results, and diagrams

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required libraries will be installed automatically

### Installation & Running

1. Clone or download this repository
2. Install dependencies:
```bash
pip install streamlit pandas numpy scipy matplotlib plotly pillow fpdf2
