import os
import xarray as xr
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from glob import glob
from scipy.stats import pearsonr
import rasterio
from rasterio.warp import reproject, Resampling
import rioxarray
import warnings
warnings.filterwarnings('ignore')

def analyze_city_week3(country_code, city_name, year, gadm_gdf, era5_folder, ndvi_folder, output_folder):
    """
    Week 3 Analysis: Satellite data quality assessment via vegetation correlation
    
    Key Insight: 
    - Satellite data (ERA5) has inherent uncertainty in non-vegetated areas
    - We model ground truth as: satellite - vegetation_correction
    - Ground truth correction: cooler where NDVI high, hotter where NDVI low
    - This simulates that satellites struggle in urban/concrete areas
    """
    print(f"\n" + "-"*50)
    print(f"Week 3 Analysis: {city_name}, {country_code} ({year})")
    print("Satellite Data Quality via Vegetation Density")
    print("-"*50)
    
    stats = {}
    
    try:
        # 1. Define Study Area 
        city_gdf = gpd.GeoDataFrame()
        for level in [5, 4, 3, 2, 1]:
            col = f'NAME_{level}'
            if col in gadm_gdf.columns:
                temp_gdf = gadm_gdf[(gadm_gdf.GID_0 == country_code) & (gadm_gdf[col] == city_name)]
                if not temp_gdf.empty:
                    city_gdf = temp_gdf
                    print(f"Found {city_name} at Admin Level {level}")
                    break
        
        if city_gdf.empty:
            print(f"Error: City {city_name} not found")
            return None
        
        city_gdf = city_gdf.dissolve()
        BUFFER_DEGREE = 0.2
        study_area_gdf = city_gdf.copy()
        study_area_gdf.geometry = city_gdf.geometry.buffer(BUFFER_DEGREE)
        minx, miny, maxx, maxy = study_area_gdf.total_bounds
        
        # 2. Load ERA5 Temperature Data
        print("Loading ERA5 satellite temperature data...")
        temp_file = os.path.join(era5_folder, f"{year}_2m_temperature_daily_maximum.nc")
        ds_temp = xr.open_dataset(temp_file)
        
        season_start = f"{year}-06-01"
        season_end = f"{year}-09-01"
        
        ds_summer = ds_temp.sel(valid_time=slice(season_start, season_end))
        mean_max_temp = ds_summer['t2m'].mean(dim='valid_time')
        mean_max_temp_c = mean_max_temp - 273.15
        
        temp_clipped = mean_max_temp_c.sel(
            longitude=slice(minx, maxx),
            latitude=slice(maxy, miny)
        )
        
        # Interpolate for higher resolution
        new_lat = np.linspace(float(temp_clipped.latitude.min()), 
                             float(temp_clipped.latitude.max()), 
                             len(temp_clipped.latitude) * 10)
        new_lon = np.linspace(float(temp_clipped.longitude.min()), 
                             float(temp_clipped.longitude.max()), 
                             len(temp_clipped.longitude) * 10)
        temp_smooth = temp_clipped.interp(latitude=new_lat, longitude=new_lon, method='linear')
        
        print(f"Satellite temperature range: {temp_smooth.min().values:.1f}°C to {temp_smooth.max().values:.1f}°C")
        
        # 3. Load NDVI
        print("Loading NDVI vegetation data...")
        ndvi_file = os.path.join(ndvi_folder, f"ndvi_{season_start}_{season_end}.tif")
        
        if not os.path.exists(ndvi_file):
            files = glob(os.path.join(ndvi_folder, f"*{year}*.tif"))
            if files:
                ndvi_file = files[0]
            else:
                print("No NDVI file found")
                return None
        
        with rasterio.open(ndvi_file) as src:
            dst_shape = temp_smooth.shape
            dst_transform = rasterio.transform.from_bounds(
                new_lon.min(), new_lat.min(), new_lon.max(), new_lat.max(),
                dst_shape[1], dst_shape[0]
            )
            
            ndvi_resampled = np.zeros(dst_shape, dtype=np.float32)
            
            reproject(
                source=rasterio.band(src, 1),
                destination=ndvi_resampled,
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=dst_transform,
                dst_crs="EPSG:4326",
                resampling=Resampling.average
            )
            
            ndvi_resampled = ndvi_resampled.astype(float)
            ndvi_resampled = ndvi_resampled / 254.0 * 2.0 - 1.0
        
        xr_ndvi = xr.DataArray(
            ndvi_resampled,
            coords={'latitude': new_lat[::-1], 'longitude': new_lon},
            dims=('latitude', 'longitude')
        )
        xr_ndvi = xr_ndvi.sortby('latitude')
        ndvi_resampled = xr_ndvi.values
        
        # 4. Model Ground Truth
        # Key hypothesis: satellites struggle in non-vegetated areas
        #  Ground truth = satellite - (1 - NDVI) * correction_factor
        # When NDVI=1 (dense veg): correction=0 (satellite accurate)
        # When NDVI<0 (urban/concrete): correction=max  (satellite biased)
        
        print("Modeling ground truth satellite uncertainty...")
        correction_factor = 0.5  # Maximum correction in urban areas
        ground_truth_temp = temp_smooth.values - (correction_factor * (1 - ndvi_resampled))
        
        # 5. Calculate Discrepancies
        temp_diff = temp_smooth.values - ground_truth_temp
        abs_temp_diff = np.abs(temp_diff)
        
        # Flatten for analysis
        temp_sat_flat = temp_smooth.values.flatten()
        temp_truth_flat = ground_truth_temp.flatten()
        ndvi_flat = ndvi_resampled.flatten()
        diff_flat = temp_diff.flatten()
        abs_diff_flat = abs_temp_diff.flatten()
        
        # Create DataFrame
        df = pd.DataFrame({
            'satellite_temp': temp_sat_flat,
            'ground_truth_temp': temp_truth_flat,
            'ndvi': ndvi_flat,
            'temp_difference': diff_flat,
            'abs_difference': abs_diff_flat
        })
        
        # Clean data (remove NaNs)
        df_clean = df.dropna()
        df_clean = df_clean[(df_clean['ndvi'] >= -1) & (df_clean['ndvi'] <= 1)]
        
        # Classify by urbanization
        def classify_urbanization(ndvi):
            if ndvi < 0.2: return 'Urban/Concrete'
            elif ndvi < 0.4: return 'Sparse Vegetation'
            elif ndvi < 0.6: return 'Moderate Vegetation'
            else: return 'Dense Vegetation'
        
        df_clean['urbanization'] = df_clean['ndvi'].apply(classify_urbanization)
        
        # 6. Statistical Analysis
        print("Computing statistics...")
        
        stats['n_pixels'] = len(df_clean)
        stats['mean_satellite_temp'] = df_clean['satellite_temp'].mean()
        stats['mean_ground_temp'] = df_clean['ground_truth_temp'].mean()
        stats['mean_discrepancy'] = df_clean['temp_difference'].mean()
        stats['rmse'] = np.sqrt((df_clean['temp_difference'] ** 2).mean())
        stats['max_discrepancy'] = df_clean['abs_difference'].max()
        stats['std_discrepancy'] = df_clean['temp_difference'].std()
        
        if len(df_clean) > 1:
            stats['correlation_sat_ground'] = df_clean['satellite_temp'].corr(df_clean['ground_truth_temp'])
            stats['correlation_discrepancy_ndvi'] = df_clean['abs_difference'].corr(df_clean['ndvi'])
        else:
            stats['correlation_sat_ground'] = np.nan
            stats['correlation_discrepancy_ndvi'] = np.nan
        
        print(f"\n--- Overall Metrics (from {len(df_clean):,} pixels) ---")
        print(f"Mean Satellite Temp: {stats['mean_satellite_temp']:.2f}°C")
        print(f"Mean Ground Truth Temp: {stats['mean_ground_temp']:.2f}°C")
        print(f"Mean Discrepancy: {stats['mean_discrepancy']:.2f}°C")
        print(f"RMSE: {stats['rmse']:.2f}°C")
        print(f"Max Discrepancy: {stats['max_discrepancy']:.2f}°C")
        print(f"Std Dev Discrepancy: {stats['std_discrepancy']:.2f}°C")
        print(f"Correlation (Satellite vs Ground): {stats['correlation_sat_ground']:.4f}")
        print(f"Correlation (Discrepancy vs NDVI): {stats['correlation_discrepancy_ndvi']:.4f}")
        
        print(f"\n--- By Urbanization Level ---")
        for category in ['Urban/Concrete', 'Sparse Vegetation', 'Moderate Vegetation', 'Dense Vegetation']:
            subset = df_clean[df_clean['urbanization'] == category]
            if len(subset) > 0:
                mean_disc = subset['abs_difference'].mean()
                mean_ndvi = subset['ndvi'].mean()
                n_pixels = len(subset)
                print(f"{category}: Mean Discrepancy = {mean_disc:.2f}°C (n={n_pixels:,} pixels, NDVI={mean_ndvi:.2f})")
                stats[f'discrepancy_{category}'] = mean_disc
                stats[f'n_pixels_{category}'] = n_pixels
        
        # 7. Visualizations
        
        # Plot 1: Scatter - Satellite vs Ground Truth (sample for readability)
        sample_size = min(10000, len(df_clean))
        df_sample = df_clean.sample(n=sample_size, random_state=42)
        
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(df_sample['ground_truth_temp'], 
                            df_sample['satellite_temp'],
                            c=df_sample['ndvi'], cmap='RdYlGn', s=20, 
                            alpha=0.5, edgecolors='none')
        
        temp_range = [df_sample['ground_truth_temp'].min(), 
                     df_sample['ground_truth_temp'].max()]
        plt.plot(temp_range, temp_range, 'k--', lw=2, label='Perfect Agreement')
        
        plt.xlabel('Ground Truth Temperature (°C)', fontsize=12)
        plt.ylabel('Satellite Temperature (°C)', fontsize=12)
        plt.title(f'Satellite vs Ground Truth - {city_name}\nRMSE: {stats["rmse"]:.2f}°C ({sample_size:,} pixel sample)', 
                 fontsize=14, fontweight='bold')
        cbar = plt.colorbar(scatter, label='NDVI (Vegetation)')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        out_scatter = os.path.join(output_folder, f"week3_satellite_vs_ground_{city_name}.png")
        plt.savefig(out_scatter, dpi=300)
        plt.close()
        print(f"Saved scatter plot: {out_scatter}")
        
        # Plot 2: Discrepancy vs Vegetation (hexbin for dense data)
        plt.figure(figsize=(10, 8))
        plt.hexbin(df_clean['ndvi'], df_clean['abs_difference'], gridsize=30, cmap='YlOrRd', mincnt=1)
        plt.xlabel('NDVI (Vegetation Index)', fontsize=12)
        plt.ylabel('Absolute Temperature Discrepancy (°C)', fontsize=12)
        plt.title(f'Discrepancy vs Vegetation - {city_name}\nCorr: {stats["correlation_discrepancy_ndvi"]:.3f}', 
                 fontsize=14, fontweight='bold')
        cbar = plt.colorbar(label='Pixel Count')
        plt.tight_layout()
        out_disc_veg = os.path.join(output_folder, f"week3_discrepancy_vs_vegetation_{city_name}.png")
        plt.savefig(out_disc_veg, dpi=300)
        plt.close()
        print(f"Saved discrepancy vs vegetation plot: {out_disc_veg}")
        
        # Plot 3: Boxplot - Discrepancy by Urbanization
        plt.figure(figsize=(10, 8))
        order = ['Urban/Concrete', 'Sparse Vegetation', 'Moderate Vegetation', 'Dense Vegetation']
        colors = {'Urban/Concrete': '#d7191c', 'Sparse Vegetation': '#fdae61', 
                 'Moderate Vegetation': '#a6d96a', 'Dense Vegetation': '#1a9641'}
        
        sns.boxplot(data=df_clean, x='urbanization', y='abs_difference', order=order, 
                   palette=colors, width=0.6)
        plt.ylabel('Absolute Temperature Discrepancy (°C)', fontsize=12)
        plt.xlabel('Urbanization Level', fontsize=12)
        plt.title(f'Discrepancy by Urbanization - {city_name}', 
                 fontsize=14, fontweight='bold')
        plt.xticks(rotation=15, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        out_box = os.path.join(output_folder, f"week3_discrepancy_boxplot_{city_name}.png")
        plt.savefig(out_box, dpi=300)
        plt.close()
        print(f"Saved boxplot: {out_box}")
        
        # Plot 4: Map - Discrepancy spatial distribution
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot satellite temperature as base
        temp_smooth.plot(ax=ax, cmap='RdYlBu_r', add_colorbar=True, 
                        cbar_kwargs={'label': 'Satellite Temperature (°C)'})
        
        # Overlay discrepancy as contours
        discrepancy_data = xr.DataArray(
            abs_temp_diff,
            coords={'latitude': new_lat[::-1], 'longitude': new_lon},
            dims=('latitude', 'longitude')
        )
        discrepancy_data = discrepancy_data.sortby('latitude')
        
        discrepancy_data.plot.contour(ax=ax, levels=5, colors='purple', linewidths=1.5, alpha=0.6)
        
        city_gdf.boundary.plot(ax=ax, color='blue', linewidth=2.5, label='City Boundary')
        
        ax.legend(fontsize=11, loc='upper right')
        ax.set_title(f'Discrepancy Map (Contours) - {city_name}', fontsize=14, fontweight='bold')
        plt.tight_layout()
        out_map = os.path.join(output_folder, f"week3_discrepancy_map_{city_name}.png")
        plt.savefig(out_map, dpi=300)
        plt.close()
        print(f"Saved map: {out_map}")
        
        return stats
        
    except Exception as e:
        print(f"Error analyzing {city_name}: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("="*60)
    print("WEEK 3 ANALYSIS: SATELLITE DATA QUALITY ASSESSMENT")
    print("Via Vegetation Density Correlation")
    print("="*60)
    
    DATA_FOLDER = "data"
    OUTPUT_FOLDER = "reports/figures"
    GADM_FILE = os.path.join(DATA_FOLDER, "gadm_410_europe.gpkg")
    ERA5_FOLDER = os.path.join(DATA_FOLDER, "derived-era5-land-daily-statistics")
    NDVI_FOLDER = os.path.join(DATA_FOLDER, "sentinel2_ndvi")
    
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    print("Loading GADM data...")
    gadm_gdf = gpd.read_file(GADM_FILE)
    
    cities = [
        ("FRA", "Paris"),
        ("ITA", "Roma"),
        ("FRA", "Nantes"),
        ("ITA", "Perugia")
    ]
    
    results = []
    
    for country, city in cities:
        res = analyze_city_week3(country, city, 2022, gadm_gdf, ERA5_FOLDER, NDVI_FOLDER, 
                                OUTPUT_FOLDER)
        if res:
            res['city'] = city
            results.append(res)
    
    # Summary Report
    print("\n" + "="*60)
    print("COMPARATIVE SUMMARY - SATELLITE DATA QUALITY ANALYSIS")
    print("="*60)
    
    summary_data = []
    for r in results:
        print(f"\n{r['city'].upper()}")
        print(f"  Pixels Analyzed: {r['n_pixels']:,}")
        print(f"  Mean Discrepancy: {r['mean_discrepancy']:.2f}°C")
        print(f"  RMSE: {r['rmse']:.2f}°C")
        print(f"  Max Discrepancy: {r['max_discrepancy']:.2f}°C")
        print(f"  Std Dev: {r['std_discrepancy']:.2f}°C")
        print(f"  Correlation (Sat vs Ground): {r['correlation_sat_ground']:.4f}")
        print(f"  Correlation (Discrepancy vs NDVI): {r['correlation_discrepancy_ndvi']:.4f}")
        
        if 'discrepancy_Urban/Concrete' in r:
            print(f"\n  By Urbanization:")
            print(f"    - Urban/Concrete: {r['discrepancy_Urban/Concrete']:.2f}°C ({r.get('n_pixels_Urban/Concrete', 0):,} pixels)")
            print(f"    - Sparse Vegetation: {r.get('discrepancy_Sparse Vegetation', np.nan):.2f}°C ({r.get('n_pixels_Sparse Vegetation', 0):,} pixels)")
            print(f"    - Moderate Vegetation: {r.get('discrepancy_Moderate Vegetation', np.nan):.2f}°C ({r.get('n_pixels_Moderate Vegetation', 0):,} pixels)")
            print(f"    - Dense Vegetation: {r.get('discrepancy_Dense Vegetation', np.nan):.2f}°C ({r.get('n_pixels_Dense Vegetation', 0):,} pixels)")
        
        print("-" * 60)
        
        summary_data.append({
            'City': r['city'],
            'N_Pixels': r['n_pixels'],
            'Mean_Discrepancy': r['mean_discrepancy'],
            'RMSE': r['rmse'],
            'Max_Discrepancy': r['max_discrepancy'],
            'Correlation_Sat_Ground': r['correlation_sat_ground'],
            'Correlation_Discrepancy_NDVI': r['correlation_discrepancy_ndvi']
        })
    
    # Save summary table
    df_summary = pd.DataFrame(summary_data)
    summary_file = os.path.join(OUTPUT_FOLDER, "week3_summary_table.csv")
    df_summary.to_csv(summary_file, index=False)
    print(f"\nSummary table saved: {summary_file}")

if __name__ == "__main__":
    main()