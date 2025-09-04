#!/usr/bin/env python3
"""
Cantilevered Monopitch Awning Design
Steel Frame using 38mm x 38mm x 2mm Square Tubing

Design Parameters:
- Length (L): 7,500 mm
- Projection (P): 800 mm  
- Slope (θ): 35°
- Material: 38mm x 38mm x 2mm square steel tubing
"""

import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np

class AwningDesign:
    def __init__(self):
        # Design parameters
        self.length = 7500  # mm
        self.projection = 800  # mm
        self.slope_angle = 35  # degrees
        self.tube_size = 38  # mm
        self.tube_thickness = 2  # mm
        
        # Material properties (Steel S275)
        self.yield_strength = 275  # N/mm²
        self.elastic_modulus = 200000  # N/mm²
        self.density = 7850  # kg/m³
        
        # Load assumptions
        self.dead_load = 0.5  # kN/m² (self weight + sheeting)
        self.live_load = 0.6  # kN/m² (maintenance load)
        self.wind_load = 1.2  # kN/m² (uplift/downward)
        
        # Calculate derived dimensions
        self.slope_rad = math.radians(self.slope_angle)
        self.rafter_length = self.projection / math.cos(self.slope_rad)
        self.height_difference = self.projection * math.tan(self.slope_rad)
        
        # Kicker brace configuration
        self.num_kickers = 5
        self.kicker_spacing = self.length / (self.num_kickers + 1)
        
    def calculate_section_properties(self):
        """Calculate section properties for 38x38x2 square tube"""
        b = self.tube_size  # outer dimension
        t = self.tube_thickness
        b_inner = b - 2*t  # inner dimension
        
        # Area
        area = b**2 - b_inner**2
        
        # Second moment of area
        I = (b**4 - b_inner**4) / 12
        
        # Section modulus
        Z = I / (b/2)
        
        # Radius of gyration
        r = math.sqrt(I / area)
        
        return {
            'area': area,  # mm²
            'I': I,        # mm⁴
            'Z': Z,        # mm³
            'r': r         # mm
        }
    
    def calculate_loads(self):
        """Calculate loads on the structure"""
        # Load per unit length on rafter
        total_load = (self.dead_load + self.live_load) * (self.length / 1000)  # kN/m
        
        # Maximum moment at wall connection
        max_moment = total_load * (self.rafter_length/1000)**2 / 2  # kNm
        
        # Maximum shear at wall
        max_shear = total_load * (self.rafter_length/1000)  # kN
        
        # Reaction at wall plate
        wall_reaction = max_shear  # kN
        
        return {
            'total_load': total_load,
            'max_moment': max_moment,
            'max_shear': max_shear,
            'wall_reaction': wall_reaction
        }
    
    def design_members(self):
        """Design and check structural members"""
        section_props = self.calculate_section_properties()
        loads = self.calculate_loads()
        
        # Check bending stress in horizontal rafter
        bending_stress = (loads['max_moment'] * 1e6) / section_props['Z']  # N/mm²
        
        # Check shear stress
        shear_stress = (loads['max_shear'] * 1000) / section_props['area']  # N/mm²
        
        # Combined stress check (von Mises)
        combined_stress = math.sqrt(bending_stress**2 + 3*shear_stress**2)
        
        # Safety factors
        bending_utilization = bending_stress / self.yield_strength
        combined_utilization = combined_stress / self.yield_strength
        
        return {
            'section_props': section_props,
            'loads': loads,
            'bending_stress': bending_stress,
            'shear_stress': shear_stress,
            'combined_stress': combined_stress,
            'bending_utilization': bending_utilization,
            'combined_utilization': combined_utilization
        }
    
    def generate_frame_coordinates(self):
        """Generate coordinates for frame members"""
        coords = {}
        
        # Wall plate (horizontal along wall)
        coords['wall_plate'] = {
            'start': (0, 0, 0),
            'end': (self.length, 0, 0)
        }
        
        # Spine beam (horizontal at projection)
        coords['spine_beam'] = {
            'start': (0, self.projection, self.height_difference),
            'end': (self.length, self.projection, self.height_difference)
        }
        
        # Horizontal rafter (connecting wall plate to spine beam)
        coords['horizontal_rafter'] = {
            'start': (self.length/2, 0, 0),
            'end': (self.length/2, self.projection, self.height_difference)
        }
        
        # Kicker braces
        coords['kicker_braces'] = []
        for i in range(self.num_kickers):
            x_pos = (i + 1) * self.kicker_spacing
            # Kicker connects from wall plate to spine beam at an angle
            coords['kicker_braces'].append({
                'start': (x_pos, 0, 0),
                'end': (x_pos, self.projection, self.height_difference),
                'number': i + 1
            })
        
        return coords
    
    def calculate_member_lengths(self):
        """Calculate lengths of all members"""
        coords = self.generate_frame_coordinates()
        lengths = {}
        
        # Wall plate length
        lengths['wall_plate'] = self.length
        
        # Spine beam length  
        lengths['spine_beam'] = self.length
        
        # Horizontal rafter length
        lengths['horizontal_rafter'] = self.rafter_length
        
        # Kicker brace lengths (all same)
        lengths['kicker_brace'] = self.rafter_length
        
        return lengths
    
    def generate_material_list(self):
        """Generate complete material and cutting list"""
        lengths = self.calculate_member_lengths()
        
        material_list = []
        
        # Wall plate
        material_list.append({
            'member': 'Wall Plate',
            'size': '38x38x2 SHS',
            'length_mm': lengths['wall_plate'],
            'length_m': lengths['wall_plate'] / 1000,
            'quantity': 1,
            'total_length_m': lengths['wall_plate'] / 1000
        })
        
        # Spine beam
        material_list.append({
            'member': 'Spine Beam',
            'size': '38x38x2 SHS',
            'length_mm': lengths['spine_beam'],
            'length_m': lengths['spine_beam'] / 1000,
            'quantity': 1,
            'total_length_m': lengths['spine_beam'] / 1000
        })
        
        # Horizontal rafter
        material_list.append({
            'member': 'Horizontal Rafter',
            'size': '38x38x2 SHS',
            'length_mm': round(lengths['horizontal_rafter']),
            'length_m': round(lengths['horizontal_rafter'] / 1000, 3),
            'quantity': 1,
            'total_length_m': round(lengths['horizontal_rafter'] / 1000, 3)
        })
        
        # Kicker braces
        material_list.append({
            'member': 'Kicker Braces',
            'size': '38x38x2 SHS',
            'length_mm': round(lengths['kicker_brace']),
            'length_m': round(lengths['kicker_brace'] / 1000, 3),
            'quantity': self.num_kickers,
            'total_length_m': round(self.num_kickers * lengths['kicker_brace'] / 1000, 3)
        })
        
        # Calculate total
        total_length = sum(item['total_length_m'] for item in material_list)
        
        return material_list, total_length

    def create_technical_drawings(self):
        """Create technical drawings"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('Cantilevered Monopitch Awning - Steel Frame Design\n38mm x 38mm x 2mm Square Tubing', 
                     fontsize=16, fontweight='bold')
        
        # Plan view (top view)
        ax1.set_title('PLAN VIEW', fontweight='bold', fontsize=14)
        ax1.set_aspect('equal')
        
        # Wall plate
        ax1.plot([0, self.length], [0, 0], 'k-', linewidth=3, label='Wall Plate')
        
        # Spine beam
        ax1.plot([0, self.length], [self.projection, self.projection], 'r-', linewidth=3, label='Spine Beam')
        
        # Horizontal rafter
        ax1.plot([self.length/2, self.length/2], [0, self.projection], 'b-', linewidth=2, label='Horizontal Rafter')
        
        # Kicker braces
        for i in range(self.num_kickers):
            x_pos = (i + 1) * self.kicker_spacing
            ax1.plot([x_pos, x_pos], [0, self.projection], 'g--', linewidth=1.5, alpha=0.7)
            ax1.text(x_pos, self.projection/2, f'K{i+1}', rotation=90, ha='center', va='center')
        
        # Dimensions
        ax1.annotate('', xy=(0, -100), xytext=(self.length, -100), 
                    arrowprops=dict(arrowstyle='<->', color='black'))
        ax1.text(self.length/2, -150, f'Length = {self.length} mm', ha='center', fontsize=12)
        
        ax1.annotate('', xy=(-200, 0), xytext=(-200, self.projection), 
                    arrowprops=dict(arrowstyle='<->', color='black'))
        ax1.text(-300, self.projection/2, f'Projection = {self.projection} mm', ha='center', va='center', 
                rotation=90, fontsize=12)
        
        ax1.set_xlim(-500, self.length + 200)
        ax1.set_ylim(-300, self.projection + 200)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_xlabel('Length (mm)')
        ax1.set_ylabel('Projection (mm)')
        
        # Side elevation
        ax2.set_title('SIDE ELEVATION', fontweight='bold', fontsize=14)
        ax2.set_aspect('equal')
        
        # Wall plate (at ground level)
        ax2.plot([0, 0], [0, 0], 'ko', markersize=8)
        ax2.plot([0, self.projection], [0, self.height_difference], 'b-', linewidth=3, label='Rafter Slope')
        
        # Show slope angle
        angle_arc = patches.Arc((0, 0), 200, 200, angle=0, theta1=0, theta2=self.slope_angle, color='red')
        ax2.add_patch(angle_arc)
        ax2.text(150, 30, f'{self.slope_angle}°', fontsize=12, color='red')
        
        # Dimensions
        ax2.annotate('', xy=(0, -50), xytext=(self.projection, -50), 
                    arrowprops=dict(arrowstyle='<->', color='black'))
        ax2.text(self.projection/2, -100, f'Projection = {self.projection} mm', ha='center', fontsize=12)
        
        ax2.annotate('', xy=(self.projection + 50, 0), xytext=(self.projection + 50, self.height_difference), 
                    arrowprops=dict(arrowstyle='<->', color='black'))
        ax2.text(self.projection + 100, self.height_difference/2, f'Rise = {round(self.height_difference)} mm', 
                ha='left', va='center', fontsize=12)
        
        ax2.set_xlim(-100, self.projection + 200)
        ax2.set_ylim(-150, self.height_difference + 100)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlabel('Projection (mm)')
        ax2.set_ylabel('Height (mm)')
        
        # 3D Isometric view
        ax3.set_title('3D ISOMETRIC VIEW', fontweight='bold', fontsize=14)
        
        # Simplified 3D representation
        # Wall plate
        ax3.plot([0, 0.75], [0, 0], 'k-', linewidth=4, label='Wall Plate')
        
        # Spine beam
        ax3.plot([0.2, 0.95], [0.4, 0.4], 'r-', linewidth=4, label='Spine Beam')
        
        # Horizontal rafter
        ax3.plot([0.375, 0.575], [0, 0.4], 'b-', linewidth=3, label='Horizontal Rafter')
        
        # Kicker braces
        kicker_positions = np.linspace(0.1, 0.65, self.num_kickers)
        for i, pos in enumerate(kicker_positions):
            ax3.plot([pos, pos + 0.2], [0, 0.4], 'g--', linewidth=2, alpha=0.7)
            ax3.text(pos + 0.1, 0.2, f'K{i+1}', fontsize=8, ha='center')
        
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 0.5)
        ax3.set_aspect('equal')
        ax3.legend()
        ax3.set_xticks([])
        ax3.set_yticks([])
        
        # Connection details
        ax4.set_title('CONNECTION DETAILS', fontweight='bold', fontsize=14)
        
        # Wall plate connection detail
        wall_conn = Rectangle((0.1, 0.6), 0.3, 0.2, linewidth=2, edgecolor='black', facecolor='lightblue', alpha=0.7)
        ax4.add_patch(wall_conn)
        ax4.text(0.25, 0.7, 'Wall Plate\nConnection', ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Kicker brace connection
        kicker_conn = Rectangle((0.6, 0.6), 0.3, 0.2, linewidth=2, edgecolor='black', facecolor='lightgreen', alpha=0.7)
        ax4.add_patch(kicker_conn)
        ax4.text(0.75, 0.7, 'Kicker Brace\nConnection', ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Rafter connection
        rafter_conn = Rectangle((0.35, 0.3), 0.3, 0.2, linewidth=2, edgecolor='black', facecolor='lightcoral', alpha=0.7)
        ax4.add_patch(rafter_conn)
        ax4.text(0.5, 0.4, 'Rafter\nConnection', ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Notes
        ax4.text(0.05, 0.1, 'Notes:\n• All connections to be welded\n• Use 6mm fillet welds minimum\n• Galvanize after fabrication\n• Fix to wall with M12 bolts @ 600mm c/c', 
                fontsize=10, va='top')
        
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.set_xticks([])
        ax4.set_yticks([])
        
        plt.tight_layout()
        return fig

def main():
    # Create awning design instance
    awning = AwningDesign()
    
    # Perform structural analysis
    analysis = awning.design_members()
    
    # Generate material list
    material_list, total_length = awning.generate_material_list()
    
    # Print design summary
    print("="*80)
    print("CANTILEVERED MONOPITCH AWNING DESIGN")
    print("="*80)
    print(f"Dimensions:")
    print(f"  Length (L): {awning.length} mm")
    print(f"  Projection (P): {awning.projection} mm")
    print(f"  Slope angle: {awning.slope_angle}°")
    print(f"  Rafter length: {awning.rafter_length:.1f} mm")
    print(f"  Height difference: {awning.height_difference:.1f} mm")
    print()
    
    print("STRUCTURAL ANALYSIS:")
    print("-" * 40)
    print(f"Section Properties (38x38x2 SHS):")
    section = analysis['section_props']
    print(f"  Area: {section['area']:.1f} mm²")
    print(f"  Second moment of area: {section['I']:.0f} mm⁴")
    print(f"  Section modulus: {section['Z']:.1f} mm³")
    print(f"  Radius of gyration: {section['r']:.1f} mm")
    print()
    
    print(f"Loading:")
    loads = analysis['loads']
    print(f"  Total load: {loads['total_load']:.2f} kN/m")
    print(f"  Maximum moment: {loads['max_moment']:.2f} kNm")
    print(f"  Maximum shear: {loads['max_shear']:.2f} kN")
    print(f"  Wall reaction: {loads['wall_reaction']:.2f} kN")
    print()
    
    print(f"Stress Analysis:")
    print(f"  Bending stress: {analysis['bending_stress']:.1f} N/mm²")
    print(f"  Shear stress: {analysis['shear_stress']:.1f} N/mm²")
    print(f"  Combined stress: {analysis['combined_stress']:.1f} N/mm²")
    print(f"  Bending utilization: {analysis['bending_utilization']:.2f} ({analysis['bending_utilization']*100:.1f}%)")
    print(f"  Combined utilization: {analysis['combined_utilization']:.2f} ({analysis['combined_utilization']*100:.1f}%)")
    print()
    
    if analysis['combined_utilization'] < 1.0:
        print("✓ DESIGN IS ADEQUATE")
    else:
        print("✗ DESIGN REQUIRES LARGER SECTIONS")
    print()
    
    print("MATERIAL LIST:")
    print("-" * 40)
    print(f"{'Member':<20} {'Size':<12} {'Length(mm)':<12} {'Qty':<5} {'Total(m)':<10}")
    print("-" * 70)
    
    for item in material_list:
        print(f"{item['member']:<20} {item['size']:<12} {item['length_mm']:<12} "
              f"{item['quantity']:<5} {item['total_length_m']:<10.3f}")
    
    print("-" * 70)
    print(f"{'TOTAL LENGTH:':<50} {total_length:.3f} m")
    print()
    
    # Create and save technical drawings
    fig = awning.create_technical_drawings()
    plt.savefig('/workspace/awning_technical_drawings.png', dpi=300, bbox_inches='tight')
    print("Technical drawings saved as 'awning_technical_drawings.png'")
    
    return awning, analysis, material_list

if __name__ == "__main__":
    awning, analysis, material_list = main()