"""
Anomaly detection and analysis for OCP Energy Data
Helps determine if anomalies should be removed or kept
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from data_loader import EnergyDataLoader
from config import CONSTRAINTS, GTA_COLUMNS, FIGURES_PATH
import os

sns.set_style("whitegrid")


class AnomalyAnalyzer:
    """Analyze and visualize anomalies in the energy data"""

    def __init__(self):
        self.loader = EnergyDataLoader()
        self.data = self.loader.load_data()
        self.totals = self.loader.calculate_system_totals()
        os.makedirs(FIGURES_PATH, exist_ok=True)

    def detect_anomalies_by_constraints(self):
        """Detect anomalies based on stated constraints"""
        anomaly_report = {}

        for gta_name, columns in GTA_COLUMNS.items():
            hp_col, mp_col, ee_col = columns

            # Find constraint violations
            hp_above_max = self.data[hp_col] > CONSTRAINTS['max_hp_steam_input']
            hp_below_min = self.data[hp_col] < CONSTRAINTS['min_steam_requirement']
            mp_above_max = self.data[mp_col] > CONSTRAINTS['max_mp_steam_extraction']
            ee_above_max = self.data[ee_col] > CONSTRAINTS['max_energy_production']

            # Near-zero values (likely shutdowns)
            hp_near_zero = self.data[hp_col] < 10
            mp_near_zero = self.data[mp_col] < 10

            anomaly_report[gta_name] = {
                'hp_above_max': hp_above_max.sum(),
                'hp_below_min': hp_below_min.sum(),
                'mp_above_max': mp_above_max.sum(),
                'ee_above_max': ee_above_max.sum(),
                'hp_near_zero': hp_near_zero.sum(),
                'mp_near_zero': mp_near_zero.sum(),
                'hp_violations_mask': hp_above_max | hp_below_min,
                'mp_violations_mask': mp_above_max,
            }

        return anomaly_report

    def analyze_temporal_distribution(self):
        """Check when anomalies occur - are they clustered or random?"""
        print("\n" + "="*70)
        print("TEMPORAL DISTRIBUTION OF ANOMALIES")
        print("="*70)

        for gta_name, columns in GTA_COLUMNS.items():
            hp_col, mp_col, ee_col = columns

            # MP anomalies (most significant)
            mp_violations = self.data[mp_col] > CONSTRAINTS['max_mp_steam_extraction']

            if mp_violations.sum() > 0:
                violation_data = self.data[mp_violations]

                print(f"\n{gta_name} - MP Steam Violations:")
                print(f"  Total violations: {mp_violations.sum():,} / {len(self.data):,} ({mp_violations.sum()/len(self.data)*100:.1f}%)")
                print(f"  Date range: {violation_data.index.min()} to {violation_data.index.max()}")
                print(f"  Max value: {self.data[mp_col].max():.2f} tons/hour")

                # Check if violations are continuous
                violation_dates = violation_data.index.to_series()
                gaps = violation_dates.diff()
                continuous_periods = (gaps <= pd.Timedelta(minutes=15)).sum()
                print(f"  Continuous violations: {continuous_periods:,} ({continuous_periods/len(violation_dates)*100:.1f}%)")

        print("\n" + "="*70)

    def plot_anomaly_timeline(self):
        """Visualize when anomalies occur over time"""
        fig, axes = plt.subplots(3, 1, figsize=(16, 10))
        fig.suptitle('Anomaly Timeline - MP Steam Extraction', fontsize=16, fontweight='bold')

        for idx, (gta_name, columns) in enumerate(GTA_COLUMNS.items()):
            mp_col = columns[1]

            # Plot full data
            axes[idx].plot(self.data.index, self.data[mp_col], alpha=0.5, linewidth=0.5, label='Actual')

            # Highlight constraint line
            axes[idx].axhline(y=CONSTRAINTS['max_mp_steam_extraction'],
                             color='red', linestyle='--', linewidth=2, label='Constraint (100 t/h)')

            # Highlight violations
            violations = self.data[self.data[mp_col] > CONSTRAINTS['max_mp_steam_extraction']]
            axes[idx].scatter(violations.index, violations[mp_col],
                            color='red', s=5, alpha=0.7, label='Violations')

            axes[idx].set_ylabel('MP Steam (tons/h)')
            axes[idx].set_title(f'{gta_name}')
            axes[idx].legend(loc='upper right')
            axes[idx].grid(True, alpha=0.3)

        axes[-1].set_xlabel('Date')
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}anomaly_timeline.png", dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_PATH}anomaly_timeline.png")
        plt.close()

    def plot_anomaly_zoom(self):
        """Zoom into anomaly periods to see patterns"""
        fig, axes = plt.subplots(3, 1, figsize=(16, 10))
        fig.suptitle('Anomaly Detail View - MP Steam Extraction', fontsize=16, fontweight='bold')

        for idx, (gta_name, columns) in enumerate(GTA_COLUMNS.items()):
            mp_col = columns[1]

            # Find first major violation period
            violations = self.data[self.data[mp_col] > CONSTRAINTS['max_mp_steam_extraction']]

            if len(violations) > 0:
                # Get a window around first violation
                first_violation = violations.index[0]
                start = max(first_violation - pd.Timedelta(days=7), self.data.index.min())
                end = min(first_violation + pd.Timedelta(days=7), self.data.index.max())

                window_data = self.data.loc[start:end]

                axes[idx].plot(window_data.index, window_data[mp_col], linewidth=1)
                axes[idx].axhline(y=CONSTRAINTS['max_mp_steam_extraction'],
                                 color='red', linestyle='--', linewidth=2, label='Constraint')
                axes[idx].fill_between(window_data.index,
                                      CONSTRAINTS['max_mp_steam_extraction'],
                                      window_data[mp_col],
                                      where=window_data[mp_col] > CONSTRAINTS['max_mp_steam_extraction'],
                                      alpha=0.3, color='red', label='Violation')

                axes[idx].set_ylabel('MP Steam (tons/h)')
                axes[idx].set_title(f'{gta_name} - Detail View (±7 days from first violation)')
                axes[idx].legend()
                axes[idx].grid(True, alpha=0.3)
            else:
                axes[idx].text(0.5, 0.5, 'No violations', ha='center', va='center',
                             transform=axes[idx].transAxes)

        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}anomaly_detail.png", dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_PATH}anomaly_detail.png")
        plt.close()

    def calculate_percentiles(self):
        """Calculate percentiles to understand data distribution"""
        print("\n" + "="*70)
        print("DATA DISTRIBUTION PERCENTILES")
        print("="*70)

        percentiles = [50, 75, 90, 95, 99, 99.5, 100]

        for gta_name, columns in GTA_COLUMNS.items():
            hp_col, mp_col, ee_col = columns

            print(f"\n{gta_name}:")
            print(f"  HP Steam Admission:")
            for p in percentiles:
                val = np.percentile(self.data[hp_col].dropna(), p)
                print(f"    {p}th percentile: {val:.2f} tons/hour")

            print(f"  MP Steam Extraction:")
            for p in percentiles:
                val = np.percentile(self.data[mp_col].dropna(), p)
                marker = " ⚠️ ABOVE CONSTRAINT" if val > CONSTRAINTS['max_mp_steam_extraction'] else ""
                print(f"    {p}th percentile: {val:.2f} tons/hour{marker}")

        print("\n" + "="*70)

    def recommend_cleaning_strategy(self):
        """Provide recommendation on whether to clean anomalies"""
        print("\n" + "="*70)
        print("ANOMALY CLEANING RECOMMENDATION")
        print("="*70)

        report = self.detect_anomalies_by_constraints()

        total_records = len(self.data)

        print("\nAnalyzing anomaly patterns...\n")

        for gta_name, metrics in report.items():
            mp_violations_pct = (metrics['mp_above_max'] / total_records) * 100
            hp_violations_pct = ((metrics['hp_above_max'] + metrics['hp_below_min']) / total_records) * 100

            print(f"{gta_name}:")
            print(f"  MP violations: {metrics['mp_above_max']:,} ({mp_violations_pct:.1f}%)")
            print(f"  HP violations: {metrics['hp_above_max'] + metrics['hp_below_min']:,} ({hp_violations_pct:.1f}%)")

        print("\n" + "-"*70)
        print("RECOMMENDATION:")
        print("-"*70)

        # Check if violations are > 5% of data
        high_violation_rate = any((report[gta]['mp_above_max'] / total_records) > 0.05
                                  for gta in GTA_COLUMNS.keys())

        if high_violation_rate:
            print("\n⚠️  HIGH ANOMALY RATE DETECTED (>5% of data)")
            print("\n✅ RECOMMENDED APPROACH: DO NOT REMOVE ANOMALIES")
            print("\nReasons:")
            print("  1. Large percentage (60-90%) of data exceeds stated constraints")
            print("  2. Removing this much data would destroy temporal patterns")
            print("  3. Anomalies appear to be normal operational variations")
            print("  4. Constraints likely represent theoretical/design limits, not operational")
            print("\n🎯 INSTEAD:")
            print("  • Use realistic constraints derived from data (e.g., 95th percentile)")
            print("  • Keep all data for optimization model")
            print("  • Flag extreme outliers (>99.5th percentile) for investigation")
            print("  • Clarify with stakeholders: are constraints aspirational or hard limits?")
        else:
            print("\n✅ RECOMMENDED APPROACH: REMOVE ANOMALIES")
            print("\nReasons:")
            print("  1. Low anomaly rate (<5% of data)")
            print("  2. Likely measurement errors or exceptional events")
            print("  3. Won't significantly impact temporal patterns")

        print("\n" + "="*70)

        return report

    def create_cleaned_dataset(self, save=False):
        """Create a cleaned dataset with anomalies removed (optional)"""
        print("\n" + "="*70)
        print("CREATING CLEANED DATASET OPTIONS")
        print("="*70)

        # Option 1: Remove only extreme outliers (>99.5th percentile)
        data_clean_extreme = self.data.copy()
        removed_extreme = 0

        for gta_name, columns in GTA_COLUMNS.items():
            hp_col, mp_col, ee_col = columns

            # Remove only top 0.5% outliers
            hp_99_5 = np.percentile(data_clean_extreme[hp_col].dropna(), 99.5)
            mp_99_5 = np.percentile(data_clean_extreme[mp_col].dropna(), 99.5)

            mask = (data_clean_extreme[hp_col] <= hp_99_5) & (data_clean_extreme[mp_col] <= mp_99_5)
            removed_extreme += (~mask).sum()
            data_clean_extreme = data_clean_extreme[mask]

        # Option 2: Keep data within stated constraints
        data_clean_constraints = self.data.copy()
        removed_constraints = 0

        for gta_name, columns in GTA_COLUMNS.items():
            hp_col, mp_col, ee_col = columns

            mask = (
                (data_clean_constraints[hp_col] >= CONSTRAINTS['min_steam_requirement']) &
                (data_clean_constraints[hp_col] <= CONSTRAINTS['max_hp_steam_input']) &
                (data_clean_constraints[mp_col] <= CONSTRAINTS['max_mp_steam_extraction']) &
                (data_clean_constraints[ee_col] <= CONSTRAINTS['max_energy_production'])
            )
            removed_constraints += (~mask).sum()
            data_clean_constraints = data_clean_constraints[mask]

        print(f"\nOriginal dataset: {len(self.data):,} records")
        print(f"\nOption 1 - Remove extreme outliers (>99.5th percentile):")
        print(f"  Remaining: {len(data_clean_extreme):,} records")
        print(f"  Removed: {removed_extreme:,} records ({removed_extreme/len(self.data)*100:.2f}%)")
        print(f"  ✅ RECOMMENDED for optimization model")

        print(f"\nOption 2 - Enforce stated constraints:")
        print(f"  Remaining: {len(data_clean_constraints):,} records")
        print(f"  Removed: {removed_constraints:,} records ({removed_constraints/len(self.data)*100:.2f}%)")
        print(f"  ⚠️  NOT RECOMMENDED (removes too much data)")

        if save:
            # Save cleaned dataset
            output_path = self.loader.filepath.replace('.csv', '_cleaned_extreme.csv')
            data_clean_extreme.to_csv(output_path)
            print(f"\n✅ Saved cleaned dataset to: {output_path}")

        print("\n" + "="*70)

        return data_clean_extreme, data_clean_constraints

    def run_full_analysis(self):
        """Run complete anomaly analysis"""
        print("\n🔍 Running Anomaly Analysis...\n")

        print("1. Detecting anomalies by constraints...")
        self.detect_anomalies_by_constraints()

        print("\n2. Analyzing temporal distribution...")
        self.analyze_temporal_distribution()

        print("\n3. Calculating percentiles...")
        self.calculate_percentiles()

        print("\n4. Plotting anomaly timeline...")
        self.plot_anomaly_timeline()

        print("\n5. Plotting anomaly detail view...")
        self.plot_anomaly_zoom()

        print("\n6. Creating cleaned dataset options...")
        self.create_cleaned_dataset(save=False)

        print("\n7. Generating recommendation...")
        self.recommend_cleaning_strategy()

        print(f"\n✅ Anomaly Analysis Complete! Check {FIGURES_PATH} for visualizations.")


if __name__ == "__main__":
    analyzer = AnomalyAnalyzer()
    analyzer.run_full_analysis()
