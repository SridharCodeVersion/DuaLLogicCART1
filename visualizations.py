import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class TruthTableVisualizer:
    """Creates visualizations for truth tables and analysis results."""
    
    def create_truth_table_heatmap(self, truth_table: Dict[str, Any], gate_name: str) -> go.Figure:
        """
        Create a heatmap visualization of the truth table.
        
        Args:
            truth_table: Truth table data
            gate_name: Name of the logic gate
            
        Returns:
            Plotly figure object
        """
        # Prepare data for heatmap
        inputs = truth_table['inputs']
        outputs = truth_table['outputs']
        probabilities = truth_table['probabilities']
        cell_types = truth_table['cell_types']
        
        # Create matrix for visualization
        n_inputs = len(inputs)
        matrix_data = []
        labels = []
        
        for i in range(n_inputs):
            input_str = f"{''.join(map(str, inputs[i]))}"
            output_val = outputs[i]
            prob_val = probabilities[i]
            cell_type = cell_types[i]
            
            matrix_data.append([output_val, prob_val])
            labels.append(f"Input: {input_str}<br>Cell: {cell_type}")
        
        # Create figure
        fig = go.Figure(data=go.Heatmap(
            z=matrix_data,
            x=['Hard Logic', 'Probabilistic'],
            y=[f"Pattern {i+1}" for i in range(n_inputs)],
            text=labels,
            texttemplate='%{text}',
            hovertemplate='<b>%{y}</b><br>%{x}: %{z:.3f}<br>%{text}<extra></extra>',
            colorscale='RdYlBu_r',
            showscale=True
        ))
        
        fig.update_layout(
            title=f'{gate_name} Gate Truth Table',
            xaxis_title='Logic Type',
            yaxis_title='Input Patterns',
            height=400,
            width=600
        )
        
        return fig
    
    def create_selectivity_comparison(self, selectivity_scores: Dict[str, float]) -> go.Figure:
        """
        Create a bar chart comparing selectivity scores across logic gates.
        
        Args:
            selectivity_scores: Dictionary of gate names and their selectivity scores
            
        Returns:
            Plotly figure object
        """
        gates = list(selectivity_scores.keys())
        scores = list(selectivity_scores.values())
        
        # Sort by score for better visualization
        sorted_data = sorted(zip(gates, scores), key=lambda x: x[1], reverse=True)
        gates, scores = zip(*sorted_data)
        
        # Color the best gate differently
        colors = ['#e74c3c' if i == 0 else '#3498db' for i in range(len(gates))]
        
        fig = go.Figure(data=go.Bar(
            x=gates,
            y=scores,
            marker_color=colors,
            text=[f'{score:.3f}' for score in scores],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Logic Gate Selectivity Comparison',
            xaxis_title='Logic Gate',
            yaxis_title='Selectivity Score (Tumor Kill / Healthy Kill)',
            height=400,
            showlegend=False
        )
        
        fig.add_hline(
            y=max(scores),
            line_dash="dash",
            line_color="red",
            annotation_text="Best Score"
        )
        
        return fig
    
    def create_expression_comparison(self, expression_data: Dict[str, Dict[str, float]], 
                                   selected_antigens: Dict[str, List[str]]) -> go.Figure:
        """
        Create a comparison plot of expression levels between tumor and healthy cells.
        
        Args:
            expression_data: Expression data for all antigens
            selected_antigens: Selected tumor and healthy antigens
            
        Returns:
            Plotly figure object
        """
        antigens = []
        tumor_expr = []
        healthy_expr = []
        antigen_types = []
        
        for antigen_type, antigen_list in selected_antigens.items():
            for antigen in antigen_list:
                if antigen in expression_data:
                    antigens.append(antigen)
                    tumor_expr.append(expression_data[antigen]['tumor_expression'])
                    healthy_expr.append(expression_data[antigen]['healthy_expression'])
                    antigen_types.append(antigen_type.title())
        
        fig = go.Figure()
        
        # Add tumor expression bars
        fig.add_trace(go.Bar(
            name='Tumor Expression',
            x=antigens,
            y=tumor_expr,
            marker_color='#e74c3c',
            text=[f'{val:.2f}' for val in tumor_expr],
            textposition='auto'
        ))
        
        # Add healthy expression bars
        fig.add_trace(go.Bar(
            name='Healthy Expression',
            x=antigens,
            y=healthy_expr,
            marker_color='#27ae60',
            text=[f'{val:.2f}' for val in healthy_expr],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Biomarker Expression Levels: Tumor vs Healthy Cells',
            xaxis_title='Biomarkers',
            yaxis_title='Expression Level',
            height=400,
            barmode='group'
        )
        
        return fig
    
    def create_fold_change_plot(self, expression_data: Dict[str, Dict[str, float]]) -> go.Figure:
        """
        Create a plot showing fold changes for each biomarker.
        
        Args:
            expression_data: Expression data for all antigens
            
        Returns:
            Plotly figure object
        """
        antigens = list(expression_data.keys())
        fold_changes = [expression_data[antigen]['fold_change'] for antigen in antigens]
        
        # Create color scale based on fold change
        colors = ['#e74c3c' if fc > 1 else '#3498db' for fc in fold_changes]
        
        fig = go.Figure(data=go.Bar(
            x=antigens,
            y=fold_changes,
            marker_color=colors,
            text=[f'{fc:.2f}x' for fc in fold_changes],
            textposition='auto'
        ))
        
        fig.add_hline(
            y=1,
            line_dash="dash",
            line_color="black",
            annotation_text="No Change (1x)"
        )
        
        fig.update_layout(
            title='Fold Change: Tumor vs Healthy Expression',
            xaxis_title='Biomarkers',
            yaxis_title='Fold Change (Tumor/Healthy)',
            height=400
        )
        
        return fig
    
    def create_summary_dashboard(self, analysis_results: Dict[str, Any], 
                               selected_antigens: Dict[str, List[str]]) -> go.Figure:
        """
        Create a comprehensive dashboard summarizing the analysis.
        
        Args:
            analysis_results: Complete analysis results
            selected_antigens: Selected antigens
            
        Returns:
            Plotly figure object with subplots
        """
        from plotly.subplots import make_subplots
        
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Selectivity Scores',
                'Best Gate Performance',
                'Expression Comparison',
                'Analysis Summary'
            ),
            specs=[[{"type": "bar"}, {"type": "indicator"}],
                   [{"type": "bar"}, {"type": "table"}]]
        )
        
        # Selectivity scores
        selectivity_scores = analysis_results['selectivity_scores']
        gates = list(selectivity_scores.keys())
        scores = list(selectivity_scores.values())
        
        fig.add_trace(
            go.Bar(x=gates, y=scores, name='Selectivity'),
            row=1, col=1
        )
        
        # Best gate indicator
        best_gate = analysis_results['best_gate']
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=best_gate['score'],
                title={"text": f"Best Gate: {best_gate['gate']}"},
                gauge={'axis': {'range': [None, max(scores)]}}
            ),
            row=1, col=2
        )
        
        # Summary table
        summary_data = [
            ["Recommended Gate", best_gate['gate']],
            ["Selectivity Score", f"{best_gate['score']:.3f}"],
            ["Tumor Antigens", ", ".join(selected_antigens['tumor'])],
            ["Healthy Antigens", ", ".join(selected_antigens['healthy'])]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Parameter', 'Value']),
                cells=dict(values=list(zip(*summary_data)))
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False, title_text="CAR-T Analysis Dashboard")
        
        return fig
