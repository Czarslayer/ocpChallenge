"""
Data loading and validation utilities for OCP Energy Optimization
"""

import pandas as pd
import numpy as np
from config import DATA_PATH, CONSTRAINTS, GTA_COLUMNS


class EnergyDataLoader:
    """Load and validate energy production data"""

    def __init__(self, filepath=DATA_PATH):
        self.filepath = filepath
        self.data = None
        self.validation_report = {}

    def load_data(self):
        """Load CSV data and parse datetime"""
        print(f"Loading data from {self.filepath}...")
        self.data = pd.read_csv(self.filepath)
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.data.set_index('Date', inplace=True)
        print(f"Loaded {len(self.data)} records from {self.data.index.min()} to {self.data.index.max()}")
        return self.data

    def get_basic_stats(self):
        """Get basic statistics about the dataset"""
        if self.data is None:
            self.load_data()

        stats = {
            'total_records': len(self.data),
            'date_range': (self.data.index.min(), self.data.index.max()),
            'missing_values': self.data.isnull().sum().to_dict(),
            'data_shape': self.data.shape
        }
        return stats

    def validate_constraints(self):
        """Check if data respects operational constraints"""
        if self.data is None:
            self.load_data()

        violations = {}

        for gta_name, columns in GTA_COLUMNS.items():
            hp_col, mp_col, ee_col = columns

            # Check HP steam input constraints
            hp_violations = self.data[
                (self.data[hp_col] > CONSTRAINTS['max_hp_steam_input']) |
                (self.data[hp_col] < CONSTRAINTS['min_steam_requirement'])
            ]

            # Check MP steam extraction constraints
            mp_violations = self.data[self.data[mp_col] > CONSTRAINTS['max_mp_steam_extraction']]

            # Check energy production constraints
            ee_violations = self.data[self.data[ee_col] > CONSTRAINTS['max_energy_production']]

            violations[gta_name] = {
                'hp_violations': len(hp_violations),
                'mp_violations': len(mp_violations),
                'ee_violations': len(ee_violations),
                'hp_range': (self.data[hp_col].min(), self.data[hp_col].max()),
                'mp_range': (self.data[mp_col].min(), self.data[mp_col].max()),
                'ee_range': (self.data[ee_col].min(), self.data[ee_col].max())
            }

        self.validation_report = violations
        return violations

    def get_gta_data(self, gta_name):
        """Extract data for a specific GTA"""
        if self.data is None:
            self.load_data()

        if gta_name not in GTA_COLUMNS:
            raise ValueError(f"Invalid GTA name. Choose from {list(GTA_COLUMNS.keys())}")

        columns = GTA_COLUMNS[gta_name]
        gta_data = self.data[columns].copy()
        gta_data.columns = ['HP_Admission', 'MP_Extraction', 'Energy_Production']
        return gta_data

    def get_all_gtas_normalized(self):
        """Get all GTA data in normalized format"""
        if self.data is None:
            self.load_data()

        all_data = []
        for gta_name in GTA_COLUMNS.keys():
            gta_df = self.get_gta_data(gta_name)
            gta_df['GTA'] = gta_name
            all_data.append(gta_df)

        return pd.concat(all_data, axis=0)

    def calculate_system_totals(self):
        """Calculate total system metrics across all GTAs"""
        if self.data is None:
            self.load_data()

        totals = pd.DataFrame(index=self.data.index)

        # Sum HP admissions
        totals['Total_HP_Admission'] = (
            self.data['Admission_HP_GTA_1'] +
            self.data['Admission_HP_GTA_2'] +
            self.data['Admission_HP_GTA_3']
        )

        # Sum MP extractions
        totals['Total_MP_Extraction'] = (
            self.data['Soutirage_MP_GTA_1'] +
            self.data['Soutirage_MP_GTA_2'] +
            self.data['Soutirage_MP_GTA_3']
        )

        # Sum energy production
        totals['Total_Energy_Production'] = (
            self.data['Prod_EE_GTA_1'] +
            self.data['Prod_EE_GTA2_2'] +
            self.data['Prod_EE_GTA_3']
        )

        return totals

    def print_validation_report(self):
        """Print a formatted validation report"""
        if not self.validation_report:
            self.validate_constraints()

        print("\n" + "="*60)
        print("CONSTRAINT VALIDATION REPORT")
        print("="*60)

        for gta, metrics in self.validation_report.items():
            print(f"\n{gta}:")
            print(f"  HP Steam Range: {metrics['hp_range'][0]:.2f} - {metrics['hp_range'][1]:.2f} tons/hour")
            print(f"    (Constraint: {CONSTRAINTS['min_steam_requirement']} - {CONSTRAINTS['max_hp_steam_input']} tons/hour)")
            print(f"    Violations: {metrics['hp_violations']}")

            print(f"  MP Extraction Range: {metrics['mp_range'][0]:.2f} - {metrics['mp_range'][1]:.2f} tons/hour")
            print(f"    (Constraint: Max {CONSTRAINTS['max_mp_steam_extraction']} tons/hour)")
            print(f"    Violations: {metrics['mp_violations']}")

            print(f"  Energy Production Range: {metrics['ee_range'][0]:.2f} - {metrics['ee_range'][1]:.2f} MWh")
            print(f"    (Constraint: Max {CONSTRAINTS['max_energy_production']} MWh)")
            print(f"    Violations: {metrics['ee_violations']}")

        print("\n" + "="*60)


if __name__ == "__main__":
    # Test the data loader
    loader = EnergyDataLoader()
    loader.load_data()

    print("\nBasic Statistics:")
    stats = loader.get_basic_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    loader.print_validation_report()

    print("\nSystem Totals Summary:")
    totals = loader.calculate_system_totals()
    print(totals.describe())
