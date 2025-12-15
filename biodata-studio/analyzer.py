"""
BioData Studio - Growth Curve Analyzer
מערכת מתקדמת לניתוח growth curves
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.integrate import trapezoid
import warnings

warnings.filterwarnings('ignore')


class GrowthCurveAnalyzer:
    """מנתח growth curves ומחשב פרמטרים קינטיים"""
    
    def __init__(self, data_path=None, data=None):
        """
        Args:
            data_path: נתיב לקובץ CSV/Excel
            data: DataFrame ישיר (אופציונלי)
        """
        if data is not None:
            self.data = data
        elif data_path:
            self.data = self._load_data(data_path)
        else:
            raise ValueError("חייב לספק data_path או data")
        
        self.results = None
        self.fitted_curves = {}
    
    def _load_data(self, path):
        """טוען נתונים מקובץ"""
        if path.endswith('.csv'):
            return pd.read_csv(path)
        elif path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(path)
        else:
            raise ValueError("פורמט לא נתמך. השתמש ב-CSV או Excel")
    
    def _identify_columns(self):
        """מזהה אוטומטית את עמודות הזמן וה-OD"""
        cols = self.data.columns.str.lower()
        
        # חיפוש עמודת זמן
        time_col = None
        for pattern in ['time', 'hour', 'hr', 'h', 'זמן']:
            matches = [c for c in self.data.columns if pattern in c.lower()]
            if matches:
                time_col = matches[0]
                break
        
        if time_col is None:
            time_col = self.data.columns[0]  # ברירת מחדל
        
        # עמודות OD = כל השאר
        od_cols = [c for c in self.data.columns if c != time_col]
        
        return time_col, od_cols
    
    def _calculate_growth_rate(self, time, od):
        """מחשב growth rate מקסימלי (μ)"""
        # חישוב דיפרנציאלי של ln(OD)
        log_od = np.log(od + 1e-10)  # הימנע מ-log(0)
        
        # חלק אקספוננציאלי (אמצע הגרף)
        start_idx = len(od) // 4
        end_idx = 3 * len(od) // 4
        
        if end_idx - start_idx < 3:
            return 0.0, 0.0
        
        # רגרסיה לינארית
        time_exp = time[start_idx:end_idx]
        log_od_exp = log_od[start_idx:end_idx]
        
        if len(time_exp) < 2:
            return 0.0, 0.0
        
        # fit
        coeffs = np.polyfit(time_exp, log_od_exp, 1)
        growth_rate = coeffs[0]
        
        # doubling time
        doubling_time = np.log(2) / growth_rate if growth_rate > 0 else np.inf
        
        return growth_rate, doubling_time
    
    def _detect_lag_phase(self, time, od, threshold=0.05):
        """מזהה lag phase"""
        max_od = np.max(od)
        lag_threshold = threshold * max_od
        
        for i, val in enumerate(od):
            if val > lag_threshold:
                return time[i]
        
        return 0.0
    
    def _gompertz_model(self, t, A, mu, lag):
        """Gompertz growth model"""
        return A * np.exp(-np.exp(mu * np.e / A * (lag - t) + 1))
    
    def _logistic_model(self, t, A, mu, lag):
        """Logistic growth model"""
        return A / (1 + np.exp(4 * mu / A * (lag - t) + 2))
    
    def _fit_model(self, time, od, model='gompertz'):
        """מתאים מודל לנתונים"""
        A_guess = np.max(od)
        mu_guess = 0.1
        lag_guess = np.min(time)
        
        try:
            if model == 'gompertz':
                popt, _ = curve_fit(self._gompertz_model, time, od,
                                   p0=[A_guess, mu_guess, lag_guess],
                                   maxfev=5000, bounds=([0, 0, 0], [np.inf, 1, np.max(time)]))
                fitted = self._gompertz_model(time, *popt)
            elif model == 'logistic':
                popt, _ = curve_fit(self._logistic_model, time, od,
                                   p0=[A_guess, mu_guess, lag_guess],
                                   maxfev=5000, bounds=([0, 0, 0], [np.inf, 1, np.max(time)]))
                fitted = self._logistic_model(time, *popt)
            else:
                return None, None
            
            # R²
            ss_res = np.sum((od - fitted) ** 2)
            ss_tot = np.sum((od - np.mean(od)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return {'params': popt, 'fitted': fitted, 'r_squared': r_squared, 'model': model}, popt
        
        except:
            return None, None
    
    def analyze(self, model='gompertz'):
        """
        מריץ ניתוח מלא על כל ה-growth curves
        
        Args:
            model: 'gompertz' או 'logistic'
            
        Returns:
            DataFrame עם כל הפרמטרים
        """
        time_col, od_cols = self._identify_columns()
        time = self.data[time_col].values
        
        results = []
        
        for col in od_cols:
            od = self.data[col].values
            
            # נקה NaN
            valid_idx = ~np.isnan(od)
            time_clean = time[valid_idx]
            od_clean = od[valid_idx]
            
            if len(od_clean) < 3:
                continue
            
            # חישוב פרמטרים
            growth_rate, doubling_time = self._calculate_growth_rate(time_clean, od_clean)
            lag_phase = self._detect_lag_phase(time_clean, od_clean)
            max_od = np.max(od_clean)
            auc = trapezoid(od_clean, time_clean)
            
            # model fitting
            fit_result, params = self._fit_model(time_clean, od_clean, model=model)
            
            result = {
                'Sample': col,
                'Max_OD': round(max_od, 4),
                'Growth_Rate (1/h)': round(growth_rate, 4),
                'Doubling_Time (h)': round(doubling_time, 2),
                'Lag_Phase (h)': round(lag_phase, 2),
                'AUC': round(auc, 2),
            }
            
            if fit_result:
                result['Model_R²'] = round(fit_result['r_squared'], 4)
                result['Model'] = model
                self.fitted_curves[col] = fit_result
            
            results.append(result)
        
        self.results = pd.DataFrame(results)
        return self.results
    
    def get_summary_stats(self):
        """מחזיר סטטיסטיקה מסכמת"""
        if self.results is None:
            raise ValueError("רוץ analyze() קודם")
        
        numeric_cols = self.results.select_dtypes(include=[np.number]).columns
        summary = self.results[numeric_cols].describe()
        
        return summary
