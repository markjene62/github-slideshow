#!/usr/bin/env python3
"""
Cantilevered Monopitch Awning Design - REVISED
Steel Frame with Appropriate Section Sizes

Design Parameters:
- Length (L): 7,500 mm
- Projection (P): 800 mm  
- Slope (θ): 35°
- Material: Various square steel tubing sizes
"""

import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np

class RevisedAwningDesign:
    def __init__(self):
        # Design parameters
        self.length = 7500  # mm
        self.projection = 800  # mm
        self.slope_angle = 35  # degrees
        
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
        
        # Member sizes (determined from analysis)
        self.member_sizes = {
            'wall_plate': {'b': 50, 't': 3},      # 50x50x3 SHS
            'spine_beam': {'b': 50, 't': 3},      # 50x50x3 SHS  
            'horizontal_rafter': {'b': 80, 't': 4}, # 80x80x4 SHS (main load bearing)
            'kicker_braces': {'b': 40, 't': 3}    # 40x40x3 SHS
        }
        
    def calculate_section_properties(self, b, t):
        """Calculate section properties for square tube"""
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
        """Design and check all structural members"""
        loads = self.calculate_loads()
        results = {}
        
        for member, size in self.member_sizes.items():
            section_props = self.calculate_section_properties(size['b'], size['t'])
            
            if member == 'horizontal_rafter':
                # Main load bearing member
                bending_stress = (loads['max_moment'] * 1e6) / section_props['Z']  # N/mm²
                shear_stress = (loads['max_shear'] * 1000) / section_props['area']  # N/mm²
                combined_stress = math.sqrt(bending_stress**2 + 3*shear_stress**2)
                
                results[member] = {
                    'size': f"{size['b']}x{size['b']}x{size['t']} SHS",
                    'section_props': section_props,
                    'bending_stress': bending_stress,
                    'shear_stress': shear_stress,
                    'combined_stress': combined_stress,
                    'utilization': combined_stress / self.yield_strength
                }
            else:
                # Other members - simplified analysis
                # Assume 50% of main rafter loading for sizing
                reduced_moment = loads['max_moment'] * 0.5
                bending_stress = (reduced_moment * 1e6) / section_props['Z']
                
                results[member] = {
                    'size': f"{size['b']}x{size['b']}x{size['t']} SHS",
                    'section_props': section_props,
                    'bending_stress': bending_stress,
                    'utilization': bending_stress / self.yield_strength
                }
        
        results['loads'] = loads
        return results
    
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
            coords['kicker_braces'].append({
                'start': (x_pos, 0, 0),
                'end': (x_pos, self.projection, self.height_difference),
                'number': i + 1
            })
        
        return coords
    
    def calculate_member_lengths(self):
        """Calculate lengths of all members"""
        lengths = {}
        
        lengths['wall_plate'] = self.length
        lengths['spine_beam'] = self.length
        lengths['horizontal_rafter'] = self.rafter_length
        lengths['kicker_brace'] = self.rafter_length
        
        return lengths
    
    def generate_material_list(self):
        """Generate complete material and cutting list"""
        lengths = self.calculate_member_lengths()
        
        material_list = []
        
        # Wall plate
        size = self.member_sizes['wall_plate']
        material_list.append({
            'member': 'Wall Plate',
            'size': f"{size['b']}x{size['b']}x{size['t']} SHS",
            'length_mm': lengths['wall_plate'],
            'length_m': lengths['wall_plate'] / 1000,
            'quantity': 1,
            'total_length_m': lengths['wall_plate'] / 1000
        })
        
        # Spine beam
        size = self.member_sizes['spine_beam']
        material_list.append({
            'member': 'Spine Beam',
            'size': f"{size['b']}x{size['b']}x{size['t']} SHS",
            'length_mm': lengths['spine_beam'],
            'length_m': lengths['spine_beam'] / 1000,
            'quantity': 1,
            'total_length_m': lengths['spine_beam'] / 1000
        })
        
        # Horizontal rafter
        size = self.member_sizes['horizontal_rafter']
        material_list.append({
            'member': 'Horizontal Rafter',
            'size': f"{size['b']}x{size['b']}x{size['t']} SHS",
            'length_mm': round(lengths['horizontal_rafter']),
            'length_m': round(lengths['horizontal_rafter'] / 1000, 3),
            'quantity': 1,
            'total_length_m': round(lengths['horizontal_rafter'] / 1000, 3)
        })
        
        # Kicker braces
        size = self.member_sizes['kicker_braces']
        material_list.append({
            'member': 'Kicker Braces',
            'size': f"{size['b']}x{size['b']}x{size['t']} SHS",
            'length_mm': round(lengths['kicker_brace']),
            'length_m': round(lengths['kicker_brace'] / 1000, 3),
            'quantity': self.num_kickers,
            'total_length_m': round(self.num_kickers * lengths['kicker_brace'] / 1000, 3)
        })
        
        # Calculate total
        total_length = sum(item['total_length_m'] for item in material_list)
        
        return material_list, total_length

    def create_technical_drawings(self):
        """Create comprehensive technical drawings"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(24, 18))
        fig.suptitle('Cantilevered Monopitch Awning - REVISED Steel Frame Design\nVariable Section Sizes', 
                     fontsize=18, fontweight='bold')
        
        # Plan view (top view)
        ax1.set_title('PLAN VIEW', fontweight='bold', fontsize=16)
        ax1.set_aspect('equal')
        
        # Wall plate - 50x50x3
        ax1.plot([0, self.length], [0, 0], 'k-', linewidth=4, label='Wall Plate (50x50x3)')
        
        # Spine beam - 50x50x3
        ax1.plot([0, self.length], [self.projection, self.projection], 'r-', linewidth=4, label='Spine Beam (50x50x3)')
        
        # Horizontal rafter - 80x80x4
        ax1.plot([self.length/2, self.length/2], [0, self.projection], 'b-', linewidth=6, label='Horizontal Rafter (80x80x4)')
        
        # Kicker braces - 40x40x3
        for i in range(self.num_kickers):
            x_pos = (i + 1) * self.kicker_spacing
            ax1.plot([x_pos, x_pos], [0, self.projection], 'g--', linewidth=3, alpha=0.8)
            ax1.text(x_pos, self.projection/2, f'K{i+1}\n40x40x3', rotation=90, ha='center', va='center', fontsize=10)
        
        # Dimensions
        ax1.annotate('', xy=(0, -150), xytext=(self.length, -150), 
                    arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        ax1.text(self.length/2, -200, f'Length = {self.length} mm', ha='center', fontsize=14, fontweight='bold')
        
        ax1.annotate('', xy=(-300, 0), xytext=(-300, self.projection), 
                    arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        ax1.text(-450, self.projection/2, f'Projection = {self.projection} mm', ha='center', va='center', 
                rotation=90, fontsize=14, fontweight='bold')
        
        # Add spacing dimensions for kicker braces
        ax1.annotate('', xy=(0, self.projection + 100), xytext=(self.kicker_spacing, self.projection + 100), 
                    arrowprops=dict(arrowstyle='<->', color='blue'))
        ax1.text(self.kicker_spacing/2, self.projection + 150, f'{self.kicker_spacing:.0f} mm c/c', ha='center', fontsize=12, color='blue')
        
        ax1.set_xlim(-600, self.length + 300)
        ax1.set_ylim(-350, self.projection + 300)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper right', fontsize=12)
        ax1.set_xlabel('Length (mm)', fontsize=12)
        ax1.set_ylabel('Projection (mm)', fontsize=12)
        
        # Side elevation
        ax2.set_title('SIDE ELEVATION', fontweight='bold', fontsize=16)
        ax2.set_aspect('equal')
        
        # Wall connection point
        ax2.plot([0, 0], [0, 0], 'ko', markersize=12, label='Wall Connection')
        
        # Rafter slope line
        ax2.plot([0, self.projection], [0, self.height_difference], 'b-', linewidth=6, label='Rafter (80x80x4)')
        
        # End point
        ax2.plot([self.projection, self.projection], [self.height_difference, self.height_difference], 'ro', markersize=12, label='Free End')
        
        # Show slope angle
        angle_arc = patches.Arc((0, 0), 300, 300, angle=0, theta1=0, theta2=self.slope_angle, color='red', linewidth=2)
        ax2.add_patch(angle_arc)
        ax2.text(200, 50, f'{self.slope_angle}°', fontsize=14, color='red', fontweight='bold')
        
        # Dimensions
        ax2.annotate('', xy=(0, -80), xytext=(self.projection, -80), 
                    arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        ax2.text(self.projection/2, -130, f'Projection = {self.projection} mm', ha='center', fontsize=14, fontweight='bold')
        
        ax2.annotate('', xy=(self.projection + 80, 0), xytext=(self.projection + 80, self.height_difference), 
                    arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        ax2.text(self.projection + 150, self.height_difference/2, f'Rise = {round(self.height_difference)} mm', 
                ha='left', va='center', fontsize=14, fontweight='bold')
        
        # Rafter length
        ax2.annotate('', xy=(20, 20), xytext=(self.projection-20, self.height_difference-20), 
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
        ax2.text(self.projection/2, self.height_difference/2 + 50, f'Rafter Length = {round(self.rafter_length)} mm', 
                ha='center', va='center', fontsize=12, color='blue', fontweight='bold', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        
        ax2.set_xlim(-200, self.projection + 300)
        ax2.set_ylim(-200, self.height_difference + 150)
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=12)
        ax2.set_xlabel('Projection (mm)', fontsize=12)
        ax2.set_ylabel('Height (mm)', fontsize=12)
        
        # 3D Isometric view with member sizes
        ax3.set_title('3D ISOMETRIC VIEW WITH MEMBER SIZES', fontweight='bold', fontsize=16)
        
        # Wall plate (50x50x3)
        ax3.plot([0, 0.75], [0, 0], 'k-', linewidth=5, label='Wall Plate (50x50x3)')
        ax3.text(0.375, -0.05, '50x50x3', ha='center', fontsize=10, fontweight='bold')
        
        # Spine beam (50x50x3)
        ax3.plot([0.2, 0.95], [0.4, 0.4], 'r-', linewidth=5, label='Spine Beam (50x50x3)')
        ax3.text(0.575, 0.45, '50x50x3', ha='center', fontsize=10, fontweight='bold')
        
        # Horizontal rafter (80x80x4)
        ax3.plot([0.375, 0.575], [0, 0.4], 'b-', linewidth=8, label='Horizontal Rafter (80x80x4)')
        ax3.text(0.475, 0.2, '80x80x4', ha='center', va='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.2", facecolor="lightblue"))
        
        # Kicker braces (40x40x3)
        kicker_positions = np.linspace(0.1, 0.65, self.num_kickers)
        for i, pos in enumerate(kicker_positions):
            ax3.plot([pos, pos + 0.2], [0, 0.4], 'g--', linewidth=4, alpha=0.8)
            if i == 2:  # Label middle kicker
                ax3.text(pos + 0.1, 0.15, '40x40x3', fontsize=9, ha='center', 
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgreen"))
        
        ax3.text(0.5, 0.55, 'Kicker Braces (40x40x3)', ha='center', fontsize=12, fontweight='bold')
        
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 0.6)
        ax3.set_aspect('equal')
        ax3.legend(fontsize=10)
        ax3.set_xticks([])
        ax3.set_yticks([])
        
        # Connection and fabrication details
        ax4.set_title('FABRICATION & CONNECTION DETAILS', fontweight='bold', fontsize=16)
        
        # Connection detail boxes
        details = [
            {'pos': (0.1, 0.7), 'size': (0.35, 0.25), 'title': 'WALL PLATE CONNECTION', 'color': 'lightblue',
             'text': '• Fix to masonry/concrete wall\n• Use M16 expansion bolts\n• 400mm centers maximum\n• 8mm fillet welds all round'},
            {'pos': (0.55, 0.7), 'size': (0.35, 0.25), 'title': 'KICKER BRACE CONNECTION', 'color': 'lightgreen',
             'text': '• Notch kicker into wall plate\n• 6mm fillet welds\n• Full penetration at spine beam\n• Grind smooth'},
            {'pos': (0.1, 0.35), 'size': (0.35, 0.25), 'title': 'RAFTER CONNECTION', 'color': 'lightcoral',
             'text': '• Full strength butt welds\n• Back gouge and re-weld\n• NDT if required\n• 10mm fillet to plates'},
            {'pos': (0.55, 0.35), 'size': (0.35, 0.25), 'title': 'GENERAL NOTES', 'color': 'lightyellow',
             'text': '• All steel to AS/NZS 3679.1\n• Welding to AS/NZS 1554.1\n• Hot dip galvanize\n• Prime and paint'}
        ]
        
        for detail in details:
            rect = Rectangle(detail['pos'], detail['size'][0], detail['size'][1], 
                           linewidth=2, edgecolor='black', facecolor=detail['color'], alpha=0.7)
            ax4.add_patch(rect)
            
            # Title
            ax4.text(detail['pos'][0] + detail['size'][0]/2, detail['pos'][1] + detail['size'][1] - 0.05, 
                    detail['title'], ha='center', va='top', fontsize=11, fontweight='bold')
            
            # Details text
            ax4.text(detail['pos'][0] + 0.02, detail['pos'][1] + detail['size'][1] - 0.08, 
                    detail['text'], ha='left', va='top', fontsize=9)
        
        # Load information
        ax4.text(0.05, 0.25, 'DESIGN LOADS:\n• Dead Load: 0.5 kN/m²\n• Live Load: 0.6 kN/m²\n• Wind Load: 1.2 kN/m²\n• Total UDL: 8.25 kN/m', 
                fontsize=10, va='top', fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        # Material specification
        ax4.text(0.55, 0.25, 'MATERIALS:\n• Steel: S275 (min)\n• Yield: 275 N/mm²\n• Bolts: Grade 8.8\n• Galvanizing: AS/NZS 4680', 
                fontsize=10, va='top', fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.set_xticks([])
        ax4.set_yticks([])
        
        plt.tight_layout()
        return fig

def main():
    # Create revised awning design instance
    awning = RevisedAwningDesign()
    
    # Perform structural analysis
    analysis = awning.design_members()
    
    # Generate material list
    material_list, total_length = awning.generate_material_list()
    
    # Print design summary
    print("="*90)
    print("CANTILEVERED MONOPITCH AWNING DESIGN - REVISED")
    print("="*90)
    print(f"Dimensions:")
    print(f"  Length (L): {awning.length} mm")
    print(f"  Projection (P): {awning.projection} mm")
    print(f"  Slope angle: {awning.slope_angle}°")
    print(f"  Rafter length: {awning.rafter_length:.1f} mm")
    print(f"  Height difference: {awning.height_difference:.1f} mm")
    print(f"  Kicker brace spacing: {awning.kicker_spacing:.0f} mm c/c")
    print()
    
    print("MEMBER ANALYSIS:")
    print("-" * 70)
    for member, data in analysis.items():
        if member != 'loads':
            print(f"{member.replace('_', ' ').title()}:")
            print(f"  Size: {data['size']}")
            print(f"  Area: {data['section_props']['area']:.1f} mm²")
            print(f"  Section modulus: {data['section_props']['Z']:.0f} mm³")
            if 'bending_stress' in data:
                print(f"  Bending stress: {data['bending_stress']:.1f} N/mm²")
            if 'shear_stress' in data:
                print(f"  Shear stress: {data['shear_stress']:.1f} N/mm²")
            if 'combined_stress' in data:
                print(f"  Combined stress: {data['combined_stress']:.1f} N/mm²")
            print(f"  Utilization: {data['utilization']:.2f} ({data['utilization']*100:.1f}%)")
            
            if data['utilization'] < 0.8:
                print("  ✓ ADEQUATE")
            elif data['utilization'] < 1.0:
                print("  ⚠ ACCEPTABLE")
            else:
                print("  ✗ OVERSTRESSED")
            print()
    
    print("LOADING SUMMARY:")
    print("-" * 40)
    loads = analysis['loads']
    print(f"  Total distributed load: {loads['total_load']:.2f} kN/m")
    print(f"  Maximum moment: {loads['max_moment']:.2f} kNm")
    print(f"  Maximum shear: {loads['max_shear']:.2f} kN")
    print(f"  Wall reaction: {loads['wall_reaction']:.2f} kN")
    print()
    
    print("REVISED MATERIAL LIST:")
    print("-" * 80)
    print(f"{'Member':<20} {'Size':<15} {'Length(mm)':<12} {'Qty':<5} {'Total(m)':<10}")
    print("-" * 80)
    
    for item in material_list:
        print(f"{item['member']:<20} {item['size']:<15} {item['length_mm']:<12} "
              f"{item['quantity']:<5} {item['total_length_m']:<10.3f}")
    
    print("-" * 80)
    print(f"{'TOTAL LENGTH:':<55} {total_length:.3f} m")
    print()
    
    # Weight estimation
    total_weight = 0
    weights = {'50x50x3': 4.57, '80x80x4': 9.63, '40x40x3': 3.63}  # kg/m
    
    print("WEIGHT ESTIMATION:")
    print("-" * 40)
    for item in material_list:
        if '50x50x3' in item['size']:
            weight = item['total_length_m'] * weights['50x50x3']
        elif '80x80x4' in item['size']:
            weight = item['total_length_m'] * weights['80x80x4']
        elif '40x40x3' in item['size']:
            weight = item['total_length_m'] * weights['40x40x3']
        else:
            weight = 0
        
        total_weight += weight
        print(f"  {item['member']}: {weight:.1f} kg")
    
    print(f"  TOTAL WEIGHT: {total_weight:.1f} kg")
    print()
    
    # Create and save technical drawings
    fig = awning.create_technical_drawings()
    plt.savefig('/workspace/awning_technical_drawings_revised.png', dpi=300, bbox_inches='tight')
    print("Revised technical drawings saved as 'awning_technical_drawings_revised.png'")
    
    return awning, analysis, material_list

if __name__ == "__main__":
    awning, analysis, material_list = main()