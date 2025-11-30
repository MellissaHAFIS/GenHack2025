# Week 2 Report: Urban Heat Island Visualization & Communication
## Berlin, Germany Analysis

---

## Executive Summary

This report presents a comprehensive visualization and analysis of the Urban Heat Island (UHI) effect in Berlin, Germany, using ERA5 reanalysis data, ground station observations, and Sentinel-2 NDVI measurements from 2020-2023. Our analysis reveals a **measurable urban heat island** with mean intensity of **+0.34°C**, clear **vegetation-temperature relationships**, and important implications for urban climate monitoring.

---

## 1. Introduction

### 1.1 Study Area: Berlin & Brandenburg
- **Berlin**: Capital city, 893 km², ~3.7 million inhabitants
- **Brandenburg**: Surrounding rural state, 29,697 km², ~2.5 million inhabitants
- **Climate**: Temperate continental with distinct seasonal patterns

### 1.2 Research Question
*How does urbanization in Berlin affect local climate patterns, and how well do current climate models capture these effects?*

---

## 2. Data & Methodology

### 2.1 Multi-Source Data Integration
- **ERA5-Land**: Daily maximum temperatures (2020-2023), ~9km resolution
- **Ground Stations**: 80 carefully selected stations across urban-rural gradient
- **Sentinel-2 NDVI**: 16 quarterly measurements, 80m resolution
- **Administrative Boundaries**: GADM database for spatial analysis

### 2.2 Station Classification
- **Urban** (8 stations): Within Berlin city, <10km from center
- **Suburban** (14 stations): Berlin outskirts, 10-30km from center  
- **Rural** (58 stations): Brandenburg countryside, 30-200km from center

---

## 3. Results & Visualization

### 3.1 Spatial Patterns: The Urban Heat Island Signature

**Visualization 1: Germany National Overview** (`01_germany_national_map.png`)
- Shows station network density across Germany
- Highlights Berlin as focus area with high station concentration
- Color gradient indicates distance from Berlin center

**Visualization 2: Brandenburg Regional NDVI** (`02_brandenburg_regional_ndvi.png`)
- Clear vegetation gradient from urban Berlin to rural Brandenburg
- Berlin appears as distinct low-NDVI (red/orange) area
- Surrounding Brandenburg shows higher vegetation (green)

**Visualization 3: Berlin City Detail** (`03_berlin_city_detail.png`)
- High-resolution analysis of Berlin's urban structure
- Combines NDVI (vegetation) with ERA5 temperature patterns
- Identifies specific urban heat islands within the city

**Key Finding**: Berlin shows a distinct "heat signature" visible at multiple spatial scales, from regional to city level.

### 3.2 Urban-Rural Temperature Gradient

**Visualization 4: Urban-Rural Transect** (`04_urban_rural_transect.png`)
- Clear temperature decrease with distance from urban core
- Strongest UHI effects within 15km of city center
- Gradient analysis shows smooth transition from urban to rural climates

**Quantitative Results**:
- **Mean UHI Intensity**: +0.34°C (Berlin warmer than rural reference)
- **Maximum UHI**: +12.10°C (extreme summer event)
- **Seasonal Variation**: 
  - Summer: +0.54°C
  - Winter: +0.14°C
  - Spring: +0.53°C  
  - Fall: +0.15°C

### 3.3 Seasonal Patterns & Temporal Evolution

**Visualization 5: Seasonal Comparison** (`05_seasonal_comparison.png`)
- UHI strongest during summer months
- Consistent seasonal pattern across all years
- Winter UHI nearly negligible

**Visualization 6: NDVI Time Series** (`06_ndvi_time_series.png`)
- Clear seasonal vegetation cycle in both Berlin and Brandenburg
- Persistent urban-rural NDVI gap of 0.113
- Berlin consistently shows 20% less vegetation than surrounding areas

**Key Finding**: Urban heat island effects are not constant—they vary significantly by season, with strongest effects during summer when cooling demand is highest.

### 3.4 Model Performance Assessment

**Visualization 7: ERA5-Station Scatter** (`07_era5_station_scatter.png`)
- High correlation (0.993) between ERA5 and observations
- Systematic cold bias: ERA5 underestimates temperatures by -0.97°C on average
- Good performance across all station types

**Visualization 8: Error Distribution** (`08_error_distribution.png`)
- Error distribution follows approximately normal pattern
- RMSE of 1.50°C indicates good model accuracy
- Similar performance across urban, suburban, and rural stations

**ERA5 Performance by Station Type**:
| Category | Mean Bias | RMSE | Correlation |
|----------|-----------|------|-------------|
| Urban    | -0.98°C   | 1.41°C | 0.994       |
| Suburban | -1.03°C   | 1.49°C | 0.992       |
| Rural    | -0.95°C   | 1.51°C | 0.993       |

### 3.5 Vegetation-Temperature Relationships

**Visualization 9: NDVI-Error Correlation** (`09_ndvi_error_correlation.png`)
- Examines relationship between vegetation density and model accuracy
- Urban areas (low NDVI) show slightly different error patterns
- No strong correlation between NDVI and ERA5 bias

**Vegetation Analysis**:
- **Berlin mean NDVI**: 0.450 (mixed urban-suburban)
- **Brandenburg mean NDVI**: 0.563 (rural-vegetated)
- **Urban-rural gap**: 0.113 (20% less vegetation in Berlin)

---

## 4. Key Insights & Discussion

### 4.1 The Berlin Urban Heat Island: Quantified
- **Moderate but measurable** UHI effect at +0.34°C mean intensity
- **Seasonally variable** - nearly 4x stronger in summer than winter
- **Spatially consistent** - affects entire urban area, not just city center

### 4.2 Vegetation's Role in Urban Climate
- Clear **urban-rural vegetation gradient** exists
- Berlin has **20% less vegetation** than surrounding countryside
- However, vegetation density alone doesn't strongly predict ERA5 errors

### 4.3 ERA5 Model: Strengths and Limitations
- **Excellent** at capturing regional temperature patterns (r=0.993)
- **Systematic cold bias** of nearly 1°C across all areas
- **Coarse resolution** (9km) limits urban-scale applications
- Berlin fits in only **2-3 ERA5 grid cells**, explaining limited urban representation

### 4.4 Implications for Urban Planning
1. **Summer heat management** crucial given strong seasonal UHI
2. **Vegetation strategies** could help mitigate extreme urban heating
3. **High-resolution monitoring** needed for city-scale climate assessments
4. **Model downscaling** required for accurate urban climate projections

---

## 5. Technical Implementation

### 5.1 Visualization Strategy
Our multi-scale approach successfully communicated complex climate patterns:
- **National context** → **Regional patterns** → **Urban detail**
- **Static maps** for spatial patterns + **Time series** for temporal evolution
- **Statistical plots** for model validation + **Correlation analysis** for relationships

### 5.2 Data Integration Challenges
- **Coordinate system alignment** across datasets
- **Temporal matching** of quarterly NDVI with daily temperatures
- **Spatial resolution** reconciliation (80m vs 9km vs point stations)
- **Station classification** using distance-based urban-rural gradient

---

## 6. Conclusions

### 6.1 Summary of Findings
1. **Berlin exhibits a measurable urban heat island** with mean intensity of +0.34°C
2. **Strong seasonal variation** observed, with summer UHI 4x stronger than winter
3. **Clear vegetation gradient** exists, with Berlin having 20% less vegetation than surroundings
4. **ERA5 performs well regionally** but has systematic cold bias and limited urban resolution
5. **Multi-scale visualization** effectively communicates complex urban climate patterns

### 6.2 Critical Analysis & Areas for Improvement
The Small UHI Signal: Is This Real?
Our +0.34°C mean UHI is surprisingly small. Typical urban heat islands are:

Berlin literature: 2-4°C (nighttime), 1-2°C (daytime average)
Our finding: 0.34°C (all-day maximum temperature)

- Possible explanations:
  - ERA5 resolution problem: At 9km, ERA5 treats most of Berlin as a single grid cell, averaging urban and rural together
  Station distribution: You have 8 urban vs 58 rural stations - the rural reference might be too broad
  - Temperature metric: Using daily maximum (not nighttime minimum where UHI is strongest)
  - Definition issue: How are you calculating UHI? (Urban mean - Rural mean)?
---

## 7. Visualizations Reference

All visualizations are available in the output directory:
1. `01_germany_national_map.png` - Context and station network
2. `02_brandenburg_regional_ndvi.png` - Regional vegetation patterns  
3. `03_berlin_city_detail.png` - Urban-scale analysis
4. `04_urban_rural_transect.png` - Spatial gradient
5. `05_seasonal_comparison.png` - Temporal patterns
6. `06_ndvi_time_series.png` - Vegetation evolution
7. `07_era5_station_scatter.png` - Model validation
8. `08_error_distribution.png` - Statistical analysis
9. `09_ndvi_error_correlation.png` - Relationship analysis
10. `10_summary_dashboard.png` - Comprehensive overview

---

**Report Generated**: November 24, 2025  
**Team**: UrbanCoolers  
**Data Period**: 2020-2023  
**Study Area**: Berlin, Germany & Brandenburg Region  

*This report fulfills the Week 2 deliverable requirements for Visualization & Communication of Urban Heat Island effects in the chosen study area.*