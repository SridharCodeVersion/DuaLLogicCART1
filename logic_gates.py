import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from itertools import product

class LogicGateAnalyzer:
    """Analyzes logic gates for CAR-T dual-antigen strategies."""
    
    def __init__(self, biomarkers_df: pd.DataFrame, selected_antigens: Dict[str, List[str]]):
        self.biomarkers_df = biomarkers_df
        self.selected_antigens = selected_antigens
        self.logic_gates = ['AND', 'OR', 'NOT', 'XOR', 'XNOR']
        
        # Import data processor for expression simulation
        from data_processor import DataProcessor
        self.data_processor = DataProcessor(biomarkers_df)
    
    def generate_truth_table(self, gate_type: str) -> Dict[str, Any]:
        """
        Generate truth table for a specific logic gate.
        
        Args:
            gate_type: Type of logic gate ('AND', 'OR', 'NOT', 'XOR', 'XNOR')
            
        Returns:
            Dictionary containing truth table data
        """
        # Get all antigens
        tumor_antigens = self.selected_antigens['tumor']
        healthy_antigens = self.selected_antigens['healthy']
        all_antigens = tumor_antigens + healthy_antigens
        
        # Generate expression data
        expression_data = self.data_processor.generate_expression_data(all_antigens)
        thresholds = self.data_processor.calculate_expression_threshold(expression_data)
        
        # Create truth table structure
        truth_table = {
            'inputs': [],
            'outputs': [],
            'probabilities': [],
            'cell_types': []
        }
        
        # Generate all possible input combinations (binary)
        n_antigens = len(tumor_antigens)  # We focus on tumor antigens for CAR-T logic
        input_combinations = list(product([0, 1], repeat=n_antigens))
        
        for inputs in input_combinations:
            # Calculate logic gate output
            output = self._calculate_gate_output(gate_type, inputs)
            
            # Calculate probabilistic output based on expression levels
            prob_output = self._calculate_probabilistic_output(
                gate_type, inputs, tumor_antigens, expression_data, thresholds
            )
            
            truth_table['inputs'].append(inputs)
            truth_table['outputs'].append(output)
            truth_table['probabilities'].append(prob_output)
            
            # Determine cell type based on antigen expression pattern
            cell_type = self._determine_cell_type(inputs, tumor_antigens, expression_data)
            truth_table['cell_types'].append(cell_type)
        
        return truth_table
    
    def _calculate_gate_output(self, gate_type: str, inputs: Tuple[int, ...]) -> int:
        """Calculate hard logic gate output."""
        a, b = inputs[0], inputs[1] if len(inputs) > 1 else inputs[0]
        
        if gate_type == 'AND':
            return a & b
        elif gate_type == 'OR':
            return a | b
        elif gate_type == 'NOT':
            return 1 - a  # NOT of first input
        elif gate_type == 'XOR':
            return a ^ b
        elif gate_type == 'XNOR':
            return 1 - (a ^ b)
        else:
            return 0
    
    def _calculate_probabilistic_output(self, gate_type: str, inputs: Tuple[int, ...], 
                                      antigens: List[str], expression_data: Dict[str, Dict[str, float]],
                                      thresholds: Dict[str, float]) -> float:
        """Calculate probabilistic gate output based on expression levels."""
        # Convert binary inputs to probabilities based on expression levels
        probs = []
        for i, antigen in enumerate(antigens[:len(inputs)]):
            if inputs[i] == 1:
                # High expression probability
                tumor_expr = expression_data[antigen]['tumor_expression']
                threshold = thresholds[antigen]
                prob = min(0.95, max(0.05, tumor_expr / (tumor_expr + threshold)))
            else:
                # Low expression probability
                prob = 0.1
            probs.append(prob)
        
        # Apply logic gate to probabilities
        a, b = probs[0], probs[1] if len(probs) > 1 else probs[0]
        
        if gate_type == 'AND':
            return a * b
        elif gate_type == 'OR':
            return a + b - (a * b)
        elif gate_type == 'NOT':
            return 1 - a
        elif gate_type == 'XOR':
            return a * (1 - b) + (1 - a) * b
        elif gate_type == 'XNOR':
            return a * b + (1 - a) * (1 - b)
        else:
            return 0.0
    
    def _determine_cell_type(self, inputs: Tuple[int, ...], antigens: List[str], 
                           expression_data: Dict[str, Dict[str, float]]) -> str:
        """Determine if the input pattern represents tumor or healthy cells."""
        score = 0
        for i, antigen in enumerate(antigens[:len(inputs)]):
            antigen_info = self.data_processor.get_biomarker_info(antigen)
            if antigen_info['is_oncogenic'] and inputs[i] == 1:
                score += 1
            elif antigen_info['is_suppressor'] and inputs[i] == 0:
                score += 1
        
        return 'tumor' if score >= len(inputs) / 2 else 'healthy'
    
    def generate_all_truth_tables(self) -> Dict[str, Dict[str, Any]]:
        """Generate truth tables for all logic gates."""
        truth_tables = {}
        for gate in self.logic_gates:
            truth_tables[gate] = self.generate_truth_table(gate)
        return truth_tables
    
    def calculate_selectivity_scores(self, truth_tables: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate selectivity scores for all logic gates.
        Selectivity = tumor_kill / (healthy_kill + ε)
        """
        selectivity_scores = {}
        epsilon = 0.001  # Small constant to avoid division by zero
        
        for gate, truth_table in truth_tables.items():
            tumor_kill = 0
            healthy_kill = 0
            
            for i, output in enumerate(truth_table['outputs']):
                prob = truth_table['probabilities'][i]
                cell_type = truth_table['cell_types'][i]
                
                kill_probability = output * prob
                
                if cell_type == 'tumor':
                    tumor_kill += kill_probability
                else:
                    healthy_kill += kill_probability
            
            selectivity = tumor_kill / (healthy_kill + epsilon)
            selectivity_scores[gate] = selectivity
        
        return selectivity_scores
    
    def get_best_gate_recommendation(self, selectivity_scores: Dict[str, float]) -> Dict[str, Any]:
        """Get the best logic gate recommendation with explanation."""
        best_gate = max(selectivity_scores.keys(), key=lambda x: selectivity_scores[x])
        best_score = selectivity_scores[best_gate]
        
        # Generate explanation based on gate type
        explanations = {
            'AND': "Both tumor antigens must be present for activation, maximizing tumor specificity while minimizing healthy tissue damage.",
            'OR': "Either tumor antigen can trigger activation, increasing sensitivity but potentially reducing specificity.",
            'NOT': "Activates when the primary antigen is absent, useful for targeting antigen-loss variants.",
            'XOR': "Activates when only one antigen is present, targeting heterogeneous tumor populations.",
            'XNOR': "Activates when both antigens have the same state, targeting consistent expression patterns."
        }
        
        recommendation = {
            'gate': best_gate,
            'score': best_score,
            'explanation': explanations.get(best_gate, "Selected based on highest selectivity score.")
        }
        
        return recommendation
