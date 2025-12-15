"""
יוצר נתוני דמו סינתטיים של growth curves
"""

import numpy as np
import pandas as pd


def generate_growth_curve(time, A=1.0, mu=0.3, lag=2.0, noise=0.05):
    """
    יוצר growth curve סינתטי עם מודל Gompertz
    
    Args:
        time: וקטור זמן
        A: OD מקסימלי
        mu: growth rate
        lag: lag phase
        noise: רעש (0-1)
    """
    # Gompertz model
    od = A * np.exp(-np.exp(mu * np.e / A * (lag - time) + 1))
    
    # הוספת רעש
    od_with_noise = od + np.random.normal(0, noise * A, size=len(time))
    od_with_noise = np.maximum(od_with_noise, 0.001)  # מניעת ערכים שליליים
    
    return od_with_noise


def create_demo_dataset(n_timepoints=20, output_path='demo_data.csv'):
    """
    יוצר dataset דמו עם מספר תנאים שונים
    
    Args:
        n_timepoints: מספר נקודות זמן
        output_path: נתיב לשמירה
    """
    time = np.linspace(0, 24, n_timepoints)
    
    data = {'Time (h)': time}
    
    # תנאים שונים
    conditions = {
        'Control': {'A': 1.2, 'mu': 0.35, 'lag': 2.0, 'noise': 0.03},
        'High_Temp': {'A': 0.9, 'mu': 0.42, 'lag': 1.5, 'noise': 0.04},
        'Low_Temp': {'A': 1.0, 'mu': 0.25, 'lag': 3.0, 'noise': 0.03},
        'Antibiotic_Low': {'A': 1.1, 'mu': 0.30, 'lag': 2.5, 'noise': 0.04},
        'Antibiotic_High': {'A': 0.6, 'mu': 0.18, 'lag': 4.0, 'noise': 0.05},
        'Rich_Media': {'A': 1.5, 'mu': 0.45, 'lag': 1.0, 'noise': 0.03},
        'Minimal_Media': {'A': 0.7, 'mu': 0.20, 'lag': 3.5, 'noise': 0.04},
    }
    
    for condition, params in conditions.items():
        data[condition] = generate_growth_curve(time, **params)
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    
    print(f"✅ נתוני דמו נוצרו: {output_path}")
    print(f"   📊 {len(conditions)} תנאים, {n_timepoints} נקודות זמן")
    
    return df


if __name__ == '__main__':
    create_demo_dataset()
