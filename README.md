# OCP Energy Optimization Hackathon

Smart Energy Optimization System for OCP Production Facility

## Project Overview

This project develops an AI-powered optimization system for managing steam production and electricity generation across 3 Gas Turbine Alternators (GTAs) at an OCP production facility.

### Challenge Goals

1. **Optimize Energy Production**: Maximize electricity generation while respecting operational constraints
2. **Smart Steam Management**: Balance HP (High Pressure) and MP (Medium Pressure) steam allocation
3. **Decision Support**: Provide plant managers with a chatbot interface for scenario testing and recommendations

## Project Structure

```
ocp hackathon/
├── data/
│   └── Data_Energie.csv          # Historical energy production data (48K+ records)
├── src/
│   ├── config.py                 # Configuration and constraints
│   ├── data_loader.py            # Data loading and validation utilities
│   ├── eda_analysis.py           # Exploratory data analysis
│   ├── optimizer.py              # [Phase 2] Optimization model
│   └── chatbot.py                # [Phase 3] Local chatbot interface
├── notebooks/                     # Jupyter notebooks for analysis
├── outputs/
│   └── figures/                  # Generated visualizations
├── requirements.txt              # Python dependencies
├── PHASE1_FINDINGS.md            # Phase 1 analysis results
└── README.md                     # This file
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For local chatbot (Phase 3)
# Install Ollama: https://ollama.ai
ollama pull llama3.2
```

## Quick Start

### Phase 1: Data Analysis

```bash
cd src
python data_loader.py      # Validate data and check constraints
python eda_analysis.py     # Run full exploratory analysis
```

**Output**: 6 visualization files in `outputs/figures/`

### Phase 2: Optimization Model (In Progress)

```bash
cd src
python optimizer.py --scenario maximize_energy
```

### Phase 3: Chatbot Interface (Planned)

```bash
cd src
python chatbot.py
```

## Key Findings (Phase 1)

### Dataset
- **48,394 records** (15-minute intervals)
- **504 days** of operational data (Jan 2024 - May 2025)
- **99.86% complete** (only 70 missing values)

### Critical Insights

1. **Constraint Violations**: Historical data frequently exceeds stated constraints
   - MP Steam: Actual max ~265 tons/hour vs. stated 100 tons/hour
   - Suggests constraints are theoretical, not operational limits

2. **System Performance**:
   - Average total energy: 54.5 MWh
   - Peak production: 102.8 MWh
   - MP extraction efficiency: ~75-80%

3. **Optimization Opportunities**:
   - Trade-off between MP extraction and energy production
   - Load balancing across GTAs
   - Dynamic scenario handling

See [PHASE1_FINDINGS.md](PHASE1_FINDINGS.md) for detailed analysis.

## Operational Constraints

| Parameter | Limit | Unit | Status |
|-----------|-------|------|--------|
| Max HP Steam Input | 220 | tons/hour | ⚠️ Exceeded in data |
| Min Steam Requirement | 90 | tons/hour | ⚠️ Below in data |
| Max MP Steam Extraction | 100 | tons/hour | ⚠️ Exceeded in data |
| Max Energy Production | 60 | MWh | ✅ Respected |

## Data Schema

### Input Data (Data_Energie.csv)

| Column | Description | Unit |
|--------|-------------|------|
| Date | Timestamp (15-min intervals) | datetime |
| Admission_HP_GTA_X | HP steam input to GTA X | tons/hour |
| Soutirage_MP_GTA_X | MP steam extraction from GTA X | tons/hour |
| Prod_EE_GTA_X | Electricity production from GTA X | MWh |

*Where X = 1, 2, or 3*

## Technology Stack

### Current (Phase 1)
- **Python 3.9+**
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **matplotlib/seaborn** - Visualization
- **scipy** - Statistical analysis

### Planned (Phase 2-3)
- **PuLP** - Linear programming optimization
- **Ollama + LangChain** - Local LLM chatbot
- **Streamlit/Gradio** - Web interface
- **scikit-learn** - ML models (optional)

## Project Timeline

- ✅ **Phase 1**: Data Analysis & Understanding (COMPLETED)
- 🔄 **Phase 2**: Build Optimization Model (NEXT)
- ⏳ **Phase 3**: Create Local Chatbot Interface
- ⏳ **Phase 4**: Integration & Testing
- ⏳ **Phase 5**: Demo & Presentation

## Visualizations

All visualizations are available in [outputs/figures/](outputs/figures/):

1. **Time Series Overview** - Complete operational history
2. **System Totals** - Aggregated performance metrics
3. **Correlation Analysis** - Variable relationships by GTA
4. **Distribution Analysis** - Statistical distributions
5. **Efficiency Comparison** - GTA performance comparison
6. **Temporal Patterns** - Hourly and daily patterns

## Development Team

Developed for the OCP Energy Optimization Hackathon

## License

MIT License - Hackathon Project
# ocpChallenge
