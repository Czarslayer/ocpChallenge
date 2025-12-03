"""
Configuration file for OCP Energy Optimization Hackathon
Contains operational constraints and system parameters
"""

# Operational Constraints
CONSTRAINTS = {
    'max_hp_steam_input': 220,      # tons/hour per GTA
    'min_steam_requirement': 90,     # tons/hour per GTA
    'max_mp_steam_extraction': 100,  # tons/hour per GTA
    'max_energy_production': 60      # MWh per GTA
}

# Data columns
GTA_COLUMNS = {
    'GTA_1': ['Admission_HP_GTA_1', 'Soutirage_MP_GTA_1', 'Prod_EE_GTA_1'],
    'GTA_2': ['Admission_HP_GTA_2', 'Soutirage_MP_GTA_2', 'Prod_EE_GTA2_2'],
    'GTA_3': ['Admission_HP_GTA_3', 'Soutirage_MP_GTA_3', 'Prod_EE_GTA_3']
}

# File paths
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'Data_Energie.csv')
OUTPUT_PATH = os.path.join(BASE_DIR, 'outputs/')
FIGURES_PATH = os.path.join(BASE_DIR, 'outputs', 'figures/')
