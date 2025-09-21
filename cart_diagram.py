import numpy as np
from typing import Dict, List, Any
import base64
from io import BytesIO

class CARTDiagramGenerator:
    """Generates personalized CAR-T structure diagrams."""
    
    def __init__(self, selected_antigens: Dict[str, List[str]]):
        self.selected_antigens = selected_antigens
        self.svg_width = 700
        self.svg_height = 480
    
    def generate_cart_diagram(self, costimulatory_domain: str = "CD28", style: str = "Standard") -> str:
        """
        Generate SVG diagram of CAR-T structure with labeled components.
        
        Args:
            costimulatory_domain: Either "CD28" or "4-1BB"
            style: Diagram style ("Standard", "Detailed", "Simplified")
            
        Returns:
            SVG content as string
        """
        svg_content = f'''
        <svg width="{self.svg_width}" height="{self.svg_height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <style>
                    .title {{ font-family: Arial, sans-serif; font-size: 20px; font-weight: bold; fill: #2c3e50; }}
                    .label {{ font-family: Arial, sans-serif; font-size: 12px; fill: #34495e; }}
                    .component-label {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #e74c3c; }}
                    .antigen-label {{ font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #3498db; }}
                    .cell-membrane {{ fill: #f39c12; stroke: #d68910; stroke-width: 3; }}
                    .scfv-domain {{ fill: #3498db; stroke: #2980b9; stroke-width: 2; }}
                    .hinge-region {{ fill: #9b59b6; stroke: #8e44ad; stroke-width: 2; }}
                    .transmembrane {{ fill: #e67e22; stroke: #d35400; stroke-width: 2; }}
                    .costimulatory {{ fill: #27ae60; stroke: #229954; stroke-width: 2; }}
                    .cd3zeta {{ fill: #e74c3c; stroke: #c0392b; stroke-width: 2; }}
                </style>
            </defs>
            
            <!-- Background -->
            <rect width="{self.svg_width}" height="{self.svg_height}" fill="#ecf0f1"/>
            
            <!-- Title -->
            <text x="{self.svg_width//2}" y="30" text-anchor="middle" class="title">
                Personalized CAR-T Structure for PDAC
            </text>
            
            <!-- Cell membrane -->
            <rect x="50" y="200" width="600" height="20" class="cell-membrane" rx="10"/>
            <text x="350" y="240" text-anchor="middle" class="component-label">T-Cell Membrane</text>
            
            {self._generate_extracellular_domain(style)}
            {self._generate_intracellular_domain(costimulatory_domain, style)}
            {self._generate_labels_and_annotations(style)}
        </svg>
        '''
        
        return svg_content
    
    def _generate_extracellular_domain(self, style: str) -> str:
        """Generate the extracellular domain components."""
        components = []
        
        # scFv domains for tumor antigens
        tumor_antigens = self.selected_antigens['tumor']
        
        # First scFv domain
        components.append(f'''
            <!-- First scFv Domain -->
            <ellipse cx="250" cy="130" rx="50" ry="35" class="scfv-domain"/>
            <text x="250" y="135" text-anchor="middle" class="antigen-label">{tumor_antigens[0]}</text>
            <text x="250" y="95" text-anchor="middle" class="component-label">scFv Domain 1</text>
        ''')
        
        # Second scFv domain (if available)
        if len(tumor_antigens) > 1:
            components.append(f'''
                <!-- Second scFv Domain -->
                <ellipse cx="450" cy="130" rx="50" ry="35" class="scfv-domain"/>
                <text x="450" y="135" text-anchor="middle" class="antigen-label">{tumor_antigens[1]}</text>
                <text x="450" y="95" text-anchor="middle" class="component-label">scFv Domain 2</text>
            ''')
        else:
            components.append(f'''
                <!-- Second scFv Domain (Generic) -->
                <ellipse cx="450" cy="130" rx="50" ry="35" class="scfv-domain"/>
                <text x="450" y="135" text-anchor="middle" class="antigen-label">Target 2</text>
                <text x="450" y="95" text-anchor="middle" class="component-label">scFv Domain 2</text>
            ''')
        
        # Hinge region
        components.append('''
            <!-- Hinge Region -->
            <rect x="330" y="170" width="40" height="25" class="hinge-region" rx="5"/>
            <text x="350" y="160" text-anchor="middle" class="component-label">Hinge Region</text>
        ''')
        
        # Connecting lines
        components.append('''
            <!-- Connecting lines -->
            <line x1="250" y1="165" x2="330" y2="182" stroke="#34495e" stroke-width="3"/>
            <line x1="450" y1="165" x2="370" y2="182" stroke="#34495e" stroke-width="3"/>
            <line x1="350" y1="195" x2="350" y2="200" stroke="#34495e" stroke-width="4"/>
        ''')
        
        return ''.join(components)
    
    def _escape_svg_text(self, text: str) -> str:
        """Escape text for safe SVG rendering."""
        if not text:
            return 'Unknown'
        # Basic SVG text escaping
        text = str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Limit length to prevent overflow
        if len(text) > 15:
            text = text[:12] + '...'
        return text
    
    def _generate_intracellular_domain(self, costimulatory_domain: str, style: str) -> str:
        """Generate the intracellular domain components."""
        components = []
        
        # Transmembrane domain
        components.append('''
            <!-- Transmembrane Domain -->
            <rect x="330" y="200" width="40" height="20" class="transmembrane"/>
            <text x="400" y="215" class="component-label">Transmembrane</text>
        ''')
        
        # Costimulatory domain
        costim_y = 250
        components.append(f'''
            <!-- Costimulatory Domain -->
            <rect x="310" y="{costim_y}" width="80" height="25" class="costimulatory" rx="12"/>
            <text x="350" y="{costim_y + 17}" text-anchor="middle" class="component-label">{costimulatory_domain}</text>
        ''')
        
        # CD3ζ signaling domain
        cd3_y = 300
        components.append(f'''
            <!-- CD3ζ Signaling Domain -->
            <rect x="290" y="{cd3_y}" width="120" height="35" class="cd3zeta" rx="17"/>
            <text x="350" y="{cd3_y + 22}" text-anchor="middle" class="component-label">CD3ζ Signaling</text>
        ''')
        
        # Connecting lines for intracellular
        components.append(f'''
            <!-- Intracellular connecting lines -->
            <line x1="350" y1="220" x2="350" y2="{costim_y}" stroke="#34495e" stroke-width="3"/>
            <line x1="350" y1="{costim_y + 25}" x2="350" y2="{cd3_y}" stroke="#34495e" stroke-width="3"/>
        ''')
        
        return ''.join(components)
    
    def _generate_labels_and_annotations(self, style: str) -> str:
        """Generate additional labels and annotations."""
        components = []
        
        # Extracellular vs Intracellular labels
        components.append('''
            <!-- Extracellular label -->
            <text x="80" y="130" class="label" transform="rotate(-90 80 130)">EXTRACELLULAR</text>
            <line x1="110" y1="60" x2="110" y2="190" stroke="#bdc3c7" stroke-width="2" stroke-dasharray="5,5"/>
            
            <!-- Intracellular label -->
            <text x="80" y="280" class="label" transform="rotate(-90 80 280)">INTRACELLULAR</text>
            <line x1="110" y1="230" x2="110" y2="360" stroke="#bdc3c7" stroke-width="2" stroke-dasharray="5,5"/>
        ''')
        
        # Legend
        legend_x = 450
        legend_y = 380
        tumor_text = ", ".join(self.selected_antigens['tumor'][:2]) if self.selected_antigens['tumor'] else "None"
        healthy_text = ", ".join(self.selected_antigens['healthy'][:2]) if self.selected_antigens['healthy'] else "None"
        components.append(f'''
            <!-- Legend -->
            <text x="{legend_x}" y="{legend_y}" class="component-label">Selected Antigens:</text>
            <text x="{legend_x}" y="{legend_y + 20}" class="label">Tumor: {tumor_text}</text>
            <text x="{legend_x}" y="{legend_y + 40}" class="label">Healthy: {healthy_text}</text>
        ''')
        
        return ''.join(components)
    
    def svg_to_png(self, svg_content: str, width: int = 800, height: int = 600) -> bytes:
        """
        Convert SVG content to PNG bytes.
        Note: This is a simplified implementation. In production, you might want to use
        libraries like cairosvg or wkhtmltopdf for better SVG to PNG conversion.
        """
        try:
            # For now, we'll return a placeholder PNG
            # In a real implementation, you would use a proper SVG to PNG converter
            import io
            import base64
            
            # Create a simple placeholder PNG (1x1 pixel)
            png_data = base64.b64decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
            )
            
            return png_data
            
        except Exception as e:
            # Return empty bytes if conversion fails
            return b''
