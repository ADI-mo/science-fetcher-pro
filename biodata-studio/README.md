# 🧬 BioData Studio - Growth Curve Analyzer

מערכת מתקדמת לניתוח growth curves של מיקרואורגניזמים.

## ✨ Features

- 📊 **ניתוח אוטומטי** של growth curves (lag phase, exponential, stationary)
- 📈 **חישוב פרמטרים**: growth rate, doubling time, max OD, AUC
- 🤖 **Model fitting**: Gompertz, Logistic, Richards models
- 📉 **סטטיסטיקה**: ANOVA, t-tests, multiple testing correction
- 🎨 **ויזואליזציות אינטראקטיביות**: Plotly-based plots
- 📋 **דוחות HTML** מלאים ואוטומטיים
- 🔧 **תמיכה בפורמטים שונים**: CSV, Excel

## 🚀 Quick Start

```python
from analyzer import GrowthCurveAnalyzer

# טען נתונים
analyzer = GrowthCurveAnalyzer('data.csv')

# רץ ניתוח
results = analyzer.analyze()

# יצר דוח
analyzer.generate_report('output_report.html')
```

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 📖 Documentation

ראה `examples/demo.py` לדוגמת שימוש מלאה.
