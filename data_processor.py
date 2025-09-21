import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

class DataProcessor:
    """Handles biomarker dataset processing and validation."""
    
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()
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
            if self.df[self.required_columns].isnull().values.any():
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
            return {}
    
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
