# Questions for Hackathon Organizers Meeting

**Prepared by**: Data Analysis Team
**Date**: November 28, 2025
**Purpose**: Clarify operational constraints and optimization objectives

---

## Section 1: Operational Constraints Clarification

### ❓ Question 1: MP Steam Extraction Limits

**Question:**
"The challenge documentation states that maximum MP (Medium Pressure) steam extraction is 100 tons/hour per GTA. However, our analysis of the provided historical data shows that the median MP extraction is 142-147 tons/hour, with peaks reaching 265 tons/hour. Can you clarify:
- Are these theoretical design limits or actual operational limits?
- Should our optimization model respect the 100 t/h limit or use data-observed ranges?"

**Evidence Supporting This Question:**

```
Data Analysis Results (Data_Energie.csv):

GTA_1 MP Steam Extraction:
  - 50th percentile (median): 147 tons/hour
  - 95th percentile: 184 tons/hour
  - Maximum observed: 265.67 tons/hour
  - Constraint violations: 43,390 / 48,394 records (89.7%)

GTA_2 MP Steam Extraction:
  - 50th percentile (median): 146 tons/hour
  - 95th percentile: 172 tons/hour
  - Maximum observed: 178.66 tons/hour
  - Constraint violations: 29,551 / 48,394 records (61.1%)

GTA_3 MP Steam Extraction:
  - 50th percentile (median): 142 tons/hour
  - 95th percentile: 175 tons/hour
  - Maximum observed: 182.05 tons/hour
  - Constraint violations: 41,215 / 48,394 records (85.2%)

Stated Constraint: Max 100 tons/hour
Reality: Even the MEDIAN exceeds this by 42-47%
```

**Visual Evidence:**
- See: `outputs/figures/anomaly_timeline.png` - Shows violations throughout entire dataset
- See: `outputs/figures/distribution_analysis.png` - Shows actual value distributions

**Why This Matters:**
If we enforce the 100 t/h limit, we can only use 55 records out of 48,394 (0.11% of data), making model training impossible.

---

### ❓ Question 2: HP Steam Input Operational Range

**Question:**
"The data shows significant periods where HP steam admission is below the stated minimum of 90 tons/hour (some periods as low as 0-50 tons/hour). Are these:
- Planned shutdowns/maintenance periods?
- Normal ramp-up/ramp-down operations?
- Should our optimization model account for these states or focus only on steady-state operations?"

**Evidence Supporting This Question:**

```
Data Analysis Results:

GTA_1 HP Steam:
  - Minimum observed: 0 tons/hour
  - Below 90 t/h (stated min): 1,562 violations (3.2%)
  - Range: 0 - 246.11 tons/hour

GTA_2 HP Steam:
  - Minimum observed: 0 tons/hour
  - Below 90 t/h violations: 18,676 (38.6%)
  - Above 220 t/h violations: Additional records
  - Range: 0 - 209.41 tons/hour

GTA_3 HP Steam:
  - Minimum observed: 0 tons/hour
  - Below 90 t/h violations: 3,970 (8.2%)
  - Range: 0 - 209.54 tons/hour

Stated Constraints: Min 90 t/h, Max 220 t/h
Reality: Significant operations outside these bounds
```

**Visual Evidence:**
- See: `outputs/figures/time_series_overview.png` - Shows HP admission over time
- See: `PHASE1_FINDINGS.md` - Section on constraint violations

**Why This Matters:**
Understanding operational states (startup, shutdown, steady-state) affects how we model the system and what recommendations are practical.

---

### ❓ Question 3: Energy Production Negative Values

**Question:**
"We observed negative energy production values in the dataset (e.g., GTA_3 shows -128.07 MWh minimum). Can you explain:
- What causes negative energy production?
- Is this regenerative braking, measurement error, or energy consumption mode?
- Should these periods be included in the optimization model?"

**Evidence Supporting This Question:**

```
Data Analysis Results:

GTA_1 Energy Production:
  - Minimum: -0.61 MWh
  - Negative values: Limited occurrences

GTA_2 Energy Production:
  - Minimum: 0.00 MWh
  - No negative values observed

GTA_3 Energy Production:
  - Minimum: -128.07 MWh ⚠️
  - Several negative value periods
  - Range: -128.07 to 38.44 MWh

Dataset span: January 2024 - May 2025 (48,394 records)
```

**Visual Evidence:**
- See: `outputs/figures/distribution_analysis.png` - Bottom row shows energy distributions
- Can provide filtered dataset showing negative value timestamps

**Why This Matters:**
Optimization objectives (maximize energy) need to handle negative values correctly, or exclude these periods if they represent equipment issues.

---

## Section 2: System Operations Understanding

### ❓ Question 4: GTA Coordination and Load Balancing

**Question:**
"Our analysis shows that the 3 GTAs operate with different average loads and efficiencies:
- GTA_1: Highest total energy production (1.1M MWh)
- GTA_2: Lowest HP input but maintains good efficiency
- GTA_3: Medium performance

Are there operational constraints on how load is distributed between GTAs? For example:
- Can we freely adjust HP steam allocation between GTAs?
- Are there interdependencies we should model?
- Are certain GTAs preferred for specific operational scenarios?"

**Evidence Supporting This Question:**

```
GTA Efficiency Comparison (from analysis):

GTA_1:
  - Avg HP Admission: 184.3 tons/hour
  - Avg MP Extraction: 139.6 tons/hour
  - Total Energy: 1,110,859 MWh
  - MP/HP Ratio: ~0.76
  - Status: Highest producer

GTA_2:
  - Avg HP Admission: 122.1 tons/hour (33% lower than GTA_1)
  - Avg MP Extraction: 97.5 tons/hour
  - Total Energy: 671,209 MWh (39% lower than GTA_1)
  - MP/HP Ratio: ~0.80
  - Status: Most efficient MP extraction

GTA_3:
  - Avg HP Admission: 171.0 tons/hour
  - Avg MP Extraction: 129.7 tons/hour
  - Total Energy: 854,439 MWh
  - MP/HP Ratio: ~0.76
  - Status: Middle performer
```

**Visual Evidence:**
- See: `outputs/figures/efficiency_comparison.png` - Shows GTA performance comparison
- See: `PHASE1_FINDINGS.md` - Section 3: Individual GTA Efficiency

**Why This Matters:**
Optimization model needs to know if we can recommend shifting load from GTA_2 to GTA_1/GTA_3, or if current distribution is fixed by other factors.

---

### ❓ Question 5: MP Steam Demand Patterns

**Question:**
"The challenge mentions that MP steam is used by industrial consumers. Can you provide:
- Is MP steam demand predictable or highly variable?
- Are there specific industrial processes that drive MP demand?
- What happens if we can't meet MP steam demand (e.g., prioritize energy production)?
- Is there a minimum MP steam requirement we must satisfy?"

**Evidence Supporting This Question:**

```
MP Steam Demand Analysis:

System-wide MP Extraction Statistics:
  - Average total: 366.8 tons/hour (across 3 GTAs)
  - Standard deviation: 78.3 tons/hour (21.3% variation)
  - Minimum: 0 tons/hour
  - Maximum: 543.1 tons/hour
  - 25th-75th percentile range: 309-431 tons/hour

Temporal Patterns Observed:
  - Relatively stable throughout day (hourly analysis)
  - Some weekly variation detected
  - No strong seasonal patterns in available data
```

**Visual Evidence:**
- See: `outputs/figures/temporal_patterns.png` - Hourly and daily patterns
- See: `outputs/figures/system_totals.png` - MP extraction over time

**Why This Matters:**
Optimization trade-off is: maximize energy vs. satisfy MP demand. We need to know which takes priority and what the penalties are for not meeting MP demand.

---

### ❓ Question 6: Trade-offs Between Energy and Steam

**Question:**
"Our correlation analysis shows a weak negative correlation between MP extraction and energy production. This suggests a trade-off: extracting more MP steam may slightly reduce electricity generation. Can you confirm:
- Is there an actual physical trade-off?
- Should the optimization prioritize energy production, MP steam supply, or balance both?
- Are there economic factors (e.g., revenue from electricity vs. value of MP steam to production)?"

**Evidence Supporting This Question:**

```
Correlation Analysis Results:

GTA_1:
  - HP Admission ↔ MP Extraction: +0.94 (strong positive)
  - HP Admission ↔ Energy: +0.71 (positive)
  - MP Extraction ↔ Energy: -0.12 (weak negative) ⚠️

GTA_2:
  - HP Admission ↔ MP Extraction: +0.88 (strong positive)
  - HP Admission ↔ Energy: +0.62 (positive)
  - MP Extraction ↔ Energy: -0.31 (moderate negative) ⚠️

GTA_3:
  - HP Admission ↔ MP Extraction: +0.92 (strong positive)
  - HP Admission ↔ Energy: +0.75 (positive)
  - MP Extraction ↔ Energy: -0.08 (weak negative) ⚠️

Key Finding: More MP extraction correlates with less energy production
```

**Visual Evidence:**
- See: `outputs/figures/correlation_analysis.png` - Correlation heatmaps
- See: `PHASE1_FINDINGS.md` - Section 4: Correlation Analysis

**Why This Matters:**
The optimization objective function needs clear priorities. Should we maximize:
1. Total energy production?
2. MP steam availability?
3. A weighted combination?
4. Economic value (requires cost/price information)?

---

## Section 3: Data Quality and Scope

### ❓ Question 7: Missing Values and Data Quality

**Question:**
"The dataset contains 70 missing values across 504 days of operation. Can you clarify:
- What caused these missing values?
- Should we interpolate, forward-fill, or exclude these timestamps?
- Are there other data quality issues we should be aware of?"

**Evidence Supporting This Question:**

```
Missing Value Analysis:

Total records: 48,394
Missing values by column:
  - Admission_HP_GTA_1: 7 missing
  - Soutirage_MP_GTA_1: 7 missing
  - Prod_EE_GTA_1: 7 missing
  - Admission_HP_GTA_2: 7 missing
  - Soutirage_MP_GTA_2: 14 missing ⚠️ (most)
  - Prod_EE_GTA2_2: 7 missing
  - Admission_HP_GTA_3: 7 missing
  - Soutirage_MP_GTA_3: 7 missing
  - Prod_EE_GTA_3: 7 missing

Total missing: 70 / 435,546 total values (0.016%)
Missing rate: Negligible but present
```

**Visual Evidence:**
- See: `PHASE1_FINDINGS.md` - Dataset Overview section
- Can provide timestamps of missing values if needed

**Why This Matters:**
Different imputation strategies could affect model training and recommendations.

---

### ❓ Question 8: Data Representativeness

**Question:**
"The provided dataset spans January 2024 to May 2025. Does this data represent:
- Normal operations only, or does it include maintenance, startup, and emergency events?
- All operating conditions we should optimize for?
- Should we weight recent data more heavily (system improvements, changing demand patterns)?"

**Evidence Supporting This Question:**

```
Data Coverage Analysis:

Time span: 504 days (16.5 months)
Records: 48,394 at 15-minute intervals
Coverage: Continuous with minimal gaps

Operational Variability Observed:
  - Total HP Steam: 3.4 to 655.2 tons/hour (190x range)
  - Total MP Steam: 0 to 543.1 tons/hour
  - Total Energy: -98.3 to 102.8 MWh

Zero/Near-Zero Periods:
  - Several periods with HP < 10 tons/hour across GTAs
  - Suggests shutdowns or maintenance windows
  - Should these be included in optimization scope?
```

**Visual Evidence:**
- See: `outputs/figures/time_series_overview.png` - Full operational history
- See: `outputs/figures/system_totals.png` - System-wide trends

**Why This Matters:**
If the data includes abnormal events, we may want to filter them out or handle them separately in the optimization model.

---

## Section 4: Optimization Objectives

### ❓ Question 9: Primary Optimization Goal

**Question:**
"The challenge states we should 'maximize energy production while respecting operational constraints.' However, given the trade-offs we've identified, can you clarify the priority order:

1. Must satisfy minimum MP steam demand first, then maximize energy?
2. Maximize energy production as primary goal, with MP as a constraint?
3. Multi-objective optimization (balance both)?
4. Economic optimization (if you can share energy prices and MP steam value)?"

**Evidence Supporting This Question:**

```
Observed Trade-off Analysis:

Scenario 1: High MP Extraction
  - Avg MP: 431 tons/hour (75th percentile)
  - Avg Energy: 65.1 MWh
  - MP/Energy ratio: High

Scenario 2: Lower MP Extraction
  - Avg MP: 309 tons/hour (25th percentile)
  - Avg Energy: 47.6 MWh
  - MP/Energy ratio: Lower

Current Operations:
  - Median total MP: 350.9 tons/hour
  - Median total Energy: 55.9 MWh
  - Shows current balance point
```

**Why This Matters:**
Optimization algorithm design depends entirely on objective function definition. Different goals require different mathematical formulations.

---

### ❓ Question 10: Chatbot Use Cases

**Question:**
"The challenge requires a chatbot interface for scenario evaluation. Can you describe:
- What are the top 3-5 scenarios plant managers want to test?
- Example questions they would ask (e.g., 'What if we reduce sulfuric acid cadence by 20%')?
- What decisions should the chatbot help them make?
- What time horizon (real-time recommendations vs. planning for next shift/day/week)?"

**Evidence Supporting This Question:**

```
Current Analysis Capabilities:

Our Phase 1 analysis can answer:
  ✓ "What's the current efficiency of each GTA?"
  ✓ "What's the average energy production by hour of day?"
  ✓ "How much MP steam are we extracting vs. optimal?"
  ✓ "What happens if GTA_2 goes offline?"

Mentioned in challenge doc:
  - "Reduce sulfuric cadence by 20%?" (need clarification)
  - "Increase MP steam consumption?" (understood)
  - "What-if scenarios" (need examples)
  - "Real-time recommendations" (time scale?)
```

**Why This Matters:**
Chatbot design requires knowing actual user workflows and questions. We want to build what managers will actually use, not theoretical features.

---

## Section 5: Technical Implementation

### ❓ Question 11: Local LLM Requirements

**Question:**
"The challenge specifies the chatbot must be 'implemented locally (not via API).' Can you clarify:
- Can we use locally-hosted open-source LLMs (e.g., Llama, Mistral via Ollama)?
- What are the deployment hardware constraints?
- Is internet access allowed for installation/updates, just not for runtime API calls?
- Any preferences on frameworks (LangChain, LlamaIndex, custom)?"

**Why This Matters:**
We need to choose the right tech stack. Local LLMs (Ollama) vs. rule-based systems vs. hybrid approaches have different trade-offs.

---

### ❓ Question 12: Deliverable Format

**Question:**
"For the hackathon submission, what format do you expect:
- Web application (Streamlit, Gradio, Flask)?
- Desktop application?
- Jupyter notebook with interactive widgets?
- API + frontend?
- What level of polish is expected (prototype vs. production-ready)?"

**Why This Matters:**
Affects time allocation between algorithm development and UI polish.

---

## Section 6: Domain-Specific Clarifications

### ❓ Question 13: Sulfuric Acid Process

**Question:**
"The challenge documentation mentions 'sulfuric acid cadence' in the example scenario. Can you explain:
- What is the sulfuric acid production process relationship to steam?
- How does changing sulfuric acid cadence affect HP/MP steam demand?
- Are there other industrial processes we should understand?
- Should the model account for these processes explicitly?"

**Evidence Supporting This Question:**

```
Current Understanding Gap:

We understand:
  ✓ HP steam → GTA → Electricity + MP steam
  ✓ MP steam → Industrial consumers
  ✓ Trade-off between energy and MP extraction

We DON'T understand:
  ✗ What "sulfuric acid cadence" means
  ✗ How it affects steam demand
  ✗ Other industrial processes consuming MP steam
  ✗ Whether these are modeled in the data
```

**Why This Matters:**
If the chatbot needs to answer "What if we reduce sulfuric acid production by 20%", we need to know how that maps to MP steam demand changes.

---

### ❓ Question 14: Steam Quality Parameters

**Question:**
"Does the optimization need to consider:
- Steam temperature and pressure (beyond HP/MP designation)?
- Steam quality/dryness?
- Condensate return?
- Or can we treat steam purely as a flow rate optimization problem?"

**Why This Matters:**
Determines model complexity - flow rates only vs. thermodynamic modeling.

---

## Section 7: Success Criteria

### ❓ Question 15: Evaluation Metrics

**Question:**
"How will hackathon solutions be evaluated? What's the priority order:
- Optimization algorithm quality (% improvement over baseline)?
- Chatbot user experience and usefulness?
- Technical innovation?
- Practical deployability?
- Presentation quality?

Can you share the judging rubric or key criteria?"

**Why This Matters:**
Helps us allocate effort between optimization model sophistication, chatbot features, and presentation materials.

---

## Recommended Approach Based on Their Answers

### If They Say: "Use stated constraints (100 t/h MP limit)"
**Our Response:**
"Understood. We'll enforce these as hard constraints, but note that this means we can only train on 0.11% of the provided data. We recommend using the stated constraints as optimization targets/goals while training on realistic data."

### If They Say: "Use data-derived constraints"
**Our Response:**
"Perfect. We'll use 95th percentile values from the data as realistic operational bounds, which keeps 97% of data for training while filtering extreme outliers."

### If They Say: "Those aren't anomalies, that's normal operation"
**Our Response:**
"Excellent clarification. We'll use the full dataset and update our constraint documentation to reflect actual operational ranges rather than theoretical limits."

---

## Visual Aids to Bring to Meeting

1. **Print/Show:**
   - `outputs/figures/anomaly_timeline.png` - Shows constraint violations
   - `outputs/figures/distribution_analysis.png` - Shows actual value distributions
   - `outputs/figures/efficiency_comparison.png` - Shows GTA differences
   - `PHASE1_FINDINGS.md` - Summary of analysis

2. **Have Ready on Laptop:**
   - All visualizations in `outputs/figures/`
   - `ANOMALY_DECISION.md` - Constraint analysis
   - Jupyter notebook for ad-hoc queries if they ask specific questions

---

## Summary of Key Asks

**MOST CRITICAL (Must Have):**
1. ✅ Clarify MP steam extraction limits (100 t/h vs. observed 265 t/h)
2. ✅ Define optimization priority (energy vs. MP steam vs. both)
3. ✅ Explain negative energy values

**IMPORTANT (Should Have):**
4. ✅ Clarify GTA load balancing constraints
5. ✅ Define chatbot use cases and example scenarios
6. ✅ Explain sulfuric acid process relationship

**NICE TO HAVE:**
7. ✅ Data quality handling guidance
8. ✅ Evaluation criteria for judging
9. ✅ Technical implementation preferences

---

## Suggested Meeting Flow

1. **Start with appreciation** (30 seconds)
   - "Thank you for providing such a rich dataset with 48K records"

2. **Lead with biggest issue** (2 minutes)
   - Show anomaly_timeline.png
   - Explain 89% of data exceeds MP constraint
   - Ask Question 1 about constraints

3. **Clarify optimization objectives** (3 minutes)
   - Ask Questions 6 and 9 about trade-offs and priorities

4. **Domain-specific questions** (2-3 minutes)
   - Ask Question 13 about sulfuric acid process
   - Ask Question 10 about chatbot scenarios

5. **Technical clarifications** (2 minutes)
   - Ask Question 11 about local LLM requirements
   - Ask Question 12 about deliverable format

6. **Wrap up** (1 minute)
   - Confirm next steps
   - Ask for any additional resources/documentation

**Total Time: 10-15 minutes**

---

**Prepared by**: Data Analysis Phase 1
**Files Referenced**: All visualizations in `outputs/figures/`, PHASE1_FINDINGS.md, ANOMALY_DECISION.md
**Data Source**: Data_Energie.csv (48,394 records, Jan 2024 - May 2025)
