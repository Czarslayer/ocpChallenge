"""
Split data into separate CSV files per GTA
For GTA_2, remove downtime periods entirely
"""

import pandas as pd
import os
from data_loader import EnergyDataLoader
from config import GTA_COLUMNS, BASE_DIR
from downtime_analysis import DowntimeAnalyzer


def split_gta_data(low_threshold=10):
    """
    Create separate CSV files for each GTA
    For GTA_2: Remove downtime periods
    For GTA_1 and GTA_3: Keep all data but mark operational state
    """

    print("\n" + "="*70)
    print("SPLITTING GTA DATA INTO SEPARATE FILES")
    print("="*70)
    print()

    # Load data
    loader = EnergyDataLoader()
    data = loader.load_data()

    # Get operational states
    analyzer = DowntimeAnalyzer(low_threshold=low_threshold)
    states = analyzer.detect_operational_states()

    # Create output directory
    output_dir = os.path.join(BASE_DIR, 'data', 'gta_individual')
    os.makedirs(output_dir, exist_ok=True)

    print(f"Output directory: {output_dir}\n")

    # Process each GTA
    for gta_name, columns in GTA_COLUMNS.items():
        hp_col, mp_col, ee_col = columns
        operational_col = f'{gta_name}_operational'

        print(f"Processing {gta_name}...")

        # Create DataFrame for this GTA
        gta_df = pd.DataFrame(index=data.index)
        gta_df['Date'] = data.index
        gta_df['HP_Admission'] = data[hp_col]
        gta_df['MP_Extraction'] = data[mp_col]
        gta_df['Energy_Production'] = data[ee_col]
        gta_df['Operational'] = states[operational_col]

        # Statistics before filtering
        total_records = len(gta_df)
        operational_records = gta_df['Operational'].sum()
        downtime_records = (~gta_df['Operational']).sum()

        print(f"  Total records: {total_records:,}")
        print(f"  Operational: {operational_records:,} ({operational_records/total_records*100:.1f}%)")
        print(f"  Downtime: {downtime_records:,} ({downtime_records/total_records*100:.1f}%)")

        # Special handling for GTA_2: Remove downtime
        if gta_name == 'GTA_2':
            print(f"  → Removing downtime periods for {gta_name}")
            gta_df_filtered = gta_df[gta_df['Operational']].copy()
            gta_df_filtered = gta_df_filtered.drop(columns=['Operational'])

            # Save filtered version
            output_path = os.path.join(output_dir, f'{gta_name}_operational_only.csv')
            gta_df_filtered.to_csv(output_path, index=False)
            print(f"  ✓ Saved: {output_path}")
            print(f"    Records: {len(gta_df_filtered):,} (downtime removed)")

            # Also save full version with operational flag for reference
            output_path_full = os.path.join(output_dir, f'{gta_name}_full.csv')
            gta_df.to_csv(output_path_full, index=False)
            print(f"  ✓ Saved: {output_path_full}")
            print(f"    Records: {len(gta_df):,} (includes downtime)")

        else:
            # For GTA_1 and GTA_3: Keep all data
            gta_df = gta_df.drop(columns=['Operational'])
            output_path = os.path.join(output_dir, f'{gta_name}.csv')
            gta_df.to_csv(output_path, index=False)
            print(f"  ✓ Saved: {output_path}")
            print(f"    Records: {len(gta_df):,}")

        print()

    # Create a combined operational-only dataset (all 3 GTAs, operational only)
    print("Creating combined operational-only dataset...")

    combined_operational = pd.DataFrame(index=data.index)
    combined_operational['Date'] = data.index

    for gta_name, columns in GTA_COLUMNS.items():
        hp_col, mp_col, ee_col = columns
        operational_col = f'{gta_name}_operational'

        # Get operational mask
        operational_mask = states[operational_col]

        # Create columns with operational values only (0 when down)
        combined_operational[f'{gta_name}_HP_Admission'] = data[hp_col].where(operational_mask, 0)
        combined_operational[f'{gta_name}_MP_Extraction'] = data[mp_col].where(operational_mask, 0)
        combined_operational[f'{gta_name}_Energy_Production'] = data[ee_col].where(operational_mask, 0)
        combined_operational[f'{gta_name}_Operational'] = operational_mask

    # Remove rows where ALL GTAs are down
    all_down = True
    for gta_name in GTA_COLUMNS.keys():
        all_down = all_down & ~combined_operational[f'{gta_name}_Operational']

    combined_operational = combined_operational[~all_down]

    output_path = os.path.join(output_dir, 'all_gtas_operational.csv')
    combined_operational.to_csv(output_path, index=False)
    print(f"✓ Saved: {output_path}")
    print(f"  Records: {len(combined_operational):,}")
    print(f"  Removed: {all_down.sum():,} rows where all GTAs were down")
    print()

    # Create summary statistics file
    print("Creating summary statistics...")

    summary = []
    for gta_name, columns in GTA_COLUMNS.items():
        hp_col, mp_col, ee_col = columns
        operational_col = f'{gta_name}_operational'

        # Get operational data only
        operational_mask = states[operational_col]
        operational_data = data[operational_mask]

        stats = {
            'GTA': gta_name,
            'Total_Records': len(data),
            'Operational_Records': operational_mask.sum(),
            'Downtime_Records': (~operational_mask).sum(),
            'Uptime_Percentage': (operational_mask.sum() / len(data)) * 100,
            'Avg_HP_Operational': operational_data[hp_col].mean(),
            'Avg_MP_Operational': operational_data[mp_col].mean(),
            'Avg_Energy_Operational': operational_data[ee_col].mean(),
            'Max_HP': operational_data[hp_col].max(),
            'Max_MP': operational_data[mp_col].max(),
            'Max_Energy': operational_data[ee_col].max(),
            'Min_HP': operational_data[hp_col].min(),
            'Min_MP': operational_data[mp_col].min(),
            'Min_Energy': operational_data[ee_col].min(),
        }
        summary.append(stats)

    summary_df = pd.DataFrame(summary)
    summary_path = os.path.join(output_dir, 'gta_summary_statistics.csv')
    summary_df.to_csv(summary_path, index=False)
    print(f"✓ Saved: {summary_path}")
    print()

    print("="*70)
    print("SUMMARY OF CREATED FILES")
    print("="*70)
    print(f"\nIndividual GTA files:")
    print(f"  • GTA_1.csv - Full data (98.4% operational)")
    print(f"  • GTA_2_operational_only.csv - Downtime removed (61.5% → 100% operational)")
    print(f"  • GTA_2_full.csv - Full data including downtime (for reference)")
    print(f"  • GTA_3.csv - Full data (92.8% operational)")
    print(f"\nCombined files:")
    print(f"  • all_gtas_operational.csv - All GTAs, operational values only")
    print(f"  • gta_summary_statistics.csv - Statistical summary")
    print(f"\nLocation: {output_dir}")
    print("="*70)

    return output_dir


if __name__ == "__main__":
    output_dir = split_gta_data(low_threshold=10)

    # List all created files
    print("\nCreated files:")
    for filename in sorted(os.listdir(output_dir)):
        if filename.endswith('.csv'):
            filepath = os.path.join(output_dir, filename)
            file_size = os.path.getsize(filepath) / 1024  # KB
            print(f"  {filename:<40} ({file_size:>8.1f} KB)")
