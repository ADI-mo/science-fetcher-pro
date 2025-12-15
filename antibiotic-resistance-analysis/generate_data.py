"""
🦠 Generate Synthetic Antibiotic Resistance Surveillance Data
Simulates realistic patterns of antimicrobial resistance across countries and time
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)


def generate_resistance_data(n_records=10000):
    """Generate comprehensive antibiotic resistance surveillance dataset"""
    
    countries = ['USA', 'UK', 'Germany', 'France', 'Japan', 'India', 'Brazil', 
                 'South Africa', 'Australia', 'Canada', 'China', 'Mexico']
    
    bacteria_species = {
        'Escherichia coli': ['Gram-negative', 'Rod'],
        'Staphylococcus aureus': ['Gram-positive', 'Cocci'],
        'Klebsiella pneumoniae': ['Gram-negative', 'Rod'],
        'Pseudomonas aeruginosa': ['Gram-negative', 'Rod'],
        'Acinetobacter baumannii': ['Gram-negative', 'Rod'],
        'Enterococcus faecium': ['Gram-positive', 'Cocci'],
    }
    
    antibiotics = {
        'Penicillin': 'Beta-lactam',
        'Ampicillin': 'Beta-lactam',
        'Ceftriaxone': 'Cephalosporin',
        'Meropenem': 'Carbapenem',
        'Ciprofloxacin': 'Fluoroquinolone',
        'Gentamicin': 'Aminoglycoside',
        'Vancomycin': 'Glycopeptide',
        'Colistin': 'Polymyxin',
        'Azithromycin': 'Macrolide'
    }
    
    sample_sources = ['Blood', 'Urine', 'Wound', 'Respiratory', 'CSF', 'Stool']
    
    # Base resistance rates (%) - reflecting real-world patterns
    base_resistance = {
        'Escherichia coli': {
            'Ampicillin': 45, 'Ceftriaxone': 15, 'Ciprofloxacin': 25, 
            'Gentamicin': 12, 'Meropenem': 2
        },
        'Staphylococcus aureus': {
            'Penicillin': 85, 'Gentamicin': 20, 'Vancomycin': 1, 
            'Ciprofloxacin': 30
        },
        'Klebsiella pneumoniae': {
            'Ampicillin': 95, 'Ceftriaxone': 30, 'Ciprofloxacin': 35, 
            'Gentamicin': 18, 'Meropenem': 10
        },
        'Pseudomonas aeruginosa': {
            'Ciprofloxacin': 40, 'Gentamicin': 28, 'Meropenem': 18, 
            'Colistin': 4
        },
        'Acinetobacter baumannii': {
            'Ampicillin': 98, 'Ciprofloxacin': 75, 'Gentamicin': 65, 
            'Meropenem': 50, 'Colistin': 8
        },
        'Enterococcus faecium': {
            'Ampicillin': 80, 'Vancomycin': 15, 'Gentamicin': 45
        }
    }
    
    # Country development factor (affects resistance rates)
    country_factors = {
        'USA': 1.0, 'UK': 0.95, 'Germany': 0.88, 'France': 0.92, 'Japan': 0.82,
        'India': 1.45, 'Brazil': 1.35, 'South Africa': 1.40, 'Australia': 0.85,
        'Canada': 0.90, 'China': 1.30, 'Mexico': 1.25
    }
    
    data = []
    start_date = datetime(2015, 1, 1)
    
    for i in range(n_records):
        # Selections
        country = np.random.choice(countries)
        bacterium = np.random.choice(list(bacteria_species.keys()))
        
        # Get applicable antibiotics for this bacterium
        applicable_abs = list(base_resistance[bacterium].keys())
        antibiotic = np.random.choice(applicable_abs)
        
        # Date and year
        days_offset = np.random.randint(0, 365 * 10)
        sample_date = start_date + timedelta(days=days_offset)
        year = sample_date.year
        
        # Calculate resistance probability
        base_rate = base_resistance[bacterium][antibiotic]
        country_mod = country_factors[country]
        year_trend = (year - 2015) * 1.8  # Increasing trend over years
        
        # Source-specific modifiers (blood infections often more resistant)
        sample_source = np.random.choice(sample_sources)
        source_mod = 1.15 if sample_source == 'Blood' else 1.0
        
        resistance_rate = base_rate * country_mod * source_mod + year_trend
        resistance_rate += np.random.normal(0, 8)  # Add noise
        resistance_rate = np.clip(resistance_rate, 0, 99)
        
        # Determine resistance
        is_resistant = np.random.random() < (resistance_rate / 100)
        
        # Patient demographics
        patient_age = int(np.abs(np.random.normal(55, 25)))
        patient_age = np.clip(patient_age, 0, 100)
        
        # Hospital outcomes
        if is_resistant:
            hospital_days = int(np.random.exponential(10) + 5)
            mortality = np.random.random() < 0.15
        else:
            hospital_days = int(np.random.exponential(6) + 2)
            mortality = np.random.random() < 0.05
        
        hospital_days = min(hospital_days, 90)
        
        # Bacterial characteristics
        gram_stain, morphology = bacteria_species[bacterium]
        antibiotic_class = antibiotics[antibiotic]
        
        data.append({
            'Sample_ID': f'AMR{i+1:06d}',
            'Country': country,
            'Date': sample_date.strftime('%Y-%m-%d'),
            'Year': year,
            'Quarter': f'Q{(sample_date.month-1)//3 + 1}',
            'Bacterium': bacterium,
            'Gram_Stain': gram_stain,
            'Morphology': morphology,
            'Antibiotic': antibiotic,
            'Antibiotic_Class': antibiotic_class,
            'Sample_Source': sample_source,
            'Is_Resistant': is_resistant,
            'Resistance_Rate_Percent': round(resistance_rate, 2),
            'Patient_Age': patient_age,
            'Hospital_Stay_Days': hospital_days,
            'Patient_Died': mortality
        })
    
    df = pd.DataFrame(data)
    
    # Add some derived features
    df['Age_Group'] = pd.cut(df['Patient_Age'], 
                               bins=[0, 18, 45, 65, 100], 
                               labels=['Pediatric', 'Young Adult', 'Middle Age', 'Elderly'])
    
    return df


if __name__ == '__main__':
    print("="*70)
    print("🦠 GENERATING ANTIBIOTIC RESISTANCE SURVEILLANCE DATA")
    print("="*70)
    print()
    
    print("🔬 Simulating 10,000 bacterial isolate records...")
    print("   • 6 bacterial species")
    print("   • 9 antibiotic agents")
    print("   • 12 countries")
    print("   • 2015-2024 timeframe")
    print()
    
    df = generate_resistance_data(10000)
    
    # Save
    output_file = 'data/antibiotic_resistance_surveillance.csv'
    df.to_csv(output_file, index=False)
    
    print(f"✅ Generated {len(df):,} records")
    print(f"💾 Saved to: {output_file}")
    print()
    print("📊 DATASET PREVIEW:")
    print("="*70)
    print(df.head(10).to_string(index=False))
    print()
    print("📈 SUMMARY STATISTICS:")
    print("="*70)
    print(f"Overall resistance rate: {df['Is_Resistant'].mean()*100:.1f}%")
    print(f"Average hospital stay: {df['Hospital_Stay_Days'].mean():.1f} days")
    print(f"Mortality rate: {df['Patient_Died'].mean()*100:.1f}%")
    print()
    print(f"Resistance by bacterium:")
    print(df.groupby('Bacterium')['Is_Resistant'].mean().sort_values(ascending=False).apply(lambda x: f"{x*100:.1f}%"))
    print()
    print("🎉 Data generation complete!")
