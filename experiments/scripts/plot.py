#!/usr/bin/env python3
"""
LLMP6 Architecture Diagram Generation Script
 
Generates architecture and execution mode diagrams:
1. Fig1: LLMP6 Six-Layer Architecture
2. Fig2: LLMP6 Execution Modes (Union vs Intersection)
"""
 
import os
import matplotlib
matplotlib.use('Agg')  # 不显示图片
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patches as mpatches
import numpy as np
 
def plot_architecture(output_dir):
    """
    Plot Fig1: LLMP6 Six-Layer Architecture
    """
    fig, ax = plt.subplots(figsize=(10, 4), dpi=100)
    ax.set_xlim(-0.5, 7.5)
    ax.set_ylim(-0.5, 0.9)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 定义各层
    layers = ['Input', 'Assign', 'Core', 'Filter', 'Tool', 'Check', 'Show', 'Output']
    x_pos = np.array([0, 1, 2, 3, 4, 5, 6, 7])
    
    # 输入和输出使用相同的中性色
    input_output_color = [0.95, 0.97, 1.0]  # 淡蓝色
    
    # 区域定义和颜色
    zone_data = [
        (1, 2, 'FRONT', [0.85, 0.90, 0.95]),  # 浅蓝色，只覆盖Assign
        (2, 6, 'CENTER', [0.95, 0.85, 0.90]),  # 浅粉色，覆盖Core, Filter, Tool, Check
        (6, 7, 'BACK', [0.90, 0.95, 0.85])    # 浅绿色，只覆盖Show
    ]
    
    # 为每个框分配颜色
    colors = []
    for i in range(len(layers)):
        if i == 0 or i == len(layers)-1:  # Input 和 Output
            colors.append(input_output_color)
        else:
            for start_idx, end_idx, label, color in zone_data:
                if start_idx <= i < end_idx:
                    colors.append(color)
                    break
    
    # 计算框的高度和位置
    box_height = 0.4
    box_width = 0.7
    box_y = 0  # 框的垂直中心位置
    
    # 绘制节点
    for i, (layer, x, color) in enumerate(zip(layers, x_pos, colors)):
        rect = patches.FancyBboxPatch(
            (x-0.35, box_y - box_height/2), box_width, box_height,
            boxstyle="round,pad=0.02,rounding_size=0.1",
            facecolor=color, edgecolor=[0.3, 0.3, 0.5],
            linewidth=1.5
        )
        ax.add_patch(rect)
        ax.text(x, box_y, layer, 
                ha='center', va='center',
                fontsize=11, fontweight='bold')
    
    # 绘制箭头 - 在框的高度中央
    arrow_y = box_y
    for i in range(7):
        start_x = x_pos[i] + 0.35
        end_x = x_pos[i+1] - 0.35
        ax.annotate('', 
                    xy=(end_x, arrow_y),
                    xytext=(start_x, arrow_y),
                    arrowprops=dict(
                        arrowstyle='->', 
                        color=[0.2, 0.4, 0.6], 
                        lw=1.5,
                        mutation_scale=15
                    ))
    
    # 绘制区域背景 - 连续无空白（增加与主体的距离）
    zone_y = 0.52
    zone_height = 0.12
    
    for start_idx, end_idx, label, color in zone_data:
        zone_start = x_pos[start_idx] - 0.5
        zone_end = x_pos[end_idx-1] + 0.5
        zone_width = zone_end - zone_start
        zone_center = zone_start + zone_width/2
        
        # 绘制区域背景矩形
        rect = patches.Rectangle(
            (zone_start, zone_y), zone_width, zone_height,
            facecolor=color, edgecolor=[0.4, 0.4, 0.4],
            linewidth=0.5, alpha=0.5
        )
        ax.add_patch(rect)
        
        # 添加区域标签
        ax.text(zone_center, zone_y + zone_height/2, label,
                ha='center', va='center',
                fontsize=9, fontweight='bold')
    
    # 添加红色反馈箭头 - 从Check指向Core
    check_center_x = x_pos[5]
    core_center_x = x_pos[2]
    arrow_start_y = box_y - box_height/2
    arrow_end_y = box_y - box_height/2
    
    ax.annotate('',
                xy=(core_center_x, arrow_end_y),
                xytext=(check_center_x, arrow_start_y),
                arrowprops=dict(
                    arrowstyle='->',
                    color='red',
                    lw=2,
                    mutation_scale=15,
                    connectionstyle='arc3,rad=-0.3'
                ))
    
    # 添加箭头标签
    ax.text(3.5, -0.35, 'Retry on Fail',
            ha='center', va='center',
            fontsize=9, fontweight='bold', color='red')
    
    # 主标题
    ax.set_title('LLMP6: Six-Layer Architecture', 
                 fontsize=14, 
                 fontweight='bold', 
                 pad=20)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    output_path = os.path.join(output_dir, 'fig1_architecture.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Fig1 saved: {output_path}")
 
def plot_execution_modes(output_dir):
    """
    Plot Fig2: LLMP6 Execution Modes (Union vs Intersection)
    """
    # Create figure
    fig = plt.figure(figsize=(8, 4), dpi=100, facecolor='white')
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Define colors
    union_color = [0.2, 0.5, 0.8]  # Blue for union
    intersection_color = [0.8, 0.3, 0.3]  # Red for intersection
    union_circle_color = [0.7, 0.8, 1.0]  # Light blue for union circles
    model_colors = [[0.85, 0.92, 0.95], [0.95, 0.85, 0.90], [0.90, 0.95, 0.85]]
    
    # Circle parameters
    circle_centers = [(0.4, 0.5), (0.6, 0.6), (0.5, 0.4)]
    circle_radius = 0.2
    
    # ============================================
    # Left side: Union Mode (Venn Diagram)
    # ============================================
    ax1 = plt.subplot(1, 2, 1, facecolor='white')
    ax1.set_xlim(0, 1.0)
    ax1.set_ylim(0, 1.0)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # Create three overlapping circles for union - ALL SAME COLOR
    for i, (x, y) in enumerate(circle_centers):
        circle = plt.Circle((x, y), circle_radius, 
                            color=union_circle_color,
                            alpha=0.6, 
                            ec='black', 
                            lw=1)
        ax1.add_patch(circle)
        ax1.text(x, y, f'M{i+1}', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Add union symbol
    ax1.text(0.5, 0.85, 'Union Mode', fontsize=11, fontweight='bold', ha='center', color=union_color)
    ax1.text(0.5, 0.5, '∪', ha='center', va='center', fontsize=20, fontweight='bold')
    
    # ============================================
    # Right side: Intersection Mode (Venn Diagram)
    # ============================================
    ax2 = plt.subplot(1, 2, 2, facecolor='white')
    ax2.set_xlim(0, 1.0)
    ax2.set_ylim(0, 1.0)
    ax2.set_aspect('equal')
    ax2.axis('off')
    
    # First, draw the three circles with low transparency
    for i, (x, y) in enumerate(circle_centers):
        circle = plt.Circle((x, y), circle_radius, 
                            color=model_colors[i], 
                            alpha=0.3,  # Lower alpha
                            ec='black', 
                            lw=1)
        ax2.add_patch(circle)
        ax2.text(x, y, f'M{i+1}', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Create intersection area manually
    # Define a fine grid of points
    grid_size = 400
    x_vals = np.linspace(0, 1.0, grid_size)
    y_vals = np.linspace(0, 1.0, grid_size)
    
    # Find points that are inside all three circles
    intersection_points = []
    
    for x in x_vals:
        for y in y_vals:
            inside_all = True
            for cx, cy in circle_centers:
                distance_sq = (x - cx)**2 + (y - cy)**2
                if distance_sq > circle_radius**2:
                    inside_all = False
                    break
            if inside_all:
                intersection_points.append((x, y))
    
    # If we found intersection points, create a convex hull polygon
    if len(intersection_points) > 3:
        from scipy.spatial import ConvexHull
        
        points_array = np.array(intersection_points)
        
        # Create convex hull
        hull = ConvexHull(points_array)
        
        # Get hull vertices
        hull_points = points_array[hull.vertices]
        
        # Create and add polygon
        polygon = mpatches.Polygon(hull_points, 
                                  closed=True, 
                                  facecolor='red', 
                                  alpha=0.7, 
                                  edgecolor='red', 
                                  linewidth=1.5)
        ax2.add_patch(polygon)
        
        # Add intersection symbol
        # Find the centroid of the hull
        centroid = np.mean(hull_points, axis=0)
        ax2.text(centroid[0], centroid[1], '∩', 
                 ha='center', va='center', fontsize=20, fontweight='bold', color='white')
    else:
        # Fallback: draw a red dot in the center
        center_x = np.mean([c[0] for c in circle_centers])
        center_y = np.mean([c[1] for c in circle_centers])
        intersection_circle = plt.Circle((center_x, center_y), 0.08, 
                                         color='red', 
                                         alpha=0.7, 
                                         ec='red', 
                                         lw=1.5)
        ax2.add_patch(intersection_circle)
        ax2.text(center_x, center_y, '∩', 
                 ha='center', va='center', fontsize=20, fontweight='bold', color='white')
    
    # Add intersection label
    ax2.text(0.5, 0.85, 'Intersection Mode', fontsize=11, fontweight='bold', ha='center', color=intersection_color)
    
    # Main title
    plt.suptitle('LLMP6 Execution Modes', fontsize=12, fontweight='bold', y=0.95)
    
    # ============================================
    # Add simple code examples
    # ============================================
    fig.text(0.25, 0.05, '--filter-model M1 M2 M3', 
             fontsize=8, fontfamily='monospace', ha='center', style='italic')
    
    fig.text(0.75, 0.05, '--filter-model M1 --filter-model M2 --filter-model M3', 
             fontsize=8, fontfamily='monospace', ha='center', style='italic')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    
    # Save image
    output_path = os.path.join(output_dir, 'fig2_execution_modes.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Fig2 saved: {output_path}")
 
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.dirname(script_dir), 'results')
    os.makedirs(output_dir, exist_ok=True)
    
    print('=' * 60)
    print('LLMP6 Architecture Diagram Generation')
    print('=' * 60)
    
    plot_architecture(output_dir)
    plot_execution_modes(output_dir)
    
    print('=' * 60)
    print('✓ All diagrams generated successfully!')
    print('=' * 60)
 
if __name__ == '__main__':
    main()
