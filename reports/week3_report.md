# Week 3 Presentation: Quantitative Metrics & Discrepancy Analysis

---

## Slide 1: Title & Research Focus

**Week 3: Quantitative Metrics & Discrepancy Analysis**
*From Visualization to Statistical Insight*

**Core Question:**
*"Does Urban Heat Island explain ERA5 discrepancies with ground truth?"*

**Analysis Scope:**
- 286 stations across 5 European cities
- 2020-2023 period
- Multi-variable statistical analysis
- Machine learning feature importance

**Visual:** Overview map showing 5 cities (Berlin, Paris, Milano, Warszawa, Madrid)

---

## Slide 2: The Surprising Finding - Vegetation Doesn't Explain Errors

**NDVI vs ERA5 Bias Analysis**

**Statistical Results:**
- **ANOVA Test**: F=1.054, p=0.369
- **Correlation**: r=0.042, p=0.480
- **95% Confidence Intervals** overlap across all NDVI bins

**Error by Vegetation Density:**
| NDVI Class | Bias (°C) | 95% CI | N Stations |
|------------|-----------|---------|------------|
| Very Low   | -1.630 ± 1.268 | [-2.17, -1.09] | 21 |
| Low        | -1.133 ± 1.015 | [-1.35, -0.92] | 84 |
| Medium     | -1.274 ± 1.242 | [-1.48, -1.07] | 147 |
| High       | -1.235 ± 1.071 | [-1.60, -0.88] | 34 |

**Key Insight**: ✗ **NO significant relationship** between vegetation density and ERA5 errors

**Visual:** Box plots showing error distribution across NDVI classes

---

## Slide 3: Urban vs Rural - No Significant Difference

**Urbanization Category Analysis**

**Error Statistics:**
| Category | Bias (°C) | MAE (°C) | RMSE (°C) | N Stations |
|----------|-----------|----------|-----------|------------|
| Urban    | -1.141 ± 0.830 | 1.361 | 1.635 | 21 |
| Suburban | -0.970 ± 1.441 | 1.722 | 2.017 | 22 |
| Rural    | -1.290 ± 1.159 | 1.766 | 2.086 | 243 |

**Statistical Tests:**
- Urban vs Rural: t=0.576, p=0.565
- Urban vs Suburban: t=-0.473, p=0.639
- All comparisons: **NOT SIGNIFICANT**

**Key Insight**: ✗ **Urbanization category alone doesn't predict ERA5 errors**

**Visual:** Violin plots showing error distributions by urbanization category

---

## Slide 4: Seasonal Patterns Matter Most

**Strong Seasonal Variation in Errors**

**Seasonal Bias Pattern:**
- **Winter**: -0.780 ± 1.196°C
- **Spring**: -1.394 ± 1.252°C  
- **Summer**: -1.689 ± 1.327°C
- **Fall**: -1.005 ± 1.139°C

**Statistical Significance:**
- **ANOVA**: F=30.58, p<0.000001
- **Highly significant** seasonal variation

**Multiplicative Effect:**
- Correlation(Bias, Temperature): r=-0.329, p<0.000001
- **Error scales with temperature** - larger cold bias in warmer conditions

**Visual:** Seasonal error bar charts with confidence intervals

---

## Slide 5: Geographic Variation - City-Level Differences

**Significant Cross-City Variation**

**City Performance:**
| City | Bias (°C) | RMSE (°C) | Elevation (m) | N Stations |
|------|-----------|-----------|---------------|------------|
| Berlin | -0.982 ± 0.201 | 1.490 | 65 | 86 |
| Madrid | -1.299 ± 1.200 | 2.097 | 888 | 87 |
| Milano | -1.590 ± 1.640 | 2.674 | 510 | 88 |
| Paris | -1.018 ± 0.317 | 1.589 | 103 | 5 |
| Warszawa | -0.809 ± 0.347 | 1.588 | 135 | 20 |

**Statistical Test:**
- **ANOVA**: F=3.993, p=0.0036
- **Significant differences** between cities

**Visual:** City comparison bar charts with error bars

---

## Slide 6: The UHI Representation Problem

**ERA5 Underestimates Urban Heat Island**

**UHI Discrepancy Analysis:**
| City | Observed UHI | ERA5 UHI | Discrepancy |
|------|--------------|----------|-------------|
| Berlin | +0.103°C | +0.129°C | +0.025°C |
| Warszawa | +0.791°C | +0.507°C | -0.283°C |
| Madrid | -1.335°C | -4.686°C | -3.351°C |

**Key Findings:**
- **Mean UHI Discrepancy**: -1.203°C
- **ERA5 systematically underestimates** UHI intensity
- **Madrid shows extreme discrepancy** (-3.35°C)

**Interpretation**: ERA5's coarse resolution smooths out urban temperature peaks

**Visual:** UHI comparison scatter plot (Observed vs ERA5)

---

## Slide 7: Machine Learning Reveals True Drivers

**Random Forest Feature Importance**

**Top Predictors of ERA5 Bias:**
1. **Elevation** (29.7%) - Most important
2. **Mean Temperature** (23.3%) - Confirms multiplicative effect
3. **Latitude** (16.8%) - Geographic factor
4. **Distance to Coast** (8.6%) - Maritime influence
5. **Distance to City** (8.0%) - Urbanization proxy
6. **NDVI** (7.8%) - Vegetation (low importance)
7. **Longitude** (5.9%) - Geographic factor

**Model Performance:**
- **R² = 0.235** - Explains 23.5% of error variance
- **Cross-validation consistent**

**Key Insight**: Elevation and temperature are better predictors than urbanization

**Visual:** Feature importance bar chart

---

## Slide 8: Statistical Significance Summary

**Correlation Analysis with ERA5 Bias**

**Significant Correlations:**
- ✓ **Mean Temperature**: r=-0.329, p<0.000001 (***)
- ✓ **Latitude**: r=+0.162, p=0.006 (**)
- ✓ **Distance to Coast**: r=-0.161, p=0.006 (**)
- ✓ **Distance to City**: r=-0.121, p=0.041 (*)

**Non-Significant Correlations:**
- ✗ **NDVI**: r=+0.042, p=0.480
- ✗ **Elevation**: r=+0.024, p=0.689
- ✗ **Longitude**: r=+0.082, p=0.165

**Key Insight**: Atmospheric and geographic factors matter more than surface characteristics

**Visual:** Correlation matrix heatmap

---

## Slide 9: Overall ERA5 Performance Metrics

**Comprehensive Accuracy Assessment**

**Overall Statistics:**
- **Mean Bias**: -1.254 ± 1.162°C
- **RMSE**: 2.048°C
- **MAE**: 1.733°C
- **Correlation**: 0.9876

**Error Distribution:**
- Small errors (<1°C): 39.9% of stations
- Medium errors (1-2°C): 42.7% of stations  
- Large errors (≥2°C): 17.5% of stations

**Systematic Pattern:**
- **Consistent cold bias** across all conditions
- **Multiplicative scaling** with temperature
- **Seasonal dependence** strongest factor

**Visual:** Error distribution histogram with percentiles

---

## Slide 10: Key Insights & Week 4 Implications

**Three Major Findings:**

1. **✗ Vegetation Doesn't Explain Errors**
   - No significant NDVI-bias relationship
   - Challenges initial hypothesis

2. **✓ Season & Geography Matter Most**
   - Strong seasonal patterns (p<0.000001)
   - Significant city-level variation (p=0.0036)
   - Elevation is top predictor (29.7% importance)

3. **⚠️ ERA5 Underestimates UHI**
   - Mean discrepancy: -1.203°C
   - Systematic smoothing of urban peaks

**Week 4 Modeling Implications:**
- Focus on **seasonal correction models**
- Incorporate **elevation and temperature scaling**
- Develop **city-specific bias corrections**
- Move beyond vegetation-based explanations

**Visual:** Summary dashboard highlighting key metrics

---

## Presentation Delivery Notes

### Key Numbers to Emphasize:
- **p=0.369** - NDVI non-significance
- **p<0.000001** - Seasonal significance  
- **29.7%** - Elevation feature importance
- **-1.203°C** - UHI underestimation
- **0.9876** - Overall correlation excellence