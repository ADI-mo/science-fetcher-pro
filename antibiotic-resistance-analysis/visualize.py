"""
📊 VISUALIZATION MODULE
Create beautiful and insightful charts for antibiotic resistance data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# Enhanced plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("notebook", font_scale=1.1)
sns.set_palette("husl")


class ResistanceVisualizer:
    """Create comprehensive visualizations"""
    
    def __init__(self, data_path):
        """Load data"""
        self.df = pd.read_csv(data_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        print(f"📊 Visualizer initialized with {len(self.df):,} records")
        
    def plot_temporal_trends(self, save_path='outputs/temporal_trends.png'):
        """Plot resistance trends over time"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('🕐 Temporal Trends in Antibiotic Resistance', fontsize=18, fontweight='bold')
        
        # 1. Overall resistance by year
        yearly = self.df.groupby('Year')['Is_Resistant'].mean() * 100
        axes[0, 0].plot(yearly.index, yearly.values, marker='o', linewidth=3, markersize=10, color='#e74c3c')
        axes[0, 0].fill_between(yearly.index, yearly.values, alpha=0.3, color='#e74c3c')
        axes[0, 0].set_title('Overall Resistance Rate Over Time', fontweight='bold', fontsize=14)
        axes[0, 0].set_xlabel('Year', fontsize=12)
        axes[0, 0].set_ylabel('Resistance Rate (%)', fontsize=12)
        axes[0, 0].grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(yearly.index, yearly.values, 1)
        p = np.poly1d(z)
        axes[0, 0].plot(yearly.index, p(yearly.index), "--", alpha=0.7, linewidth=2, label=f'Trend: {z[0]:+.2f}%/year')
        axes[0, 0].legend()
        
        # 2. Resistance by bacterial species over time
        for bacterium in self.df['Bacterium'].unique():
            subset = self.df[self.df['Bacterium'] == bacterium]
            yearly_bac = subset.groupby('Year')['Is_Resistant'].mean() * 100
            axes[0, 1].plot(yearly_bac.index, yearly_bac.values, marker='o', label=bacterium.split()[0], linewidth=2)
        
        axes[0, 1].set_title('Resistance Trends by Bacterial Species', fontweight='bold', fontsize=14)
        axes[0, 1].set_xlabel('Year', fontsize=12)
        axes[0, 1].set_ylabel('Resistance Rate (%)', fontsize=12)
        axes[0, 1].legend(loc='best', fontsize=9)
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Quarterly trends (recent years)
        recent = self.df[self.df['Year'] >= 2020].copy()
        recent['YearQuarter'] = recent['Year'].astype(str) + '-' + recent['Quarter']
        quarterly = recent.groupby('YearQuarter')['Is_Resistant'].mean() * 100
        
        axes[1, 0].bar(range(len(quarterly)), quarterly.values, color='#3498db', alpha=0.7)
        axes[1, 0].set_xticks(range(len(quarterly)))
        axes[1, 0].set_xticklabels(quarterly.index, rotation=45, ha='right', fontsize=9)
        axes[1, 0].set_title('Quarterly Resistance Rates (2020-2024)', fontweight='bold', fontsize=14)
        axes[1, 0].set_ylabel('Resistance Rate (%)', fontsize=12)
        axes[1, 0].grid(True, axis='y', alpha=0.3)
        
        # 4. Sample volume over time
        samples_per_year = self.df.groupby('Year').size()
        axes[1, 1].bar(samples_per_year.index, samples_per_year.values, color='#2ecc71', alpha=0.7)
        axes[1, 1].set_title('Sample Volume by Year', fontweight='bold', fontsize=14)
        axes[1, 1].set_xlabel('Year', fontsize=12)
        axes[1, 1].set_ylabel('Number of Samples', fontsize=12)
        axes[1, 1].grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")
        plt.close()
        
    def plot_geographic_heatmap(self, save_path='outputs/geographic_heatmap.png'):
        """Create geographic resistance heatmap"""
        fig, axes = plt.subplots(1, 2, figsize=(18, 6))
        fig.suptitle('🌍 Geographic Distribution of Antibiotic Resistance', fontsize=18, fontweight='bold')
        
        # 1. Resistance rate by country
        country_res = self.df.groupby('Country')['Is_Resistant'].mean() * 100
        country_res = country_res.sort_values(ascending=True)
        
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(country_res)))
        axes[0].barh(country_res.index, country_res.values, color=colors)
        axes[0].set_title('Resistance Rate by Country', fontweight='bold', fontsize=14)
        axes[0].set_xlabel('Resistance Rate (%)', fontsize=12)
        axes[0].axvline(country_res.mean(), color='red', linestyle='--', linewidth=2, label=f'Global Mean: {country_res.mean():.1f}%')
        axes[0].legend()
        axes[0].grid(True, axis='x', alpha=0.3)
        
        # 2. Heatmap: Country x Year
        pivot_data = self.df.groupby(['Country', 'Year'])['Is_Resistant'].mean().unstack() * 100
        
        sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='RdYlGn_r', 
                    cbar_kws={'label': 'Resistance Rate (%)'}, ax=axes[1],
                    linewidths=0.5, linecolor='gray')
        axes[1].set_title('Resistance Rate: Country × Year', fontweight='bold', fontsize=14)
        axes[1].set_xlabel('Year', fontsize=12)
        axes[1].set_ylabel('Country', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")
        plt.close()
        
    def plot_bacterial_analysis(self, save_path='outputs/bacterial_analysis.png'):
        """Visualize bacterial species patterns"""
        fig = plt.figure(figsize=(18, 10))
        gs = GridSpec(2, 3, figure=fig)
        fig.suptitle('🦠 Bacterial Species Analysis', fontsize=18, fontweight='bold')
        
        # 1. Resistance by species
        ax1 = fig.add_subplot(gs[0, 0])
        species_res = self.df.groupby('Bacterium')['Is_Resistant'].mean() * 100
        species_res = species_res.sort_values(ascending=True)
        ax1.barh(species_res.index, species_res.values, color='#e74c3c', alpha=0.7)
        ax1.set_xlabel('Resistance Rate (%)')
        ax1.set_title('Resistance by Species', fontweight='bold')
        ax1.grid(True, axis='x', alpha=0.3)
        
        # 2. Sample distribution
        ax2 = fig.add_subplot(gs[0, 1])
        species_count = self.df['Bacterium'].value_counts()
        ax2.pie(species_count.values, labels=species_count.index, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Sample Distribution by Species', fontweight='bold')
        
        # 3. Mortality by species
        ax3 = fig.add_subplot(gs[0, 2])
        species_mort = self.df.groupby('Bacterium')['Patient_Died'].mean() * 100
        species_mort = species_mort.sort_values(ascending=False)
        ax3.bar(range(len(species_mort)), species_mort.values, color='#9b59b6', alpha=0.7)
        ax3.set_xticks(range(len(species_mort)))
        ax3.set_xticklabels([s.split()[0] for s in species_mort.index], rotation=45, ha='right')
        ax3.set_ylabel('Mortality Rate (%)')
        ax3.set_title('Mortality by Species', fontweight='bold')
        ax3.grid(True, axis='y', alpha=0.3)
        
        # 4. Hospital stay comparison
        ax4 = fig.add_subplot(gs[1, :])
        species_stay = []
        species_names = []
        for species in self.df['Bacterium'].unique():
            resistant = self.df[(self.df['Bacterium']==species) & (self.df['Is_Resistant']==True)]['Hospital_Stay_Days']
            susceptible = self.df[(self.df['Bacterium']==species) & (self.df['Is_Resistant']==False)]['Hospital_Stay_Days']
            species_stay.append([susceptible.values, resistant.values])
            species_names.append(species.split()[0])
        
        positions = np.arange(len(species_names)) * 3
        bp1 = ax4.boxplot([s[0] for s in species_stay], positions=positions-0.6, widths=0.5, 
                          patch_artist=True, boxprops=dict(facecolor='#2ecc71', alpha=0.7),
                          medianprops=dict(color='black', linewidth=2))
        bp2 = ax4.boxplot([s[1] for s in species_stay], positions=positions+0.6, widths=0.5,
                          patch_artist=True, boxprops=dict(facecolor='#e74c3c', alpha=0.7),
                          medianprops=dict(color='black', linewidth=2))
        
        ax4.set_xticks(positions)
        ax4.set_xticklabels(species_names)
        ax4.set_ylabel('Hospital Stay (days)')
        ax4.set_title('Hospital Stay Duration: Susceptible vs Resistant', fontweight='bold')
        ax4.legend([bp1["boxes"][0], bp2["boxes"][0]], ['Susceptible', 'Resistant'], loc='upper right')
        ax4.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")
        plt.close()
        
    def plot_antibiotic_analysis(self, save_path='outputs/antibiotic_analysis.png'):
        """Visualize antibiotic effectiveness"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('💊 Antibiotic Effectiveness Analysis', fontsize=18, fontweight='bold')
        
        # 1. Resistance by antibiotic
        ab_res = self.df.groupby('Antibiotic')['Is_Resistant'].mean() * 100
        ab_res = ab_res.sort_values(ascending=False)
        
        colors_ab = ['#e74c3c' if x > 50 else '#f39c12' if x > 30 else '#2ecc71' for x in ab_res.values]
        axes[0, 0].bar(range(len(ab_res)), ab_res.values, color=colors_ab, alpha=0.7)
        axes[0, 0].set_xticks(range(len(ab_res)))
        axes[0, 0].set_xticklabels(ab_res.index, rotation=45, ha='right')
        axes[0, 0].set_ylabel('Resistance Rate (%)')
        axes[0, 0].set_title('Resistance Rate by Antibiotic', fontweight='bold')
        axes[0, 0].axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% threshold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, axis='y', alpha=0.3)
        
        # 2. Resistance by antibiotic class
        class_res = self.df.groupby('Antibiotic_Class')['Is_Resistant'].mean() * 100
        class_res = class_res.sort_values(ascending=True)
        
        axes[0, 1].barh(class_res.index, class_res.values, color='#3498db', alpha=0.7)
        axes[0, 1].set_xlabel('Resistance Rate (%)')
        axes[0, 1].set_title('Resistance by Antibiotic Class', fontweight='bold')
        axes[0, 1].grid(True, axis='x', alpha=0.3)
        
        # 3. Heatmap: Bacterium x Antibiotic
        # Get top combinations
        combo_data = self.df.groupby(['Bacterium', 'Antibiotic']).agg({
            'Is_Resistant': 'mean',
            'Sample_ID': 'count'
        })
        combo_data = combo_data[combo_data['Sample_ID'] >= 50]  # Filter for sufficient samples
        pivot = combo_data['Is_Resistant'].unstack() * 100
        
        sns.heatmap(pivot, annot=True, fmt='.0f', cmap='RdYlGn_r', 
                    cbar_kws={'label': 'Resistance Rate (%)'}, ax=axes[1, 0],
                    linewidths=0.5, linecolor='gray')
        axes[1, 0].set_title('Resistance Matrix: Bacterium × Antibiotic', fontweight='bold')
        axes[1, 0].set_xlabel('Antibiotic')
        axes[1, 0].set_ylabel('Bacterium')
        
        # 4. Temporal trends for critical antibiotics
        critical_abs = ['Meropenem', 'Vancomycin', 'Colistin']
        for ab in critical_abs:
            if ab in self.df['Antibiotic'].values:
                subset = self.df[self.df['Antibiotic'] == ab]
                yearly = subset.groupby('Year')['Is_Resistant'].mean() * 100
                axes[1, 1].plot(yearly.index, yearly.values, marker='o', label=ab, linewidth=2, markersize=8)
        
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Resistance Rate (%)')
        axes[1, 1].set_title('Trends in Critical Last-Resort Antibiotics', fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")
        plt.close()
        
    def plot_clinical_outcomes(self, save_path='outputs/clinical_outcomes.png'):
        """Visualize clinical outcomes"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('🏥 Clinical Outcomes Analysis', fontsize=18, fontweight='bold')
        
        # 1. Hospital stay: Resistant vs Susceptible
        resistant_stay = self.df[self.df['Is_Resistant']==True]['Hospital_Stay_Days']
        susceptible_stay = self.df[self.df['Is_Resistant']==False]['Hospital_Stay_Days']
        
        axes[0, 0].hist([susceptible_stay, resistant_stay], bins=30, label=['Susceptible', 'Resistant'],
                       color=['#2ecc71', '#e74c3c'], alpha=0.6)
        axes[0, 0].set_xlabel('Hospital Stay (days)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Hospital Stay Distribution', fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].axvline(susceptible_stay.mean(), color='#2ecc71', linestyle='--', linewidth=2)
        axes[0, 0].axvline(resistant_stay.mean(), color='#e74c3c', linestyle='--', linewidth=2)
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Mortality by resistance status
        mort_data = self.df.groupby('Is_Resistant')['Patient_Died'].mean() * 100
        axes[0, 1].bar(['Susceptible', 'Resistant'], mort_data.values, 
                      color=['#2ecc71', '#e74c3c'], alpha=0.7, width=0.6)
        axes[0, 1].set_ylabel('Mortality Rate (%)')
        axes[0, 1].set_title('Mortality: Resistant vs Susceptible', fontweight='bold')
        axes[0, 1].grid(True, axis='y', alpha=0.3)
        
        # Add values on bars
        for i, v in enumerate(mort_data.values):
            axes[0, 1].text(i, v + 0.5, f'{v:.1f}%', ha='center', fontweight='bold')
        
        # 3. Age distribution by resistance
        age_bins = [0, 18, 45, 65, 100]
        age_labels = ['<18', '18-45', '45-65', '65+']
        
        age_res = []
        for i in range(len(age_bins)-1):
            mask = (self.df['Patient_Age'] >= age_bins[i]) & (self.df['Patient_Age'] < age_bins[i+1])
            age_res.append(self.df[mask]['Is_Resistant'].mean() * 100)
        
        axes[1, 0].bar(age_labels, age_res, color='#9b59b6', alpha=0.7)
        axes[1, 0].set_xlabel('Age Group')
        axes[1, 0].set_ylabel('Resistance Rate (%)')
        axes[1, 0].set_title('Resistance by Age Group', fontweight='bold')
        axes[1, 0].grid(True, axis='y', alpha=0.3)
        
        # 4. Sample source analysis
        source_data = self.df.groupby('Sample_Source').agg({
            'Is_Resistant': 'mean',
            'Patient_Died': 'mean'
        }) * 100
        
        x = np.arange(len(source_data))
        width = 0.35
        
        axes[1, 1].bar(x - width/2, source_data['Is_Resistant'], width, 
                      label='Resistance Rate', color='#e74c3c', alpha=0.7)
        axes[1, 1].bar(x + width/2, source_data['Patient_Died'], width,
                      label='Mortality Rate', color='#34495e', alpha=0.7)
        
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(source_data.index, rotation=45, ha='right')
        axes[1, 1].set_ylabel('Rate (%)')
        axes[1, 1].set_title('Outcomes by Sample Source', fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")
        plt.close()
        
    def plot_correlation_matrix(self, save_path='outputs/correlation_matrix.png'):
        """Create correlation heatmap"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Select numeric variables
        numeric_cols = ['Patient_Age', 'Hospital_Stay_Days', 'Is_Resistant', 'Patient_Died']
        corr_matrix = self.df[numeric_cols].corr()
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(corr_matrix), k=1)
        
        sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   mask=mask, ax=ax, vmin=-1, vmax=1)
        
        ax.set_title('🔗 Correlation Matrix: Key Variables', fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")
        plt.close()
        
    def create_all_visualizations(self):
        """Generate all visualizations"""
        print("\n" + "="*70)
        print("📊 GENERATING VISUALIZATIONS")
        print("="*70)
        print()
        
        self.plot_temporal_trends()
        self.plot_geographic_heatmap()
        self.plot_bacterial_analysis()
        self.plot_antibiotic_analysis()
        self.plot_clinical_outcomes()
        self.plot_correlation_matrix()
        
        print()
        print("="*70)
        print("✅ ALL VISUALIZATIONS COMPLETE!")
        print("="*70)
        print("📁 Check the 'outputs/' folder for all generated charts")


if __name__ == '__main__':
    viz = ResistanceVisualizer('data/antibiotic_resistance_surveillance.csv')
    viz.create_all_visualizations()
