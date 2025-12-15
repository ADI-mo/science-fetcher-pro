"""
🦠 ANTIBIOTIC RESISTANCE SURVEILLANCE - MAIN RUNNER
Complete analysis pipeline: Data Generation → Analysis → Visualization
"""

import os
import sys
from datetime import datetime

print("="*70)
print("🦠 ANTIBIOTIC RESISTANCE SURVEILLANCE ANALYSIS")
print("="*70)
print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
print()

# Ensure output directory exists
os.makedirs('outputs', exist_ok=True)

# Step 1: Generate Data
print("📊 STEP 1: GENERATING SYNTHETIC DATASET")
print("-"*70)
try:
    import generate_data
    print()
except Exception as e:
    print(f"❌ Error in data generation: {e}")
    sys.exit(1)

# Step 2: Run Analysis
print("\n" + "="*70)
print("📈 STEP 2: STATISTICAL ANALYSIS")
print("-"*70)
try:
    import analyze
    print()
except Exception as e:
    print(f"❌ Error in analysis: {e}")
    sys.exit(1)

# Step 3: Create Visualizations
print("\n" + "="*70)
print("🎨 STEP 3: GENERATING VISUALIZATIONS")
print("-"*70)
try:
    import visualize
    print()
except Exception as e:
    print(f"❌ Error in visualization: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*70)
print("✅ PIPELINE COMPLETE!")
print("="*70)
print()
print("📁 Generated Files:")
print("   • data/antibiotic_resistance_surveillance.csv")
print("   • outputs/temporal_trends.png")
print("   • outputs/geographic_heatmap.png")
print("   • outputs/bacterial_analysis.png")
print("   • outputs/antibiotic_analysis.png")
print("   • outputs/clinical_outcomes.png")
print("   • outputs/correlation_matrix.png")
print()
print("🎉 Check the 'outputs' folder for all generated visualizations!")
print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
