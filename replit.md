# Overview

This is a production-ready web application for designing dual-logic CAR-T (Chimeric Antigen Receptor T-cell) strategies specifically for Pancreatic Ductal Adenocarcinoma (PDAC). The tool enables clinicians to upload biomarker datasets, select tumor and healthy cell antigens, analyze different logic gate strategies, and generate personalized CAR-T structure diagrams. The application provides selectivity scoring to rank different logic gates and recommends optimal strategies based on tumor kill versus healthy cell kill ratios.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web framework for rapid deployment and interactive UI components
- **Layout**: Wide layout with expandable sidebar for navigation and controls
- **Session Management**: Streamlit session state for maintaining user data across interactions
- **Theming**: Custom CSS implementation with light/dark theme toggle
- **Visualization**: Plotly for interactive charts and heatmaps, SVG generation for CAR-T diagrams

## Backend Architecture
- **Modular Design**: Component-based architecture with separate modules for distinct functionalities:
  - `data_processor.py`: Handles CSV upload, validation, and biomarker data processing
  - `logic_gates.py`: Implements truth table generation and logic gate analysis
  - `cart_diagram.py`: Generates personalized CAR-T structure diagrams
  - `visualizations.py`: Creates interactive visualizations and heatmaps
- **Data Processing Pipeline**: Validates required columns (biomarker_name, category, indication), cleans data, and generates expression simulations
- **Logic Gate Engine**: Supports AND, OR, NOT, XOR, XNOR gates with both hard and probabilistic calculations
- **Selectivity Scoring**: Implements tumor kill/healthy kill ratio calculations for ranking strategies

## Data Storage Solutions
- **File-based Storage**: CSV input processing with pandas DataFrames for in-memory operations
- **Session State**: Streamlit's built-in session state for temporary data persistence
- **Default Dataset**: Includes `pancreatic_biomarkers.csv` as reference dataset

## Diagram Generation System
- **SVG-based Rendering**: Custom SVG generation for CAR-T structure diagrams
- **Dynamic Labeling**: Personalizes diagrams with selected antigen names
- **Component Mapping**: Maps selected antigens to scFv domains with proper labeling
- **Export Functionality**: Supports PNG/SVG download for clinical documentation

## Analysis Engine
- **Truth Table Generation**: Creates comprehensive truth tables for all logic gate combinations
- **Expression Simulation**: Generates probabilistic expression data for tumor vs healthy cells
- **Threshold Calculation**: Implements dynamic threshold determination for binary classifications
- **Selectivity Ranking**: Automated ranking system based on therapeutic index calculations

# External Dependencies

## Core Libraries
- **streamlit**: Web application framework and UI components
- **pandas**: Data manipulation and CSV processing
- **numpy**: Numerical computations and array operations
- **scipy**: Statistical calculations and probability distributions

## Visualization Libraries
- **plotly**: Interactive charts, heatmaps, and graph objects
- **matplotlib**: Static plotting and image generation
- **PIL (Pillow)**: Image processing and format conversion

## Export and Documentation
- **fpdf2**: PDF generation for downloadable reports
- **base64**: Encoding for file downloads and data URI generation
- **io.BytesIO**: In-memory file handling for exports

## Standard Libraries
- **json**: Data serialization for configuration and results
- **itertools**: Combinatorial operations for truth table generation
- **typing**: Type hints for better code documentation and IDE support

Note: The application is designed to be self-contained with no external API dependencies, ensuring it can run in isolated clinical environments while maintaining data privacy and security.