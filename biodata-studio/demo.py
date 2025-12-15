"""
🧬 BioData Studio - Demo Script
דוגמה מלאה לשימוש במערכת
"""

from analyzer import GrowthCurveAnalyzer
from visualizer import Visualizer
from statistics import StatisticalAnalyzer
from report_generator import ReportGenerator
from generate_demo_data import create_demo_dataset

print("="*60)
print("🧬 BioData Studio - Growth Curve Analyzer")
print("="*60)
print()

# שלב 1: יצירת נתוני דמו
print("📊 שלב 1: יצירת נתוני דמו...")
demo_data = create_demo_dataset(n_timepoints=25, output_path='demo_data.csv')
print()

# שלב 2: טעינה וניתוח
print("🔬 שלב 2: ניתוח growth curves...")
analyzer = GrowthCurveAnalyzer('demo_data.csv')
results = analyzer.analyze(model='gompertz')

print("✅ ניתוח הושלם!")
print(f"   נותחו {len(results)} דגימות\n")
print("📋 תוצאות:")
print(results.to_string(index=False))
print()

# שלב 3: סטטיסטיקה
print("📊 שלב 3: ניתוח סטטיסטי...")
stats_analyzer = StatisticalAnalyzer(results)

print("\n📈 סיכום סטטיסטי:")
summary = stats_analyzer.generate_summary_table()
print(summary)
print()

# קורלציות
print("🔗 מטריצת קורלציות:")
corr_analysis = stats_analyzer.correlation_analysis()
print(corr_analysis['correlation_matrix'])
print()

# Outliers
print("⚠️ זיהוי outliers (Growth Rate):")
outliers = stats_analyzer.outlier_detection(parameter='Growth_Rate (1/h)', method='iqr')
if len(outliers) > 0:
    print(outliers[['Sample', 'Growth_Rate (1/h)']])
else:
    print("   לא נמצאו outliers")
print()

# שלב 4: ויזואליזציות
print("🎨 שלב 4: יצירת ויזואליזציות...")
visualizer = Visualizer(analyzer)

# גרף growth curves
print("   📈 יוצר growth curves...")
fig1 = visualizer.plot_growth_curves(show_fitted=True)
fig1.write_html('growth_curves.html')
print("      ✅ נשמר: growth_curves.html")

# השוואת growth rates
print("   📊 יוצר השוואת growth rates...")
fig2 = visualizer.plot_growth_rate_comparison()
fig2.write_html('growth_rates.html')
print("      ✅ נשמר: growth_rates.html")

# Heatmap
print("   🔥 יוצר heatmap...")
fig3 = visualizer.plot_parameter_heatmap()
fig3.write_html('heatmap.html')
print("      ✅ נשמר: heatmap.html")

print()

# שלב 5: דוח מלא
print("📄 שלב 5: יצירת דוח HTML מלא...")
report_gen = ReportGenerator(analyzer, visualizer, stats_analyzer)
report_path = report_gen.generate_html_report(
    output_path='full_report.html',
    title='Growth Curve Analysis - Demo Report'
)
print()

# סיכום
print("="*60)
print("✨ הושלם בהצלחה! ✨")
print("="*60)
print("\n📂 קבצים שנוצרו:")
print("   📊 demo_data.csv - נתוני הדמו")
print("   📈 growth_curves.html - גרף growth curves")
print("   📊 growth_rates.html - השוואת growth rates")
print("   🔥 heatmap.html - heatmap של פרמטרים")
print("   📄 full_report.html - דוח HTML מלא")
print()
print("💡 פתח את full_report.html בדפדפן לראות את הדוח המלא!")
print()

# תובנות אוטומטיות
print("🧠 תובנות אוטומטיות:")
fastest = results.loc[results['Growth_Rate (1/h)'].idxmax()]
slowest = results.loc[results['Growth_Rate (1/h)'].idxmin()]

print(f"   ⚡ הגידול המהיר ביותר: {fastest['Sample']} ({fastest['Growth_Rate (1/h)']:.3f} 1/h)")
print(f"   🐌 הגידול האיטי ביותר: {slowest['Sample']} ({slowest['Growth_Rate (1/h)']:.3f} 1/h)")

max_od = results.loc[results['Max_OD'].idxmax()]
print(f"   📈 OD מקסימלי: {max_od['Sample']} (OD={max_od['Max_OD']:.3f})")

avg_doubling = results['Doubling_Time (h)'].mean()
print(f"   ⏱️ זמן הכפלה ממוצע: {avg_doubling:.2f} שעות")

print()
print("🎉 נהנת? עכשיו תוכל לנתח את הנתונים שלך!")
