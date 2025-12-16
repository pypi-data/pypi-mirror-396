#!/usr/bin/env python3
"""
Example demonstrating the tactical scenario plotting capability.

This example shows how to visualize radar, target, and support jammer positions
on a 2D tactical plot.

Note: This example uses sys.path.insert() to allow running directly from the
repository without installation. In production code, install the package and
import normally: `import radar_range_equation as RRE`
"""

import sys
sys.path.insert(0, 'python/src')  # For running from repo without installation
import radar_range_equation as RRE


def example_default_tactical_scenario():
    """Demonstrate tactical scenario plotting with default parameters."""
    print("\n" + "="*70)
    print("Example 1: Tactical Scenario with Default Positions")
    print("="*70)
    print("Creating a tactical scenario plot with:")
    print("  - Radar at (10, 20) km - Blue 'x' marker")
    print("  - Target at (50, -20) km - Green solid square marker")
    print("  - Support jammer at (70, -10) km - Red hollow circle marker")
    print("  - X-axis range: 0 to 75 km")
    print("  - Y-axis range: -25 to 25 km")
    
    # Create the tactical scenario plot (matches the problem statement)
    fig = RRE.plot.tactical_scenario(show=False)
    
    print("✓ Generated tactical scenario plot")
    
    # Save the figure
    fig.savefig('/tmp/tactical_scenario_default.png', dpi=150, bbox_inches='tight')
    print("✓ Saved plot to /tmp/tactical_scenario_default.png")
    
    return fig


def example_custom_tactical_scenario():
    """Demonstrate tactical scenario plotting with custom parameters."""
    print("\n" + "="*70)
    print("Example 2: Tactical Scenario with Custom Positions")
    print("="*70)
    print("Creating a custom tactical scenario plot with:")
    print("  - Radar at (20, 15) km")
    print("  - Target at (60, -15) km")
    print("  - Support jammer at (80, -5) km")
    print("  - X-axis range: 0 to 100 km")
    print("  - Y-axis range: -30 to 30 km")
    
    # Create custom tactical scenario
    fig = RRE.plot.tactical_scenario(
        radar_pos=(20, 15),
        target_pos=(60, -15),
        jammer_pos=(80, -5),
        xlim=(0, 100),
        ylim=(-30, 30),
        show=False
    )
    
    print("✓ Generated custom tactical scenario plot")
    
    # Save the figure
    fig.savefig('/tmp/tactical_scenario_custom.png', dpi=150, bbox_inches='tight')
    print("✓ Saved plot to /tmp/tactical_scenario_custom.png")
    
    return fig


def example_multiple_scenarios():
    """Demonstrate multiple tactical scenarios for comparison."""
    print("\n" + "="*70)
    print("Example 3: Multiple Tactical Scenarios")
    print("="*70)
    print("Creating tactical scenarios for different operational contexts:")
    
    import matplotlib.pyplot as plt
    
    # Create a figure with multiple subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Scenario 1: Close range engagement
    plt.sca(ax1)
    plt.scatter(5, 10, marker='x', color='blue', s=80, label='Radar')
    plt.scatter(25, -10, marker='s', color='green', s=60, label='Target')
    plt.scatter(35, -5, marker='o', facecolors='none', edgecolors='red', s=80, label='Support jammer')
    plt.xlabel('X (km)', fontsize=12)
    plt.ylabel('Y (km)', fontsize=12)
    plt.title('Close Range Scenario', fontsize=12, fontweight='bold')
    plt.xlim(0, 40)
    plt.ylim(-15, 15)
    plt.xticks(range(0, 41, 5))
    plt.yticks(range(-15, 16, 5))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Scenario 2: Long range surveillance
    plt.sca(ax2)
    plt.scatter(10, 20, marker='x', color='blue', s=80, label='Radar')
    plt.scatter(80, -30, marker='s', color='green', s=60, label='Target')
    plt.scatter(120, -15, marker='o', facecolors='none', edgecolors='red', s=80, label='Support jammer')
    plt.xlabel('X (km)', fontsize=12)
    plt.ylabel('Y (km)', fontsize=12)
    plt.title('Long Range Scenario', fontsize=12, fontweight='bold')
    plt.xlim(0, 130)
    plt.ylim(-35, 25)
    plt.xticks(range(0, 131, 20))
    plt.yticks(range(-35, 26, 10))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    plt.tight_layout()
    
    print("✓ Generated multiple tactical scenarios")
    
    # Save the figure
    fig.savefig('/tmp/tactical_scenario_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved plot to /tmp/tactical_scenario_comparison.png")
    
    return fig


def main():
    """Run all tactical scenario examples."""
    print("\n" + "="*70)
    print("Radar Range Equation - Tactical Scenario Plotting Examples")
    print("="*70)
    print("This script demonstrates the tactical scenario plotting capability")
    print("of the radar_range_equation package.")
    
    try:
        # Run all examples
        example_default_tactical_scenario()
        example_custom_tactical_scenario()
        example_multiple_scenarios()
        
        print("\n" + "="*70)
        print("✓ All examples completed successfully!")
        print("="*70)
        print("\nGenerated plots saved to /tmp/:")
        print("  - tactical_scenario_default.png")
        print("  - tactical_scenario_custom.png")
        print("  - tactical_scenario_comparison.png")
        print("\nThese plots can be used for mission planning, analysis,")
        print("and tactical decision-making.")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
