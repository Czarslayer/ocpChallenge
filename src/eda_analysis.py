"""
Exploratory Data Analysis for OCP Energy Optimization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from data_loader import EnergyDataLoader
from config import CONSTRAINTS, GTA_COLUMNS, FIGURES_PATH
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


class EnergyEDA:
    """Exploratory Data Analysis for energy data"""

    def __init__(self):
        self.loader = EnergyDataLoader()
        self.data = self.loader.load_data()
        self.totals = self.loader.calculate_system_totals()
        os.makedirs(FIGURES_PATH, exist_ok=True)

    def plot_time_series_overview(self):
        """Plot time series for all GTAs"""
        fig, axes = plt.subplots(3, 1, figsize=(16, 12))
        fig.suptitle('Energy Production Time Series - All GTAs', fontsize=16, fontweight='bold')

        metrics = ['HP_Admission', 'MP_Extraction', 'Energy_Production']
        titles = ['HP Steam Admission (tons/hour)', 'MP Steam Extraction (tons/hour)', 'Energy Production (MWh)']

        for idx, (metric, title) in enumerate(zip(metrics, titles)):
            for gta_name in GTA_COLUMNS.keys():
                gta_data = self.loader.get_gta_data(gta_name)
                axes[idx].plot(gta_data.index, gta_data[metric], label=gta_name, alpha=0.7)

            axes[idx].set_title(title, fontsize=12)
            axes[idx].set_ylabel('Value')
            axes[idx].legend()
            axes[idx].grid(True, alpha=0.3)

        axes[-1].set_xlabel('Date')
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}time_series_overview.png", dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_PATH}time_series_overview.png")
        plt.close()

    def plot_system_totals(self):
        """Plot total system metrics"""
        fig, axes = plt.subplots(3, 1, figsize=(16, 10))
        fig.suptitle('Total System Metrics Over Time', fontsize=16, fontweight='bold')

        metrics = ['Total_HP_Admission', 'Total_MP_Extraction', 'Total_Energy_Production']
        titles = ['Total HP Steam Admission', 'Total MP Steam Extraction', 'Total Energy Production']

        for idx, (metric, title) in enumerate(zip(metrics, titles)):
            axes[idx].plot(self.totals.index, self.totals[metric], color='navy', linewidth=0.8)
            axes[idx].fill_between(self.totals.index, self.totals[metric], alpha=0.3)
            axes[idx].set_title(title, fontsize=12)
            axes[idx].set_ylabel('Value')
            axes[idx].grid(True, alpha=0.3)

        axes[-1].set_xlabel('Date')
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}system_totals.png", dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_PATH}system_totals.png")
        plt.close()

    def plot_correlation_analysis(self):
        """Analyze correlations between variables"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle('Correlation Analysis by GTA', fontsize=16, fontweight='bold')

        for idx, gta_name in enumerate(GTA_COLUMNS.keys()):
            gta_data = self.loader.get_gta_data(gta_name)
            corr = gta_data.corr()

            sns.heatmap(corr, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                       square=True, ax=axes[idx], cbar_kws={'shrink': 0.8})
            axes[idx].set_title(f'{gta_name} Correlations')

        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}correlation_analysis.png", dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_PATH}correlation_analysis.png")
        plt.close()

    def plot_distribution_analysis(self):
        """Plot distributions of key metrics"""
        fig, axes = plt.subplots(3, 3, figsize=(18, 12))
        fig.suptitle('Distribution Analysis - All GTAs', fontsize=16, fontweight='bold')

        metrics = ['HP_Admission', 'MP_Extraction', 'Energy_Production']
        metric_labels = ['HP Steam (tons/hour)', 'MP Steam (tons/hour)', 'Energy (MWh)']

        for row_idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
            for col_idx, gta_name in enumerate(GTA_COLUMNS.keys()):
                gta_data = self.loader.get_gta_data(gta_name)

                axes[row_idx, col_idx].hist(gta_data[metric], bins=50, alpha=0.7, color='steelblue', edgecolor='black')
                axes[row_idx, col_idx].axvline(gta_data[metric].mean(), color='red', linestyle='--', linewidth=2, label='Mean')
                axes[row_idx, col_idx].axvline(gta_data[metric].median(), color='green', linestyle='--', linewidth=2, label='Median')

                if row_idx == 0:
                    axes[row_idx, col_idx].set_title(f'{gta_name}', fontsize=11, fontweight='bold')
                if col_idx == 0:
                    axes[row_idx, col_idx].set_ylabel(label)
                if row_idx == 2:
                    axes[row_idx, col_idx].set_xlabel('Value')

                axes[row_idx, col_idx].legend(fontsize=8)
                axes[row_idx, col_idx].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}distribution_analysis.png", dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_PATH}distribution_analysis.png")
        plt.close()

    def calculate_efficiency_metrics(self):
        """Calculate efficiency metrics for each GTA"""
        efficiency_data = []

        for gta_name in GTA_COLUMNS.keys():
            gta_data = self.loader.get_gta_data(gta_name)

            # Energy per unit HP steam
            gta_data['Energy_per_HP'] = gta_data['Energy_Production'] / gta_data['HP_Admission']

            # Energy per unit MP steam
            gta_data['Energy_per_MP'] = gta_data['Energy_Production'] / gta_data['MP_Extraction']

            # MP extraction efficiency (MP/HP ratio)
            gta_data['MP_to_HP_Ratio'] = gta_data['MP_Extraction'] / gta_data['HP_Admission']

            # Net steam consumption (HP - MP)
            gta_data['Net_Steam_Consumption'] = gta_data['HP_Admission'] - gta_data['MP_Extraction']

            efficiency_summary = {
                'GTA': gta_name,
                'Avg_Energy_per_HP': gta_data['Energy_per_HP'].mean(),
                'Avg_Energy_per_MP': gta_data['Energy_per_MP'].mean(),
                'Avg_MP_to_HP_Ratio': gta_data['MP_to_HP_Ratio'].mean(),
                'Avg_Net_Steam': gta_data['Net_Steam_Consumption'].mean(),
                'Total_Energy': gta_data['Energy_Production'].sum(),
                'Avg_HP': gta_data['HP_Admission'].mean(),
                'Avg_MP': gta_data['MP_Extraction'].mean()
            }

            efficiency_data.append(efficiency_summary)

        return pd.DataFrame(efficiency_data)

    def plot_efficiency_comparison(self):
        """Plot efficiency metrics comparison"""
        efficiency_df = self.calculate_efficiency_metrics()

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('GTA Efficiency Comparison', fontsize=16, fontweight='bold')

        # Energy per HP
        axes[0, 0].bar(efficiency_df['GTA'], efficiency_df['Avg_Energy_per_HP'], color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Average Energy per HP Steam')
        axes[0, 0].set_ylabel('MWh / (tons/hour)')
        axes[0, 0].grid(axis='y', alpha=0.3)

        # MP to HP Ratio
        axes[0, 1].bar(efficiency_df['GTA'], efficiency_df['Avg_MP_to_HP_Ratio'], color='lightcoral', edgecolor='black')
        axes[0, 1].set_title('Average MP to HP Ratio')
        axes[0, 1].set_ylabel('Ratio')
        axes[0, 1].grid(axis='y', alpha=0.3)

        # Total Energy Production
        axes[1, 0].bar(efficiency_df['GTA'], efficiency_df['Total_Energy'], color='lightgreen', edgecolor='black')
        axes[1, 0].set_title('Total Energy Production')
        axes[1, 0].set_ylabel('MWh')
        axes[1, 0].grid(axis='y', alpha=0.3)

        # Average Net Steam Consumption
        axes[1, 1].bar(efficiency_df['GTA'], efficiency_df['Avg_Net_Steam'], color='orange', edgecolor='black')
        axes[1, 1].set_title('Average Net Steam Consumption (HP - MP)')
        axes[1, 1].set_ylabel('tons/hour')
        axes[1, 1].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}efficiency_comparison.png", dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_PATH}efficiency_comparison.png")
        plt.close()

        return efficiency_df

    def analyze_temporal_patterns(self):
        """Analyze hourly and daily patterns"""
        # Add time features
        totals_copy = self.totals.copy()
        totals_copy['Hour'] = totals_copy.index.hour
        totals_copy['DayOfWeek'] = totals_copy.index.dayofweek
        totals_copy['Date'] = totals_copy.index.date

        # Hourly patterns
        hourly_avg = totals_copy.groupby('Hour')[['Total_HP_Admission', 'Total_MP_Extraction', 'Total_Energy_Production']].mean()

        # Daily patterns
        daily_avg = totals_copy.groupby('DayOfWeek')[['Total_HP_Admission', 'Total_MP_Extraction', 'Total_Energy_Production']].mean()

        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Temporal Patterns Analysis', fontsize=16, fontweight='bold')

        # Hourly pattern
        hourly_avg.plot(ax=axes[0], marker='o', linewidth=2)
        axes[0].set_title('Average Metrics by Hour of Day')
        axes[0].set_xlabel('Hour')
        axes[0].set_ylabel('Value')
        axes[0].legend(['HP Admission', 'MP Extraction', 'Energy Production'])
        axes[0].grid(True, alpha=0.3)

        # Daily pattern
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_avg.index = [day_names[i] for i in daily_avg.index]
        daily_avg.plot(ax=axes[1], marker='o', linewidth=2)
        axes[1].set_title('Average Metrics by Day of Week')
        axes[1].set_xlabel('Day')
        axes[1].set_ylabel('Value')
        axes[1].legend(['HP Admission', 'MP Extraction', 'Energy Production'])
        axes[1].grid(True, alpha=0.3)
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}temporal_patterns.png", dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_PATH}temporal_patterns.png")
        plt.close()

        return hourly_avg, daily_avg

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "="*70)
        print("EXPLORATORY DATA ANALYSIS SUMMARY REPORT")
        print("="*70)

        # Basic stats
        stats = self.loader.get_basic_stats()
        print(f"\nDataset Overview:")
        print(f"  Total Records: {stats['total_records']:,}")
        print(f"  Date Range: {stats['date_range'][0]} to {stats['date_range'][1]}")
        print(f"  Duration: {(stats['date_range'][1] - stats['date_range'][0]).days} days")

        # Missing values
        missing = stats['missing_values']
        total_missing = sum(missing.values())
        print(f"\nMissing Values: {total_missing}")

        # Constraint validation
        self.loader.print_validation_report()

        # Efficiency metrics
        print("\nEfficiency Metrics:")
        efficiency_df = self.calculate_efficiency_metrics()
        print(efficiency_df.to_string(index=False))

        # System totals summary
        print("\nSystem Totals Summary:")
        print(self.totals.describe())

        print("\n" + "="*70)

    def run_full_analysis(self):
        """Run complete EDA pipeline"""
        print("\nRunning Full Exploratory Data Analysis...\n")

        print("1. Generating time series overview...")
        self.plot_time_series_overview()

        print("2. Plotting system totals...")
        self.plot_system_totals()

        print("3. Analyzing correlations...")
        self.plot_correlation_analysis()

        print("4. Analyzing distributions...")
        self.plot_distribution_analysis()

        print("5. Comparing efficiency metrics...")
        self.plot_efficiency_comparison()

        print("6. Analyzing temporal patterns...")
        self.analyze_temporal_patterns()

        print("\n7. Generating summary report...")
        self.generate_summary_report()

        print(f"\n✅ EDA Complete! All visualizations saved to {FIGURES_PATH}")


if __name__ == "__main__":
    eda = EnergyEDA()
    eda.run_full_analysis()
