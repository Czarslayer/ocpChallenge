"""
Downtime and operational state analysis
Identifies shutdowns, startups, and active periods for each GTA
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from data_loader import EnergyDataLoader
from config import CONSTRAINTS, GTA_COLUMNS, FIGURES_PATH
import os

sns.set_style("whitegrid")


class DowntimeAnalyzer:
    """Analyze downtime and operational states for GTAs"""

    def __init__(self, low_threshold=10):
        """
        Parameters:
        -----------
        low_threshold : float
            HP admission below this is considered "down" (tons/hour)
        """
        self.loader = EnergyDataLoader()
        self.data = self.loader.load_data()
        self.low_threshold = low_threshold

    def detect_operational_states(self):
        """Classify each timestamp as operational or down for each GTA"""

        states = pd.DataFrame(index=self.data.index)

        for gta_name, columns in GTA_COLUMNS.items():
            hp_col = columns[0]

            # Consider GTA "operational" if HP > threshold
            states[f'{gta_name}_operational'] = self.data[hp_col] > self.low_threshold
            states[f'{gta_name}_HP'] = self.data[hp_col]

        return states

    def calculate_uptime_statistics(self):
        """Calculate uptime percentages for each GTA"""

        states = self.detect_operational_states()
        total_records = len(states)

        print("\n" + "="*70)
        print("OPERATIONAL UPTIME ANALYSIS")
        print("="*70)
        print(f"\nThreshold for 'operational': HP > {self.low_threshold} tons/hour")
        print(f"Total time period: {total_records:,} records (15-min intervals)")
        print(f"Duration: {total_records * 15 / 60 / 24:.1f} days")
        print()

        uptime_stats = {}

        for gta_name in GTA_COLUMNS.keys():
            operational_col = f'{gta_name}_operational'

            operational_count = states[operational_col].sum()
            downtime_count = (~states[operational_col]).sum()

            uptime_pct = (operational_count / total_records) * 100
            downtime_pct = (downtime_count / total_records) * 100

            uptime_stats[gta_name] = {
                'operational_records': operational_count,
                'downtime_records': downtime_count,
                'uptime_pct': uptime_pct,
                'downtime_pct': downtime_pct,
                'operational_days': operational_count * 15 / 60 / 24,
                'downtime_days': downtime_count * 15 / 60 / 24
            }

            print(f"{gta_name}:")
            print(f"  Operational: {operational_count:,} records ({uptime_pct:.1f}%)")
            print(f"               {uptime_stats[gta_name]['operational_days']:.1f} days")
            print(f"  Downtime:    {downtime_count:,} records ({downtime_pct:.1f}%)")
            print(f"               {uptime_stats[gta_name]['downtime_days']:.1f} days")
            print()

        print("="*70)

        return uptime_stats, states

    def plot_operational_timeline(self):
        """Visualize operational states over time"""

        states = self.detect_operational_states()

        fig, axes = plt.subplots(3, 1, figsize=(16, 10))
        fig.suptitle(f'GTA Operational States Timeline (HP > {self.low_threshold} t/h = Operational)',
                     fontsize=16, fontweight='bold')

        for idx, gta_name in enumerate(GTA_COLUMNS.keys()):
            operational_col = f'{gta_name}_operational'
            hp_col = f'{gta_name}_HP'

            # Plot HP values
            axes[idx].plot(states.index, states[hp_col], linewidth=0.5, alpha=0.7, color='blue')

            # Highlight operational periods
            axes[idx].fill_between(states.index, 0, states[hp_col],
                                  where=states[operational_col],
                                  alpha=0.3, color='green', label='Operational')

            # Highlight downtime periods
            axes[idx].fill_between(states.index, 0, states[hp_col],
                                  where=~states[operational_col],
                                  alpha=0.3, color='red', label='Downtime')

            # Add threshold line
            axes[idx].axhline(y=self.low_threshold, color='orange', linestyle='--',
                            linewidth=2, label=f'Threshold ({self.low_threshold} t/h)')

            uptime_pct = (states[operational_col].sum() / len(states)) * 100
            axes[idx].set_title(f'{gta_name} - Uptime: {uptime_pct:.1f}%', fontsize=12)
            axes[idx].set_ylabel('HP Steam (tons/h)')
            axes[idx].legend(loc='upper right')
            axes[idx].grid(True, alpha=0.3)

        axes[-1].set_xlabel('Date')
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}operational_timeline.png", dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_PATH}operational_timeline.png")
        plt.close()

    def analyze_correlation_operational_only(self):
        """Recalculate correlations using only operational periods"""

        states = self.detect_operational_states()

        print("\n" + "="*70)
        print("CORRELATION ANALYSIS - OPERATIONAL PERIODS ONLY")
        print("="*70)
        print(f"(Excluding periods where HP < {self.low_threshold} tons/hour)")
        print()

        for gta_name, columns in GTA_COLUMNS.items():
            hp_col, mp_col, ee_col = columns
            operational_col = f'{gta_name}_operational'

            # Filter to operational periods only
            operational_mask = states[operational_col]
            operational_data = self.data[operational_mask].copy()

            if len(operational_data) == 0:
                print(f"{gta_name}: NO OPERATIONAL DATA")
                continue

            # Extract the three metrics
            df = pd.DataFrame({
                'HP_Admission': operational_data[hp_col],
                'MP_Extraction': operational_data[mp_col],
                'Energy_Production': operational_data[ee_col]
            })

            # Calculate correlations
            corr = df.corr()

            print(f"{gta_name} ({len(operational_data):,} operational records):")
            print(f"  HP ↔ MP:     {corr.loc['HP_Admission', 'MP_Extraction']:>7.3f}")
            print(f"  HP ↔ Energy: {corr.loc['HP_Admission', 'Energy_Production']:>7.3f}")
            print(f"  MP ↔ Energy: {corr.loc['MP_Extraction', 'Energy_Production']:>7.3f}")
            print()

        print("="*70)

    def plot_correlation_comparison(self):
        """Compare correlations: all data vs operational only"""

        states = self.detect_operational_states()

        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle('Correlation Comparison: All Data vs Operational Only',
                     fontsize=16, fontweight='bold')

        for idx, gta_name in enumerate(GTA_COLUMNS.keys()):
            hp_col, mp_col, ee_col = GTA_COLUMNS[gta_name]
            operational_col = f'{gta_name}_operational'

            # All data correlation
            all_data = pd.DataFrame({
                'HP': self.data[hp_col],
                'MP': self.data[mp_col],
                'Energy': self.data[ee_col]
            })
            corr_all = all_data.corr()

            # Operational only correlation
            operational_mask = states[operational_col]
            operational_data = self.data[operational_mask]

            op_data = pd.DataFrame({
                'HP': operational_data[hp_col],
                'MP': operational_data[mp_col],
                'Energy': operational_data[ee_col]
            })
            corr_op = op_data.corr()

            # Plot all data
            sns.heatmap(corr_all, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                       square=True, ax=axes[0, idx], cbar_kws={'shrink': 0.8},
                       vmin=-1, vmax=1)
            axes[0, idx].set_title(f'{gta_name}\nAll Data ({len(all_data):,} records)')

            # Plot operational only
            sns.heatmap(corr_op, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                       square=True, ax=axes[1, idx], cbar_kws={'shrink': 0.8},
                       vmin=-1, vmax=1)
            axes[1, idx].set_title(f'{gta_name}\nOperational Only ({len(op_data):,} records)')

        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}correlation_comparison.png", dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_PATH}correlation_comparison.png")
        plt.close()

    def identify_downtime_periods(self):
        """Identify continuous downtime periods"""

        states = self.detect_operational_states()

        print("\n" + "="*70)
        print("MAJOR DOWNTIME PERIODS (> 7 days continuous)")
        print("="*70)
        print()

        for gta_name in GTA_COLUMNS.keys():
            operational_col = f'{gta_name}_operational'

            # Find downtime periods
            is_down = ~states[operational_col]

            # Find start and end of downtime periods
            downtime_starts = is_down & ~is_down.shift(1, fill_value=False)
            downtime_ends = is_down & ~is_down.shift(-1, fill_value=False)

            starts = states.index[downtime_starts]
            ends = states.index[downtime_ends]

            # Calculate durations
            major_downtimes = []
            for start, end in zip(starts, ends):
                duration = (end - start).total_seconds() / 3600 / 24  # days
                if duration > 7:  # More than 7 days
                    major_downtimes.append({
                        'start': start,
                        'end': end,
                        'duration_days': duration
                    })

            print(f"{gta_name}: {len(major_downtimes)} major downtime periods")
            for i, dt in enumerate(major_downtimes[:5], 1):  # Show first 5
                print(f"  {i}. {dt['start']} to {dt['end']} ({dt['duration_days']:.1f} days)")
            if len(major_downtimes) > 5:
                print(f"  ... and {len(major_downtimes) - 5} more")
            print()

        print("="*70)

    def create_cleaned_dataset(self, save_path=None):
        """Create dataset with downtime periods removed and missing values handled"""

        states = self.detect_operational_states()

        print("\n" + "="*70)
        print("CREATING CLEANED DATASET")
        print("="*70)
        print()

        # Start with original data
        cleaned = self.data.copy()

        # Step 1: Remove rows where ALL GTAs are down
        all_down_mask = True
        for gta_name in GTA_COLUMNS.keys():
            operational_col = f'{gta_name}_operational'
            all_down_mask = all_down_mask & ~states[operational_col]

        rows_all_down = all_down_mask.sum()
        cleaned = cleaned[~all_down_mask]

        print(f"Step 1: Removed {rows_all_down:,} rows where all GTAs were down")
        print(f"        Remaining: {len(cleaned):,} records")
        print()

        # Step 2: For each GTA, set values to 0 when that GTA is down
        for gta_name, columns in GTA_COLUMNS.items():
            hp_col, mp_col, ee_col = columns
            operational_col = f'{gta_name}_operational'

            # Get downtime mask for indices that exist in cleaned data
            down_indices = states.index[~states[operational_col]]
            down_indices_in_cleaned = down_indices.intersection(cleaned.index)
            down_count = len(down_indices_in_cleaned)

            # Set to 0 when down (instead of removing rows)
            cleaned.loc[down_indices_in_cleaned, hp_col] = 0
            cleaned.loc[down_indices_in_cleaned, mp_col] = 0
            cleaned.loc[down_indices_in_cleaned, ee_col] = 0

            print(f"{gta_name}: Set {down_count:,} downtime records to 0")

        print()

        # Step 3: Handle missing values
        missing_before = cleaned.isnull().sum().sum()

        # Forward fill missing values (reasonable for time series)
        cleaned = cleaned.ffill()

        # If any still missing (at start), backward fill
        cleaned = cleaned.bfill()

        # If any STILL missing, fill with 0
        cleaned = cleaned.fillna(0)

        missing_after = cleaned.isnull().sum().sum()

        print(f"Step 3: Handled missing values")
        print(f"        Before: {missing_before} missing values")
        print(f"        After:  {missing_after} missing values")
        print()

        # Summary
        print(f"SUMMARY:")
        print(f"  Original dataset:  {len(self.data):,} records")
        print(f"  Cleaned dataset:   {len(cleaned):,} records")
        print(f"  Removed:           {len(self.data) - len(cleaned):,} records ({(len(self.data) - len(cleaned))/len(self.data)*100:.1f}%)")
        print()

        # Save if path provided
        if save_path:
            cleaned.to_csv(save_path)
            print(f"✓ Saved cleaned dataset to: {save_path}")

        print("="*70)

        return cleaned

    def run_full_analysis(self):
        """Run complete downtime analysis"""

        print("\n🔍 Running Downtime Analysis...\n")

        print("1. Calculating uptime statistics...")
        uptime_stats, states = self.calculate_uptime_statistics()

        print("\n2. Plotting operational timeline...")
        self.plot_operational_timeline()

        print("\n3. Identifying major downtime periods...")
        self.identify_downtime_periods()

        print("\n4. Analyzing correlations (operational only)...")
        self.analyze_correlation_operational_only()

        print("\n5. Creating correlation comparison plot...")
        self.plot_correlation_comparison()

        print("\n6. Creating cleaned dataset...")
        import os
        cleaned_path = os.path.join(os.path.dirname(self.loader.filepath),
                                   'Data_Energie_cleaned.csv')
        cleaned = self.create_cleaned_dataset(save_path=cleaned_path)

        print(f"\n✅ Downtime Analysis Complete!")

        return uptime_stats, cleaned


if __name__ == "__main__":
    # Run with threshold of 10 tons/hour
    analyzer = DowntimeAnalyzer(low_threshold=10)
    uptime_stats, cleaned_data = analyzer.run_full_analysis()
