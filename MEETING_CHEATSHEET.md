# Hackathon Meeting Cheat Sheet - Quick Reference

**Date**: Nov 28, 2025 | **Your Name**: _____________ | **Dataset**: Data_Energie.csv (48,394 records)

---

## 🔴 TOP 3 CRITICAL QUESTIONS (MUST ASK)

### 1. GTA_2 Extended Downtime ⚠️ **NEW - MOST CRITICAL**
**Question**: "GTA_2 has been completely offline since Nov 8, 2024 (191 consecutive days to end of dataset). Is this expected? Should we model for 2 or 3 operational GTAs?"

**Proof**:
- GTA_2 uptime: Only 61.5% of dataset
- Continuous downtime: Nov 8, 2024 → May 19, 2025 (191 days)
- This is the entire last 6 months of data!

**Show**: `operational_timeline.png` ⭐ **MUST SHOW THIS FIRST**

---

### 2. MP Steam Constraint Mismatch ⚠️
**Question**: "Max MP constraint is 100 t/h, but data shows median of 147 t/h and max 265 t/h. Use stated limit or data-derived limits?"

**Proof**:
- 89.7% of GTA_1 data violates 100 t/h limit
- Even median (50th percentile) = 147 t/h
- Enforcing 100 t/h leaves only 55 records (0.11% of data)

**Show**: `anomaly_timeline.png`, `distribution_analysis.png`

---

### 3. Correlation Analysis (UPDATED) ⚠️
**Question**: "When we filter downtime, MP↔Energy correlation changes from -0.31 to +0.05. What's the actual relationship?"

**Proof**:
- All data (with downtime): MP↔Energy = -0.31 to 0.20
- Operational only: MP↔Energy = -0.004 to 0.05 (essentially zero!)
- Downtime distorted previous analysis

**Show**: `correlation_comparison.png`

---

## 📊 KEY DATA FACTS (Memorize These)

| Metric | Value | Implication |
|--------|-------|-------------|
| Total records | 48,394 | 15-min intervals, 504 days |
| Missing values | 70 (0.016%) | Excellent data quality |
| MP violations | 60-90% of data | Constraints don't match reality |
| GTA_1 production | 1.11M MWh | Highest producer |
| System avg energy | 54.5 MWh | Baseline for optimization |
| Correlation MP↔Energy | -0.12 to -0.31 | Trade-off exists |

---

## 💡 QUESTIONS BY PRIORITY

### TIER 1: Must Have Answers
- [ ] Q1: MP steam limits (100 vs 265 t/h)?
- [ ] Q2: Optimization priority (energy vs MP)?
- [ ] Q3: Negative energy values explanation?
- [ ] Q4: GTA load balancing allowed?
- [ ] Q5: Chatbot scenario examples?

### TIER 2: Important
- [ ] Q6: Sulfuric acid process explanation?
- [ ] Q7: Data quality - how to handle missing values?
- [ ] Q8: Local LLM tech stack preferences?
- [ ] Q9: Deliverable format (web app, notebook)?
- [ ] Q10: Judging criteria/rubric?

### TIER 3: Nice to Have
- [ ] Q11: Steam quality parameters matter?
- [ ] Q12: Economic data (energy prices)?
- [ ] Q13: Data representativeness?

---

## 📈 VISUALIZATIONS TO SHOW

**Primary Evidence**:
1. `anomaly_timeline.png` → Violations aren't rare spikes
2. `distribution_analysis.png` → Actual value ranges
3. `correlation_analysis.png` → Trade-offs exist
4. `efficiency_comparison.png` → GTA differences

**Backup**:
5. `system_totals.png` → Overall trends
6. `temporal_patterns.png` → Time-based patterns

---

## 🎯 RECOMMENDED APPROACHES (Based on Their Answers)

### If they say: "Enforce 100 t/h limit"
➜ "OK, but only 55 records remain. Recommend using as target, not hard limit."

### If they say: "Use realistic constraints"
➜ "Great! We'll use 95th percentile: ~185 t/h MP, keeps 97% of data."

### If they say: "Maximize energy"
➜ "Understood. MP steam becomes a constraint, not objective."

### If they say: "Balance both"
➜ "We'll use multi-objective optimization with weighted function."

---

## 📋 MEETING FLOW (10 minutes)

**0:00-0:30** - Thank them for rich dataset

**0:30-3:00** - Show `anomaly_timeline.png`, ask Q1 (MP limits)

**3:00-5:00** - Ask Q2 (optimization priority) + Q5 (chatbot scenarios)

**5:00-7:00** - Ask Q3 (negative values) + Q6 (sulfuric acid)

**7:00-9:00** - Ask Q8 (tech stack) + Q10 (judging criteria)

**9:00-10:00** - Confirm next steps, ask for additional resources

---

## 🔢 QUICK STATS FOR REFERENCE

### Constraint Violations
| Constraint | GTA_1 | GTA_2 | GTA_3 |
|-----------|-------|-------|-------|
| MP > 100 t/h | 89.7% | 61.1% | 85.2% |
| HP < 90 t/h | 3.2% | 38.6% | 8.2% |

### Percentiles (MP Steam)
| Percentile | GTA_1 | GTA_2 | GTA_3 | Constraint |
|-----------|-------|-------|-------|------------|
| 50th | 147 | 146 | 142 | **100** |
| 95th | 184 | 172 | 175 | **100** |
| Max | 265 | 179 | 182 | **100** |

### GTA Performance
| GTA | Avg HP | Avg MP | Total Energy | Rank |
|-----|--------|--------|--------------|------|
| GTA_1 | 184 | 140 | 1.11M MWh | 🥇 Best |
| GTA_2 | 122 | 98 | 0.67M MWh | 🥉 Lowest |
| GTA_3 | 171 | 130 | 0.85M MWh | 🥈 Middle |

---

## ✅ POST-MEETING TODO

After meeting, update:
- [ ] `config.py` - Set final constraints based on answers
- [ ] `PHASE1_FINDINGS.md` - Add meeting notes
- [ ] Start Phase 2 with clarified objectives

---

## 📞 CONTACT INFO

**Your Info**: _______________________

**Organizer Info**: _______________________

**Follow-up By**: _______________________

---

**Files to Bring**:
- ✅ This cheat sheet (printed)
- ✅ Laptop with all visualizations open
- ✅ MEETING_QUESTIONS.md (detailed version)
- ✅ PHASE1_FINDINGS.md
- ✅ Notebook for notes

**Backup**: USB with all `outputs/figures/` files

---

**Remember**:
- You've done thorough analysis (48K records!)
- Questions are legitimate, not criticism
- Goal: Build practical solution they can deploy
- Be confident but collaborative

**Good luck! 🚀**
