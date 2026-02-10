# GenHack 2025 – Urban Heat Island Analysis
## Urban Coolers – École Polytechnique Hackathon (Nov–Dec 2025)

This repository contains our work for GenHack 2025, a four-week hackathon focused on analyzing and explaining the Urban Heat Island (UHI) effect using:

- ERA5 rescaled temperature data
- Sentinel-2 NDVI (vegetation index)
- Ground-station temperature observations

Our goal is to explore discrepancies between datasets, quantify errors, and propose simple explanatory models for improving local temperature estimates.


## 🧠 Project Idea / Subject

### Insights from Charles‑Albert Lehalle (Organizer Talk)

During the meeting, the organizer explained the **core motivation** behind the hackathon challenge:

* ERA5 temperatures are **rescaled/reconstructed** using physical atmospheric models and **infrared data**.
* These reconstructions rely partly on **true temperature observations**, but the final product still contains **systematic errors**.
* Errors tend to be larger in **cities**, **mountain areas**, or **complex terrain** where urban structures or altitude make physical modeling harder.
* To assess the **quality** of ERA5 rescaled temperatures, we must compare them to **ground‑truth station data**.
* To understand how **urbanism** impacts temperature accuracy, we use **NDVI (biomass)** maps from satellite imagery.
* Hypothesis:
  **ERA5 temperature is more accurate in areas with vegetation (high biomass) and less accurate in dense urban zones (low biomass) due to the Urban Heat Island effect.**
* Our mission is to verify this relationship by turning the data into meaningful **plots, metrics, and maps**.

This forms the conceptual foundation for the entire hackathon.
GenHack 2025 is an international hackathon focused on understanding and modeling the **Urban Heat Island (UHI)** effect across Europe using satellite and climate data.

The goal is to:

* Compare **ERA5** rescaled temperature data with **ground‑station observations**.
* Study how **vegetation (NDVI)** affects temperature discrepancies.
* Build visualizations, metrics, and simple explanatory models.
* Provide insights that can help cities better understand and mitigate UHI.

# Checkout my work in these files:
Notebooks/ 
* week1_team19.ipynb
* week2_team19.ipynb
* week3_team19.ipynb
* week4_team19.ipynb

Slides/
* week1_team19.pdf
* week2_team19.pdf
* week3_team19.pdf
* week4_team19.pdf
