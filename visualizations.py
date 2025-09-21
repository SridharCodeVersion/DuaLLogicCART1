import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class TruthTableVisualizer:
    """Creates visualizations for truth tables and analysis results."""
    
    def create_fixed_not_truth_table(self) -> go.Figure:
        """Create fixed NOT gate truth table for HCA input."""
        table_data = {
            'Input (HCA)': [0, 1],
            'Y (Output)': [1, 0],
            'Explanation': ['Activate (kill)', 'Deactivate (off)']
        }
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[f'<b>{col}</b>' for col in table_data.keys()],
                fill_color='#34495e',
                font=dict(color='white', size=14),
                align='center',
                height=40
            ),
            cells=dict(
                values=list(table_data.values()),
                fill_color=[['#ecf0f1' if i % 2 == 0 else 'white' for i in range(2)] for _ in range(len(table_data))],
                font=dict(size=12),
                align='center',
                height=35
            )
        )])
        
        fig.update_layout(
            title=dict(
                text=f'<b>NOT Gate Fixed Truth Table</b><br><sub>Input: 1=Present, 0=Absent | Output: 1=Kill, 0=Off</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            height=300,
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        return fig

    def create_simplified_truth_table(self, truth_table: Dict[str, Any], gate_name: str) -> go.Figure:
        """
        Create a simplified truth table with actual antigen names as headers.
        
        Args:
            truth_table: Truth table data with antigen names
            gate_name: Name of the logic gate
            
        Returns:
            Plotly table figure
        """
        antigen_names = truth_table.get('antigen_names', ['A', 'B'])
        inputs = truth_table['inputs']
        outputs = truth_table['outputs']
        
        # Clean antigen names for display
        antigen_a = antigen_names[0] if len(antigen_names) > 0 else 'A'
        antigen_b = antigen_names[1] if len(antigen_names) > 1 else 'B'
        
        # Prepare table data
        table_data = {
            f'{antigen_a}': [inp[0] for inp in inputs],
            f'{antigen_b}': [inp[1] for inp in inputs],
            'Y (Output)': outputs,
            'Action': ['🎯 Kill' if out == 1 else '❌ Off' for out in outputs]
        }
        
        # Create table figure
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[f'<b>{col}</b>' for col in table_data.keys()],
                fill_color='#34495e',
                font=dict(color='white', size=14),
                align='center',
                height=40
            ),
            cells=dict(
                values=list(table_data.values()),
                fill_color=[['#ecf0f1' if i % 2 == 0 else 'white' for i in range(len(inputs))] for _ in range(len(table_data))],
                font=dict(size=12),
                align='center',
                height=35
            )
        )])
        
        fig.update_layout(
            title=dict(
                text=f'<b>{gate_name} Gate Truth Table</b><br><sub>Input: 1=Present, 0=Absent | Output: 1=Kill, 0=Off</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            height=300,
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        return fig
    
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
        Create a bar chart comparing selectivity scores across logic gates for PDAC.
        
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
        
        # Enhanced color scheme for PDAC analysis
        colors = ['#27ae60' if i == 0 else '#3498db' if i == 1 else '#f39c12' if i == 2 else '#e74c3c' for i in range(len(gates))]
        
        fig = go.Figure(data=go.Bar(
            x=gates,
            y=scores,
            marker_color=colors,
            text=[f'{score:.3f}' for score in scores],
            textposition='auto',
            hovertemplate='<b>%{x} Gate</b><br>Selectivity: %{y:.3f}<br>Rank: %{pointNumber}<extra></extra>'
        ))
        
        fig.update_layout(
            title='🎯 PDAC Selectivity Ranking: Tumor Kill vs Healthy Cell Sparing',
            xaxis_title='Logic Gate Strategy',
            yaxis_title='Selectivity Score (Higher = Better)',
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='white'
        )
        
        # Add best score indicator
        if scores:
            fig.add_hline(
                y=max(scores),
                line_dash="dash",
                line_color="#27ae60",
                annotation_text="🏆 Optimal Choice",
                annotation_position="top right"
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
    
    def create_pdac_recommendation_card(self, best_gate: Dict[str, Any]) -> go.Figure:
        """
        Create a recommendation card specifically for PDAC therapy.
        
        Args:
            best_gate: Best gate recommendation with PDAC context
            
        Returns:
            Plotly figure object
        """
        gate_name = best_gate['gate']
        score = best_gate['score']
        explanation = best_gate.get('explanation', '')
        safety_note = best_gate.get('safety_note', '')
        
        # Create recommendation card
        fig = go.Figure()
        
        fig.add_annotation(
            x=0.5, y=0.8,
            text=f"<b>🏆 RECOMMENDED FOR PDAC</b><br><span style='font-size:24px'>{gate_name} Gate</span>",
            showarrow=False,
            font=dict(size=18, color='#2c3e50'),
            align='center'
        )
        
        fig.add_annotation(
            x=0.5, y=0.6,
            text=f"<b>Selectivity Score: {score:.3f}</b>",
            showarrow=False,
            font=dict(size=16, color='#e74c3c'),
            align='center'
        )
        
        fig.add_annotation(
            x=0.5, y=0.4,
            text=explanation,
            showarrow=False,
            font=dict(size=12, color='#34495e'),
            align='center',
            width=400
        )
        
        fig.add_annotation(
            x=0.5, y=0.2,
            text=f"<b>Safety Note:</b> {safety_note}",
            showarrow=False,
            font=dict(size=11, color='#27ae60'),
            align='center',
            width=400
        )
        
        fig.update_layout(
            height=300,
            width=500,
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='#f8f9fa'
        )
        
        return fig
