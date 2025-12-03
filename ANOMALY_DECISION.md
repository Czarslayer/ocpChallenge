# Anomaly Analysis & Decision Guide

## Executive Summary

**RECOMMENDATION: DO NOT REMOVE ANOMALIES - USE REALISTIC CONSTRAINTS INSTEAD**

The "anomalies" are actually **normal operations** that exceed theoretical design limits. Removing them would destroy 99.89% of your data.

---

## The Numbers

### Constraint Violations in Historical Data

| GTA | MP Violations | HP Violations | % of Total Data |
|-----|---------------|---------------|-----------------|
| **GTA_1** | 43,390 / 48,394 | 1,562 / 48,394 | **89.7%** violate MP |
| **GTA_2** | 29,551 / 48,394 | 18,676 / 48,394 | **61.1%** violate MP |
| **GTA_3** | 41,215 / 48,394 | 3,970 / 48,394 | **85.2%** violate MP |

### Key Finding: Violations Are Continuous

- **98-99%** of violations occur in continuous blocks
- Not random spikes - sustained operational patterns
- Spans from **Jan 2024 to May 2025** (entire dataset)

---

## Data Cleaning Options Tested

### Option 1: Remove Extreme Outliers (>99.5th percentile)
- **Removes**: 1,395 records (2.88%)
- **Keeps**: 46,999 records (97.12%)
- ✅ **RECOMMENDED** - Removes only truly exceptional values
- Preserves operational patterns and temporal relationships

### Option 2: Enforce Stated Constraints (100 tons/hour MP max)
- **Removes**: 48,339 records (99.89%)
- **Keeps**: 55 records (0.11%)
- ❌ **NOT VIABLE** - Destroys dataset completely
- Would leave you with ~55 data points from 48K

---

## What the Data Actually Shows

### MP Steam Extraction - Real Distribution

| Percentile | GTA_1 | GTA_2 | GTA_3 | Constraint |
|------------|-------|-------|-------|------------|
| **50th** (median) | 147 | 146 | 142 | 100 |
| **75th** | 165 | 166 | 158 | 100 |
| **90th** | 178 | 171 | 170 | 100 |
| **95th** | 184 | 172 | 175 | 100 |
| **99th** | 187 | 175 | 179 | 100 |
| **99.5th** | 187 | 176 | 180 | 100 |
| **100th** (max) | **266** | 179 | 182 | 100 |

**Even the MEDIAN (50th percentile) exceeds the stated constraint of 100 tons/hour!**

---

## Recommendation: Use Data-Derived Constraints

### Proposed Realistic Constraints

Instead of theoretical limits, use actual operational ranges:

#### Option A: Normal Operations (95th Percentile)
```python
REALISTIC_CONSTRAINTS = {
    'max_hp_steam_input': 210,      # 95th percentile across GTAs
    'min_steam_requirement': 50,     # Allow for partial shutdowns
    'max_mp_steam_extraction': 185,  # 95th percentile
    'max_energy_production': 60      # Keep original (respected)
}
```

#### Option B: Safety Margins (99th Percentile)
```python
CONSERVATIVE_CONSTRAINTS = {
    'max_hp_steam_input': 207,      # 99th percentile
    'min_steam_requirement': 50,
    'max_mp_steam_extraction': 180,  # 99th percentile
    'max_energy_production': 60
}
```

#### Option C: Keep Stated Constraints (For Optimization Targets)
```python
# Use stated constraints as GOALS, not hard limits
# Optimization model tries to stay within these, but can exceed if needed
TARGET_CONSTRAINTS = {
    'target_hp_steam_input': 220,
    'target_mp_steam_extraction': 100,
    'max_energy_production': 60  # Hard limit (never violated)
}
```

---

## Why This Matters for Your Hackathon

### If You Remove "Anomalies"
❌ You'll have only 55 data points (from 48K)
❌ Can't train meaningful models
❌ Can't understand operational patterns
❌ Optimization will be based on unrealistic scenarios

### If You Keep Data & Use Realistic Constraints
✅ Keep 46,999 records (97% of data)
✅ Model reflects actual operations
✅ Optimization recommendations will be practical
✅ Chatbot can handle real scenarios

---

## What Caused This Mismatch?

### Likely Explanations

1. **Theoretical Design Limits**: The 100 tons/hour may be the original equipment spec
2. **Outdated Documentation**: Constraints may not reflect actual upgraded capacity
3. **Safety Margins**: Conservative limits that aren't enforced in practice
4. **Different Operating Modes**: Normal operations exceed "design" limits safely

### What You Should Do

**For the Hackathon**: Use data-derived constraints (95th percentile approach)

**For Production**: Recommend OCP clarify:
- Are these hard physical limits or targets?
- Have equipment upgrades changed capacity?
- Should optimization respect these or use actual ranges?

---

## Visualizations Generated

Check [outputs/figures/](outputs/figures/) for:

1. **anomaly_timeline.png** - Full timeline showing violations aren't rare spikes
2. **anomaly_detail.png** - Zoom into violation periods (continuous, not random)

---

## Final Decision for Optimization Model

### 🎯 RECOMMENDED APPROACH

```python
# For Phase 2 optimization model:

1. Use data-derived constraints (95th percentile)
2. Keep all 48,394 records (or remove only top 0.5% extremes)
3. Model realistic operations, not theoretical limits
4. Flag when recommendations exceed stated limits
5. Let chatbot explain: "Exceeds design limit, but within operational range"
```

### Implementation

```python
# In config.py, add:

# Data-derived realistic constraints (95th percentile)
OPERATIONAL_CONSTRAINTS = {
    'max_hp_steam_input': 210,       # Based on data analysis
    'min_steam_requirement': 50,     # Allow for shutdowns/ramp-up
    'max_mp_steam_extraction': 185,  # Based on data analysis
    'max_energy_production': 60      # Original (never violated)
}

# Original stated constraints (for reference/comparison)
STATED_CONSTRAINTS = {
    'max_hp_steam_input': 220,
    'min_steam_requirement': 90,
    'max_mp_steam_extraction': 100,
    'max_energy_production': 60
}
```

---

## Summary

**The "anomalies" aren't errors - they're how the plant actually operates.**

If you want to enforce the stated constraints as hard limits, you can build that into the optimization model as **aspirational goals**, but the model needs to train on **realistic data** to be useful.

For the hackathon, use realistic constraints and keep the data intact. The judges will appreciate a practical, deployable solution over a theoretical one that doesn't match reality.
