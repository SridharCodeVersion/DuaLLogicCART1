import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

class DataProcessor:
    """Handles biomarker dataset processing and validation."""
    
    def __init__(self, csv_file_path: str = ''):
        if csv_file_path and csv_file_path.strip():
            self.df = pd.read_csv(csv_file_path)
            # Clean up the first column name which might have BOM characters
            self.df.columns = [col.strip().replace('\ufeff', '') for col in self.df.columns]
            # Rename columns to match expected format
            if 'Serum Protein Biomarker' in self.df.columns:
                self.df.rename(columns={'Serum Protein Biomarker': 'biomarker_name'}, inplace=True)
            if 'Category' in self.df.columns:
                self.df.rename(columns={'Category': 'category'}, inplace=True)
            if 'Indication' in self.df.columns:
                self.df.rename(columns={'Indication': 'indication'}, inplace=True)
        else:
            self.df = pd.DataFrame()
        
        self.required_columns = ['biomarker_name', 'category', 'indication']
    
    def validate_dataset(self) -> Dict[str, Any]:
        """
        Validate the uploaded biomarker dataset.
        
        Returns:
            Dict containing validation status and error message if any
        """
        try:
            # Check if required columns exist
            missing_columns = [col for col in self.required_columns if col not in self.df.columns]
            if missing_columns:
                return {
                    'valid': False,
                    'error': f"Missing required columns: {', '.join(missing_columns)}"
                }
            
            # Check for empty values
            if self.df[self.required_columns].isnull().any().any():
                return {
                    'valid': False,
                    'error': "Dataset contains empty values in required columns"
                }
            
            # Validate indication format
            valid_indications = self.df['indication'].str.contains('↑|↓', na=False).all()
            if not valid_indications:
                return {
                    'valid': False,
                    'error': "Indication column should contain ↑ (oncogenic) or ↓ (suppressor) symbols"
                }
            
            # Check for duplicate biomarker names
            if self.df['biomarker_name'].duplicated().any():
                return {
                    'valid': False,
                    'error': "Dataset contains duplicate biomarker names"
                }
            
            return {'valid': True, 'error': None}
            
        except Exception as e:
            return {'valid': False, 'error': f"Validation error: {str(e)}"}
    
    def get_biomarker_info(self, biomarker_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific biomarker.
        
        Args:
            biomarker_name: Name of the biomarker
            
        Returns:
            Dictionary containing biomarker information
        """
        try:
            biomarker_row = self.df[self.df['biomarker_name'] == biomarker_name].iloc[0]
            return {
                'name': biomarker_row['biomarker_name'],
                'category': biomarker_row['category'],
                'indication': biomarker_row['indication'],
                'is_oncogenic': '↑' in biomarker_row['indication'],
                'is_suppressor': '↓' in biomarker_row['indication']
            }
        except (IndexError, KeyError):
            return {'name': '', 'category': '', 'indication': '—', 'is_oncogenic': False, 'is_suppressor': False}
    
    def generate_expression_data(self, biomarker_names: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Generate simulated expression data for selected biomarkers.
        This simulates fold-change values based on biomarker indications.
        
        Args:
            biomarker_names: List of biomarker names
            
        Returns:
            Dictionary with expression data for tumor and healthy cells
        """
        expression_data = {}
        
        for biomarker in biomarker_names:
            biomarker_info = self.get_biomarker_info(biomarker)
            if biomarker_info is None:
                continue
            
            # Simulate expression levels based on indication
            if biomarker_info['is_oncogenic']:
                # Oncogenic markers: higher in tumor, lower in healthy
                tumor_expr = np.random.uniform(5.0, 15.0)  # High expression
                healthy_expr = np.random.uniform(0.5, 3.0)  # Low expression
            else:  # suppressor
                # Suppressor markers: lower in tumor, higher in healthy
                tumor_expr = np.random.uniform(0.5, 3.0)   # Low expression
                healthy_expr = np.random.uniform(5.0, 15.0)  # High expression
            
            expression_data[biomarker] = {
                'tumor_expression': tumor_expr,
                'healthy_expression': healthy_expr,
                'fold_change': tumor_expr / healthy_expr if healthy_expr > 0 else float('inf')
            }
        
        return expression_data
    
    def calculate_expression_threshold(self, expression_data: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate expression thresholds for binary classification.
        
        Args:
            expression_data: Expression data dictionary
            
        Returns:
            Dictionary with thresholds for each biomarker
        """
        thresholds = {}
        
        for biomarker, data in expression_data.items():
            # Use geometric mean as threshold
            tumor_expr = data['tumor_expression']
            healthy_expr = data['healthy_expression']
            threshold = np.sqrt(tumor_expr * healthy_expr)
            thresholds[biomarker] = threshold
        
        return thresholds
    
    def get_dataset_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics about the dataset.
        
        Returns:
            Dictionary containing dataset statistics
        """
        stats = {
            'total_biomarkers': len(self.df),
            'categories': self.df['category'].unique().tolist(),
            'category_counts': self.df['category'].value_counts().to_dict(),
            'oncogenic_count': len(self.df[self.df['indication'].str.contains('↑', na=False)]),
            'suppressor_count': len(self.df[self.df['indication'].str.contains('↓', na=False)])
        }
        
        return stats
    
    def get_categories_with_biomarkers(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get biomarkers grouped by category for tabular display.
        
        Returns:
            Dictionary with categories as keys and lists of biomarkers as values
        """
        # Filter out header rows and invalid entries
        valid_df = self.df[
            (self.df['biomarker_name'].notna()) & 
            (self.df['category'].notna()) & 
            (self.df['indication'].notna()) &
            (~self.df['biomarker_name'].str.contains('Biomarker', na=False)) &
            (self.df['indication'] != 'Indication') &
            (self.df['indication'] != '—')  # Exclude non-biomarkers
        ].copy()
        
        # Clean up indication symbols
        valid_df = valid_df.copy()
        valid_df['indication_clean'] = valid_df['indication'].apply(self._clean_indication)
        
        categories = {}
        
        for category in valid_df['category'].dropna().unique():
            if pd.isna(category):
                continue
                
            category_df = valid_df[valid_df['category'] == category]
            biomarkers = category_df.to_dict('records')
            categories[category] = biomarkers
            
        return categories
    
    def _clean_indication(self, indication: str) -> str:
        """
        Clean indication symbols to standardize format.
        """
        if pd.isna(indication):
            return '—'
        
        indication = str(indication).strip()
        
        # Standardize symbols
        if '↑' in indication:
            if '↓' in indication:
                return '↑/↓'  # Both up and down
            return '↑'  # Oncogenic/upregulated
        elif '↓' in indication:
            return '↓'  # Tumor suppressor/downregulated
        else:
            return '—'  # Not validated or neutral
    
    def get_oncogenic_biomarkers(self) -> List[str]:
        """
        Get list of oncogenic biomarkers (↑ indication).
        """
        valid_df = self._get_valid_biomarkers()
        oncogenic = valid_df[
            valid_df['indication'].str.contains('↑', na=False)
        ]['biomarker_name'].tolist()
        return oncogenic
    
    def get_tumor_suppressor_biomarkers(self) -> List[str]:
        """
        Get list of tumor suppressor biomarkers (↓ indication).
        """
        valid_df = self._get_valid_biomarkers()
        suppressors = valid_df[
            valid_df['indication'].str.contains('↓', na=False) &
            (~valid_df['indication'].str.contains('↑', na=False))  # Exclude mixed ones
        ]['biomarker_name'].tolist()
        return suppressors
    
    def _get_valid_biomarkers(self) -> pd.DataFrame:
        """
        Get filtered dataframe with only valid biomarkers.
        """
        filtered_df = self.df[
            (self.df['biomarker_name'].notna()) & 
            (self.df['category'].notna()) & 
            (self.df['indication'].notna()) &
            (~self.df['biomarker_name'].str.contains('Biomarker', na=False)) &
            (self.df['indication'] != 'Indication') &
            (self.df['indication'] != '—')
        ].copy()
        return filtered_df
