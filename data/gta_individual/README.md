# Individual GTA Data Files

**Created**: November 28, 2025
**Purpose**: Separate CSV files for each GTA with proper downtime handling

---

## Files Overview

### Individual GTA Files

| File | Records | Description | Downtime Handling |
|------|---------|-------------|-------------------|
| **GTA_1.csv** | 48,394 | Full dataset for GTA_1 | Minimal downtime (1.6%) - kept as-is |
| **GTA_2_operational_only.csv** | 29,746 | GTA_2 operational periods only | **Downtime removed** (191-day outage excluded) |
| **GTA_2_full.csv** | 48,394 | GTA_2 full dataset (reference) | Includes 191-day downtime period |
| **GTA_3.csv** | 48,394 | Full dataset for GTA_3 | Includes 16-day maintenance period |

### Combined Files

| File | Records | Description |
|------|---------|-------------|
| **all_gtas_operational.csv** | 48,380 | All 3 GTAs with operational values only (0 when down) |
| **gta_summary_statistics.csv** | 3 rows | Statistical summary of each GTA (operational periods only) |

---

## File Structures

### Individual GTA Files (GTA_1.csv, GTA_2_operational_only.csv, GTA_3.csv)

```csv
Date,HP_Admission,MP_Extraction,Energy_Production
2024-01-01 00:00:00,174.0176,142.858337,19.1799526
2024-01-01 00:15:00,174.100952,142.676392,18.9854126
...
```

**Columns**:
- `Date` - Timestamp (15-minute intervals)
- `HP_Admission` - High Pressure steam admission (tons/hour)
- `MP_Extraction` - Medium Pressure steam extraction (tons/hour)
- `Energy_Production` - Electricity production (MWh)

### Combined File (all_gtas_operational.csv)

```csv
Date,GTA_1_HP_Admission,GTA_1_MP_Extraction,GTA_1_Energy_Production,GTA_1_Operational,GTA_2_HP_Admission,...
```

**Columns**:
- `Date` - Timestamp
- `{GTA}_HP_Admission` - HP steam (0 when GTA is down)
- `{GTA}_MP_Extraction` - MP steam (0 when GTA is down)
- `{GTA}_Energy_Production` - Energy (0 when GTA is down)
- `{GTA}_Operational` - Boolean (True = operational, False = down)

### Summary Statistics File (gta_summary_statistics.csv)

Contains operational statistics for each GTA:
- Uptime percentage
- Average values (operational periods only)
- Min/max values
- Total/operational/downtime record counts

---

## Key Statistics (Operational Periods Only)

### GTA_1 - Highly Reliable
- **Uptime**: 98.4% (47,603 operational records)
- **Downtime**: 1.6% (791 records, ~8 days)
- **Avg HP**: 187.2 tons/hour
- **Avg MP**: 141.9 tons/hour
- **Avg Energy**: 23.3 MWh
- **Status**: Most reliable turbine

### GTA_2 - Extended Outage
- **Uptime**: 61.5% (29,746 operational records)
- **Downtime**: 38.5% (18,648 records, ~194 days)
- **Major Outage**: Nov 8, 2024 → May 19, 2025 (191 consecutive days)
- **Avg HP**: 198.6 tons/hour (when operational)
- **Avg MP**: 158.6 tons/hour (when operational)
- **Avg Energy**: 22.6 MWh (when operational)
- **Status**: ⚠️ Down for last 6 months of dataset

### GTA_3 - Stable with Maintenance
- **Uptime**: 92.8% (44,932 operational records)
- **Downtime**: 7.2% (3,462 records, ~36 days)
- **Major Outage**: July 6-22, 2024 (16 days)
- **Avg HP**: 183.7 tons/hour
- **Avg MP**: 139.7 tons/hour
- **Avg Energy**: 23.1 MWh
- **Status**: Stable with scheduled maintenance

---

## Usage Recommendations

### For Optimization Model Training

**Option 1: Use Individual Files (Recommended)**
```python
# Load only operational data for each GTA
gta1 = pd.read_csv('gta_individual/GTA_1.csv')
gta2 = pd.read_csv('gta_individual/GTA_2_operational_only.csv')  # ⭐ Downtime removed
gta3 = pd.read_csv('gta_individual/GTA_3.csv')

# Train separate models or combined model
```

**Option 2: Use Combined File**
```python
# Load all GTAs together with operational flags
all_gtas = pd.read_csv('gta_individual/all_gtas_operational.csv')

# Filter to operational periods
operational_only = all_gtas[
    all_gtas['GTA_1_Operational'] |
    all_gtas['GTA_2_Operational'] |
    all_gtas['GTA_3_Operational']
]
```

### For Analysis

**Comparing GTAs**:
```python
summary = pd.read_csv('gta_individual/gta_summary_statistics.csv')
# Compare uptime, efficiency, etc.
```

**Time Series Analysis**:
```python
# Use individual files for clean time series per GTA
gta1 = pd.read_csv('gta_individual/GTA_1.csv', parse_dates=['Date'])
gta1.set_index('Date', inplace=True)
```

---

## Important Notes

### GTA_2 Downtime
The `GTA_2_operational_only.csv` file has **discontinuous timestamps** because downtime periods were removed:
- Operational: Jan 1, 2024 → Nov 8, 2024
- **GAP: Nov 8, 2024 → May 19, 2025** (191 days removed)
- Next operational: (none in this dataset)

If you need continuous timestamps, use `GTA_2_full.csv` (but values will be 0 during downtime).

### Missing Values
All missing values have been handled:
- Forward fill for small gaps
- Backward fill for start-of-dataset gaps
- Zero fill for any remaining

### Threshold for "Operational"
GTAs are considered operational when `HP_Admission > 10 tons/hour`. Below this threshold, the turbine is considered down.

---

## Data Quality

| Aspect | Status |
|--------|--------|
| Missing values | ✅ Handled (70 total, filled) |
| Downtime identification | ✅ Complete |
| Outliers | ⚠️ Present (see parent ANOMALY_DECISION.md) |
| Timestamps | ✅ Consistent 15-min intervals |
| Data completeness | ✅ 99.86% complete |

---

## Related Files

- **Parent directory**: `../Data_Energie.csv` - Original raw data
- **Cleaned version**: `../Data_Energie_cleaned.csv` - All GTAs, downtime set to 0
- **Analysis**: `../../DOWNTIME_FINDINGS.md` - Full downtime analysis
- **Visualizations**: `../../outputs/figures/operational_timeline.png`

---

## Questions for Organizers

Based on this analysis, critical questions for tomorrow's meeting:

1. **GTA_2 Status**: Is the 191-day outage expected? Will GTA_2 return to service?
2. **Modeling Scope**: Should we optimize for 2 GTAs (excluding GTA_2) or 3 GTAs?
3. **Downtime Scenarios**: Should the chatbot handle "What if GTA_X goes offline?" scenarios?

See `../../MEETING_QUESTIONS.md` for full list.

---

## File Sizes

```
GTA_1.csv                      2.4 MB  (48,394 records)
GTA_2_operational_only.csv     1.5 MB  (29,746 records) ⭐ Use this for GTA_2
GTA_2_full.csv                 2.3 MB  (48,394 records, reference only)
GTA_3.csv                      2.4 MB  (48,394 records)
all_gtas_operational.csv       5.7 MB  (48,380 records)
gta_summary_statistics.csv     0.6 KB  (summary)
```

**Total**: ~14.5 MB

---

**Generated**: November 28, 2025
**Tool**: `src/split_gta_data.py`
**Threshold**: HP > 10 tons/hour = operational
