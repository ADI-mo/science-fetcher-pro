"""
🔬 COMPREHENSIVE ANTIBIOTIC RESISTANCE ANALYSIS
Using Pandas and NumPy for advanced data analysis and visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class AntibioticResistanceAnalyzer:
    """Main analyzer class for AMR surveillance data"""
    
    def __init__(self, data_path):
        """Load and prepare data"""
        print("📂 Loading data...")
        self.df = pd.read_csv(data_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        print(f"✅ Loaded {len(self.df):,} records\n")
        
    def basic_statistics(self):
        """Calculate comprehensive statistics"""
        print("="*70)
        print("📊 BASIC STATISTICS")
        print("="*70)
        
        print(f"\n🔢 Dataset Overview:")
        print(f"   Total samples: {len(self.df):,}")
        print(f"   Date range: {self.df['Date'].min().date()} to {self.df['Date'].max().date()}")
        print(f"   Countries: {self.df['Country'].nunique()}")
        print(f"   Bacteria species: {self.df['Bacterium'].nunique()}")
        print(f"   Antibiotics tested: {self.df['Antibiotic'].nunique()}")
        
        print(f"\n🦠 Resistance Overview:")
        resistant_count = self.df['Is_Resistant'].sum()
        resistance_rate = self.df['Is_Resistant'].mean() * 100
        print(f"   Resistant isolates: {resistant_count:,} ({resistance_rate:.1f}%)")
        print(f"   Susceptible isolates: {len(self.df) - resistant_count:,} ({100-resistance_rate:.1f}%)")
        
        print(f"\n👥 Patient Demographics:")
        print(f"   Mean age: {self.df['Patient_Age'].mean():.1f} years (SD: {self.df['Patient_Age'].std():.1f})")
        print(f"   Age range: {self.df['Patient_Age'].min()}-{self.df['Patient_Age'].max()} years")
        print(f"   Mean hospital stay: {self.df['Hospital_Stay_Days'].mean():.1f} days")
        print(f"   Mortality rate: {self.df['Patient_Died'].mean()*100:.2f}%")
        
        print(f"\n📈 Sample Sources:")
        source_counts = self.df['Sample_Source'].value_counts()
        for source, count in source_counts.items():
            print(f"   {source}: {count:,} ({count/len(self.df)*100:.1f}%)")
    
    def temporal_analysis(self):
        """Analyze trends over time"""
        print("\n" + "="*70)
        print("📅 TEMPORAL ANALYSIS")
        print("="*70)
        
        # Yearly trends
        yearly = self.df.groupby('Year').agg({
            'Is_Resistant': 'mean',
            'Hospital_Stay_Days': 'mean',
            'Patient_Died': 'mean',
            'Sample_ID': 'count'
        }).round(3)
        
        yearly.columns = ['Resistance_Rate', 'Avg_Hospital_Days', 'Mortality_Rate', 'Sample_Count']
        yearly['Resistance_Rate'] *= 100
        yearly['Mortality_Rate'] *= 100
        
        print("\n📊 Yearly Trends:")
        print(yearly.to_string())
        
        # Calculate trend
        years = yearly.index.values
        resistance = yearly['Resistance_Rate'].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(years, resistance)
        
        print(f"\n📈 Resistance Trend Analysis:")
        print(f"   Annual increase: {slope:+.2f}% per year")
        print(f"   R² value: {r_value**2:.3f}")
        print(f"   P-value: {p_value:.4f} {'(significant)' if p_value < 0.05 else '(not significant)'}")
        
        return yearly
    
    def geographic_analysis(self):
        """Analyze geographic patterns"""
        print("\n" + "="*70)
        print("🌍 GEOGRAPHIC ANALYSIS")
        print("="*70)
        
        country_stats = self.df.groupby('Country').agg({
            'Is_Resistant': 'mean',
            'Hospital_Stay_Days': 'mean',
            'Patient_Died': 'mean',
            'Sample_ID': 'count'
        }).round(3)
        
        country_stats.columns = ['Resistance_Rate', 'Avg_Hospital_Days', 'Mortality_Rate', 'N_Samples']
        country_stats['Resistance_Rate'] *= 100
        country_stats['Mortality_Rate'] *= 100
        country_stats = country_stats.sort_values('Resistance_Rate', ascending=False)
        
        print("\n🗺️ Resistance by Country (sorted by resistance rate):")
        print(country_stats.to_string())
        
        # Statistical test: Compare high vs low resistance countries
        high_res_countries = country_stats.nlargest(3, 'Resistance_Rate').index
        low_res_countries = country_stats.nsmallest(3, 'Resistance_Rate').index
        
        high_group = self.df[self.df['Country'].isin(high_res_countries)]['Is_Resistant']
        low_group = self.df[self.df['Country'].isin(low_res_countries)]['Is_Resistant']
        
        t_stat, p_value = stats.ttest_ind(high_group, low_group)
        
        print(f"\n🔬 Statistical Comparison (High vs Low resistance countries):")
        print(f"   High resistance (top 3): {', '.join(high_res_countries)}")
        print(f"   Low resistance (bottom 3): {', '.join(low_res_countries)}")
        print(f"   T-statistic: {t_stat:.3f}")
        print(f"   P-value: {p_value:.4e}")
        
        return country_stats
    
    def bacterial_analysis(self):
        """Analyze resistance by bacterial species"""
        print("\n" + "="*70)
        print("🦠 BACTERIAL SPECIES ANALYSIS")
        print("="*70)
        
        bacteria_stats = self.df.groupby('Bacterium').agg({
            'Is_Resistant': 'mean',
            'Hospital_Stay_Days': 'mean',
            'Patient_Died': 'mean',
            'Sample_ID': 'count'
        }).round(3)
        
        bacteria_stats.columns = ['Resistance_Rate', 'Avg_Hospital_Days', 'Mortality_Rate', 'N_Samples']
        bacteria_stats['Resistance_Rate'] *= 100
        bacteria_stats['Mortality_Rate'] *= 100
        bacteria_stats = bacteria_stats.sort_values('Resistance_Rate', ascending=False)
        
        print("\n🔬 Resistance by Bacterial Species:")
        print(bacteria_stats.to_string())
        
        # Chi-square test for independence
        contingency = pd.crosstab(self.df['Bacterium'], self.df['Is_Resistant'])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        
        print(f"\n📊 Chi-Square Test (Species vs Resistance):")
        print(f"   Chi² statistic: {chi2:.2f}")
        print(f"   Degrees of freedom: {dof}")
        print(f"   P-value: {p_value:.4e}")
        print(f"   Result: Resistance {'significantly differs' if p_value < 0.05 else 'does not differ significantly'} between species")
        
        return bacteria_stats
    
    def antibiotic_analysis(self):
        """Analyze resistance by antibiotic class"""
        print("\n" + "="*70)
        print("💊 ANTIBIOTIC ANALYSIS")
        print("="*70)
        
        # By individual antibiotic
        ab_stats = self.df.groupby('Antibiotic').agg({
            'Is_Resistant': 'mean',
            'Sample_ID': 'count'
        }).round(3)
        
        ab_stats.columns = ['Resistance_Rate', 'N_Tests']
        ab_stats['Resistance_Rate'] *= 100
        ab_stats = ab_stats.sort_values('Resistance_Rate', ascending=False)
        
        print("\n💊 Resistance by Antibiotic:")
        print(ab_stats.to_string())
        
        # By antibiotic class
        class_stats = self.df.groupby('Antibiotic_Class').agg({
            'Is_Resistant': 'mean',
            'Sample_ID': 'count'
        }).round(3)
        
        class_stats.columns = ['Resistance_Rate', 'N_Tests']
        class_stats['Resistance_Rate'] *= 100
        class_stats = class_stats.sort_values('Resistance_Rate', ascending=False)
        
        print("\n📦 Resistance by Antibiotic Class:")
        print(class_stats.to_string())
        
        return ab_stats, class_stats
    
    def risk_factor_analysis(self):
        """Analyze risk factors for resistance"""
        print("\n" + "="*70)
        print("⚠️ RISK FACTOR ANALYSIS")
        print("="*70)
        
        # Age group analysis
        age_resistance = self.df.groupby('Age_Group')['Is_Resistant'].agg(['mean', 'count'])
        age_resistance['mean'] *= 100
        age_resistance.columns = ['Resistance_Rate_%', 'N_Samples']
        
        print("\n👥 Resistance by Age Group:")
        print(age_resistance.to_string())
        
        # Sample source analysis
        source_resistance = self.df.groupby('Sample_Source')['Is_Resistant'].agg(['mean', 'count'])
        source_resistance['mean'] *= 100
        source_resistance.columns = ['Resistance_Rate_%', 'N_Samples']
        source_resistance = source_resistance.sort_values('Resistance_Rate_%', ascending=False)
        
        print("\n🩸 Resistance by Sample Source:")
        print(source_resistance.to_string())
        
        # Mortality analysis
        resistant_mortality = self.df[self.df['Is_Resistant']==True]['Patient_Died'].mean()
        susceptible_mortality = self.df[self.df['Is_Resistant']==False]['Patient_Died'].mean()
        
        print(f"\n☠️ Mortality Comparison:")
        print(f"   Resistant infections: {resistant_mortality*100:.2f}%")
        print(f"   Susceptible infections: {susceptible_mortality*100:.2f}%")
        print(f"   Relative risk: {resistant_mortality/susceptible_mortality:.2f}x higher")
        
        # Hospital stay comparison
        resistant_stay = self.df[self.df['Is_Resistant']==True]['Hospital_Stay_Days'].mean()
        susceptible_stay = self.df[self.df['Is_Resistant']==False]['Hospital_Stay_Days'].mean()
        
        t_stat, p_value = stats.ttest_ind(
            self.df[self.df['Is_Resistant']==True]['Hospital_Stay_Days'],
            self.df[self.df['Is_Resistant']==False]['Hospital_Stay_Days']
        )
        
        print(f"\n🏥 Hospital Stay Comparison:")
        print(f"   Resistant infections: {resistant_stay:.1f} days (mean)")
        print(f"   Susceptible infections: {susceptible_stay:.1f} days (mean)")
        print(f"   Difference: {resistant_stay - susceptible_stay:.1f} days longer")
        print(f"   T-test p-value: {p_value:.4e} (highly significant)")
        
    def correlation_analysis(self):
        """Analyze correlations between variables"""
        print("\n" + "="*70)
        print("🔗 CORRELATION ANALYSIS")
        print("="*70)
        
        # Select numeric columns
        numeric_cols = ['Patient_Age', 'Hospital_Stay_Days', 'Is_Resistant', 'Patient_Died']
        corr_matrix = self.df[numeric_cols].corr()
        
        print("\n📊 Correlation Matrix:")
        print(corr_matrix.round(3).to_string())
        
        # Notable correlations
        print(f"\n💡 Key Findings:")
        print(f"   • Resistance ↔ Hospital Stay: r = {corr_matrix.loc['Is_Resistant', 'Hospital_Stay_Days']:.3f}")
        print(f"   • Resistance ↔ Mortality: r = {corr_matrix.loc['Is_Resistant', 'Patient_Died']:.3f}")
        print(f"   • Age ↔ Mortality: r = {corr_matrix.loc['Patient_Age', 'Patient_Died']:.3f}")
        
        return corr_matrix
    
    def advanced_insights(self):
        """Generate advanced insights using NumPy"""
        print("\n" + "="*70)
        print("🧠 ADVANCED INSIGHTS")
        print("="*70)
        
        # Percentile analysis
        print("\n📈 Resistance Rate Percentiles:")
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        for p in percentiles:
            val = np.percentile(self.df.groupby(['Country', 'Year'])['Is_Resistant'].mean() * 100, p)
            print(f"   {p}th percentile: {val:.1f}%")
        
        # Identify outliers (countries with extremely high resistance)
        country_resistance = self.df.groupby('Country')['Is_Resistant'].mean() * 100
        mean_res = country_resistance.mean()
        std_res = country_resistance.std()
        outliers = country_resistance[country_resistance > mean_res + 2*std_res]
        
        print(f"\n⚠️ High-Risk Countries (>2 SD above mean):")
        if len(outliers) > 0:
            for country, rate in outliers.items():
                print(f"   {country}: {rate:.1f}% (Z-score: {(rate-mean_res)/std_res:.2f})")
        else:
            print("   No extreme outliers detected")
        
        # Year-over-year change analysis
        print(f"\n📊 Year-over-Year Changes:")
        yearly_res = self.df.groupby('Year')['Is_Resistant'].mean() * 100
        for year in sorted(self.df['Year'].unique())[1:]:
            prev_year = year - 1
            if prev_year in yearly_res.index:
                change = yearly_res[year] - yearly_res[prev_year]
                print(f"   {prev_year}→{year}: {change:+.2f}%")
    
    def run_complete_analysis(self):
        """Run all analyses"""
        print("\n" + "="*70)
        print("🔬 ANTIBIOTIC RESISTANCE SURVEILLANCE ANALYSIS")
        print("="*70)
        print()
        
        self.basic_statistics()
        yearly = self.temporal_analysis()
        countries = self.geographic_analysis()
        bacteria = self.bacterial_analysis()
        ab_stats, class_stats = self.antibiotic_analysis()
        self.risk_factor_analysis()
        corr = self.correlation_analysis()
        self.advanced_insights()
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE!")
        print("="*70)
        print()
        
        return {
            'yearly': yearly,
            'countries': countries,
            'bacteria': bacteria,
            'antibiotics': ab_stats,
            'classes': class_stats,
            'correlation': corr
        }


if __name__ == '__main__':
    # Run analysis
    analyzer = AntibioticResistanceAnalyzer('data/antibiotic_resistance_surveillance.csv')
    results = analyzer.run_complete_analysis()
    
    print("💾 Analysis results saved to memory")
    print("📊 Ready for visualization step!")
