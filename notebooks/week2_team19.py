import os
import xarray as xr
import pandas as pd
import rasterio
from rasterio.mask import mask
from rasterio.warp import reproject, Resampling
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from glob import glob
from scipy.stats import pearsonr
import rioxarray

def analyze_city(country_code, city_name, year, gadm_gdf, era5_folder, ndvi_folder, output_folder, vmin=None, vmax=None):
    print(f"\n" + "-"*40)
    print(f"Starting Analysis for {city_name}, {country_code} ({year})")
    print("-"*40)
    
    stats = {}

    try:
        # --- 1. Define Study Area ---
        # Filter GADM
        # Search levels 5 down to 1 to find the city/town
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
            print(f"Error: City {city_name} not found in GADM data for {country_code}.")
            return None

        city_gdf = city_gdf.dissolve()
        
        # Create Buffer (approx 20km)
        BUFFER_DEGREE = 0.2
        study_area_gdf = city_gdf.copy()
        study_area_gdf.geometry = city_gdf.geometry.buffer(BUFFER_DEGREE)
        
        minx, miny, maxx, maxy = study_area_gdf.total_bounds
        print(f"Study area defined: {minx:.4f}, {miny:.4f}, {maxx:.4f}, {maxy:.4f}")

        # Create Land Mask (Clip GADM to Study Area)
        # This ensures we only look at land, removing sea/ocean
        land_gdf = gpd.clip(gadm_gdf, study_area_gdf.envelope)

        # --- 2. Temperature Analysis (ERA5) ---
        print("Processing Temperature Data...")
        temp_file = os.path.join(era5_folder, f"{year}_2m_temperature_daily_maximum.nc")
        ds_temp = xr.open_dataset(temp_file)
        
        season_start = f"{year}-06-01"
        season_end = f"{year}-09-01"
        
        ds_summer = ds_temp.sel(valid_time=slice(season_start, season_end))
        mean_max_temp = ds_summer['t2m'].mean(dim='valid_time')
        mean_max_temp_c = mean_max_temp - 273.15
        
        # Clip to study area bounding box first
        temp_clipped = mean_max_temp_c.sel(
            longitude=slice(minx, maxx),
            latitude=slice(maxy, miny)
        )
        
        # Interpolate for smoother visualization (10x resolution)
        new_lat = np.linspace(float(temp_clipped.latitude.min()), float(temp_clipped.latitude.max()), len(temp_clipped.latitude) * 10)
        new_lon = np.linspace(float(temp_clipped.longitude.min()), float(temp_clipped.longitude.max()), len(temp_clipped.longitude) * 10)
        temp_smooth = temp_clipped.interp(latitude=new_lat, longitude=new_lon, method='linear')

        # Mask Water Bodies using Land Mask
        try:
            temp_smooth = temp_smooth.rio.write_crs("EPSG:4326")
            temp_smooth = temp_smooth.rio.clip(land_gdf.geometry, land_gdf.crs, drop=False)
        except Exception as e:
            print(f"Warning: Could not clip temperature to land geometry: {e}")

        # --- 3. NDVI Analysis (Pre-load for overlay) ---
        print("Processing NDVI Data...")
        ndvi_file = os.path.join(ndvi_folder, f"ndvi_{season_start}_{season_end}.tif")
        
        if not os.path.exists(ndvi_file):
             files = glob(os.path.join(ndvi_folder, f"*{year}*.tif"))
             if files:
                 ndvi_file = files[0]
                 print(f"Using fallback NDVI: {os.path.basename(ndvi_file)}")
             else:
                 print("No NDVI file found.")
                 return None

        # Resample NDVI to match Temperature Grid for Overlay & Stats
        # We do this BEFORE plotting to use it as an overlay
        with rasterio.open(ndvi_file) as src:
            # Create destination array (matching temp_smooth shape)
            dst_shape = temp_smooth.shape
            # from_bounds creates a North-up transform (row 0 is North)
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

        # Wrap NDVI in xarray for easy plotting and alignment
        # Note: ndvi_resampled is North-up (from_bounds default), but temp_smooth is South-up (new_lat is ascending)
        # So we assign latitude=new_lat[::-1] to the NDVI DataArray to match the data orientation
        xr_ndvi = xr.DataArray(
            ndvi_resampled,
            coords={'latitude': new_lat[::-1], 'longitude': new_lon},
            dims=('latitude', 'longitude')
        )
        # Sort by latitude to match temp_smooth (South-up) for consistency in operations
        xr_ndvi = xr_ndvi.sortby('latitude')
        
        # Update ndvi_resampled to be the aligned numpy array (South-up) for stats later
        ndvi_resampled = xr_ndvi.values

        # --- 4. Plotting Temperature with Context ---
        print("Generating Enhanced Temperature Map...")
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot Temperature (Land Only)
        # Use a colormap that highlights heat (RdYlBu_r is good: Blue=Cool, Red=Hot)
        # Fixed scale for comparison if vmin/vmax provided
        temp_plot = temp_smooth.plot(ax=ax, cmap='RdYlBu_r', add_colorbar=True, 
                                     vmin=vmin, vmax=vmax,
                                     cbar_kwargs={'label': 'Temperature (°C)'})
        
        # Add Contours to show gradients better
        temp_smooth.plot.contour(ax=ax, levels=8, colors='black', linewidths=0.3, alpha=0.5)

        # --- Add Vegetation Overlay ---
        # 1. Add Green Contours for Vegetation (NDVI > 0.4, 0.6, 0.8)
        # This shows the structure of vegetation on top of temperature
        # User requested lighter stroke
        xr_ndvi.plot.contour(ax=ax, levels=[0.4, 0.6, 0.8], colors=['#90EE90', '#32CD32', '#006400'], 
                             linewidths=0.8, linestyles='--')

        # Mask out low vegetation
        # ndvi_high_veg = xr_ndvi.where(xr_ndvi > 0.5)
        # ndvi_high_veg.plot.imshow(ax=ax, cmap='Greens', alpha=0.25, add_colorbar=False)

        # City Boundary (Thick and Distinct)
        city_gdf.boundary.plot(ax=ax, color='black', linewidth=2.5, label='City Boundary')
        
        # Add a custom legend element for Vegetation
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch
        legend_elements = [
            Line2D([0], [0], color='#32CD32', lw=0.8, linestyle='--', label='Vegetation Contours (NDVI)'),
            # Patch(facecolor='green', alpha=0.25, label='High Vegetation Area') # Removed
        ]
        ax.legend(handles=legend_elements, loc='upper right')

        plt.title(f"Temperature & Vegetation Overlay (Summer {year}) - {city_name}")
        out_temp = os.path.join(output_folder, f"week2_temperature_{city_name}.png")
        plt.savefig(out_temp)
        plt.close()
        print(f"Saved Enhanced Temperature Map: {out_temp}")

        # --- 5. Plotting NDVI (High Res) ---
        with rasterio.open(ndvi_file) as src:
            gdf_crs = study_area_gdf.to_crs(src.crs)
            out_image, out_transform = mask(src, gdf_crs.geometry, crop=True)
            out_meta = src.meta.copy()
            
            ndvi_high_res = out_image[0].astype(float)
            ndvi_high_res[ndvi_high_res == out_meta['nodata']] = np.nan
            ndvi_high_res = ndvi_high_res / 254.0 * 2.0 - 1.0
            
            height, width = ndvi_high_res.shape
            xmin = out_transform[2]
            ymax = out_transform[5]
            xmax = xmin + width * out_transform[0]
            ymin = ymax + height * out_transform[4]
            
            plt.figure(figsize=(10, 8))
            plt.imshow(ndvi_high_res, cmap='RdYlGn', vmin=-0.2, vmax=0.8, extent=[xmin, xmax, ymin, ymax])
            plt.colorbar(label='NDVI')
            city_gdf_crs = city_gdf.to_crs(src.crs)
            city_gdf_crs.boundary.plot(ax=plt.gca(), color='black', linewidth=2, label=f'{city_name} Boundary')
            plt.title(f"NDVI Vegetation Index (Summer {year}) - {city_name}")
            plt.legend()
            out_ndvi = os.path.join(output_folder, f"week2_ndvi_{city_name}.png")
            plt.savefig(out_ndvi)
            plt.close()
            print(f"Saved NDVI Map: {out_ndvi}")

        # --- 6. Statistical Analysis & Correlation ---
        print("Calculating Correlation and Insights...")
        
        # Flatten arrays (Use the masked temp_smooth to avoid water in stats!)
        # temp_smooth is an xarray, convert to numpy and flatten
        temp_flat = temp_smooth.values.flatten()
        ndvi_flat = ndvi_resampled.flatten()
        
        # Create DataFrame
        df = pd.DataFrame({'Temperature': temp_flat, 'NDVI': ndvi_flat})
        
        # Clean Data (Remove NaNs and outliers)
        df_clean = df.dropna()
        df_clean = df_clean[(df_clean['NDVI'] >= -1) & (df_clean['NDVI'] <= 1)]
        
        # Calculate Correlation
        if len(df_clean) > 0:
            corr_coef, p_value = pearsonr(df_clean['NDVI'], df_clean['Temperature'])
            stats['correlation'] = corr_coef
            print(f"Correlation (NDVI vs Temp): {corr_coef:.4f} (p-value: {p_value:.4e})")

            # Scatter Plot with Regression Line
            plt.figure(figsize=(8, 6))
            plot_data = df_clean.sample(n=min(5000, len(df_clean)), random_state=42)
            sns.regplot(x='NDVI', y='Temperature', data=plot_data, 
                        scatter_kws={'alpha':0.3, 's':10}, line_kws={'color':'red'})
            plt.title(f"Correlation: NDVI vs Temperature - {city_name}\nR = {corr_coef:.2f}")
            plt.xlabel("Vegetation Index (NDVI)")
            plt.ylabel("Max Temperature (°C)")
            plt.grid(True, alpha=0.3)
            out_scatter = os.path.join(output_folder, f"week2_scatter_{city_name}.png")
            plt.savefig(out_scatter)
            plt.close()
            print(f"Saved Scatter Plot: {out_scatter}")

            # Insight: UHI Intensity
            urban_temps = df_clean[df_clean['NDVI'] < 0.3]['Temperature']
            rural_temps = df_clean[df_clean['NDVI'] > 0.6]['Temperature']
            
            stats['avg_temp_urban'] = urban_temps.mean() if not urban_temps.empty else np.nan
            stats['avg_temp_rural'] = rural_temps.mean() if not rural_temps.empty else np.nan
            stats['uhi_intensity'] = stats['avg_temp_urban'] - stats['avg_temp_rural']
            
            print(f"Avg Temp Urban (NDVI < 0.3): {stats['avg_temp_urban']:.2f}°C")
            print(f"Avg Temp Rural (NDVI > 0.6): {stats['avg_temp_rural']:.2f}°C")
            print(f"Estimated UHI Intensity: {stats['uhi_intensity']:.2f}°C")

            # Boxplot
            def classify_ndvi(val):
                if val < 0.2: return 'Urban/Water (<0.2)'
                elif val < 0.4: return 'Sparse Veg (0.2-0.4)'
                elif val < 0.6: return 'Moderate Veg (0.4-0.6)'
                else: return 'Dense Veg (>0.6)'
                
            df_clean['Category'] = df_clean['NDVI'].apply(classify_ndvi)
            order = ['Urban/Water (<0.2)', 'Sparse Veg (0.2-0.4)', 'Moderate Veg (0.4-0.6)', 'Dense Veg (>0.6)']
            
            plt.figure(figsize=(10, 6))
            sns.boxplot(x='Category', y='Temperature', data=df_clean, order=order, palette="RdYlGn")
            plt.title(f"Temperature Distribution by Vegetation Density - {city_name}")
            plt.ylabel("Max Temperature (°C)")
            plt.xlabel("NDVI Category")
            plt.xticks(rotation=15)
            out_box = os.path.join(output_folder, f"week2_boxplot_{city_name}.png")
            plt.savefig(out_box)
            plt.close()
            print(f"Saved Boxplot: {out_box}")
        else:
            print("Not enough valid data for statistics.")
            stats['correlation'] = np.nan
            stats['uhi_intensity'] = np.nan
            stats['avg_temp_urban'] = np.nan

        return stats

    except Exception as e:
        print(f"Error analyzing {city_name}: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("Starting Week 2 Analysis: Urban Heat Island Effect (Enhanced)")

    DATA_FOLDER = "data"
    OUTPUT_FOLDER = "reports/figures"
    GADM_FILE = os.path.join(DATA_FOLDER, "gadm_410_europe.gpkg")
    ERA5_FOLDER = os.path.join(DATA_FOLDER, "derived-era5-land-daily-statistics")
    NDVI_FOLDER = os.path.join(DATA_FOLDER, "sentinel2_ndvi")
    
    print("Loading GADM data...")
    gadm_gdf = gpd.read_file(GADM_FILE)

    cities = [
        ("FRA", "Paris"),
        ("ITA", "Roma"),
        ("FRA", "Nantes"), # Smaller town in France
        ("ITA", "Perugia") # Smaller town in Italy (Inland)
    ]
    
    results = []

    for country, city in cities:
        # Reverted to dynamic scaling per user request to improve local contrast
        res = analyze_city(country, city, 2022, gadm_gdf, ERA5_FOLDER, NDVI_FOLDER, OUTPUT_FOLDER)
        if res:
            res['city'] = city
            results.append(res)
            
    # Summary
    print("\n" + "="*50)
    print("COMPARATIVE SUMMARY")
    print("="*50)
    for r in results:
        print(f"City: {r['city']}")
        print(f"  - Correlation (NDVI vs Temp): {r['correlation']:.2f}")
        print(f"  - UHI Intensity (Urban - Rural): {r['uhi_intensity']:.2f}°C")
        print(f"  - Avg Urban Temp: {r['avg_temp_urban']:.2f}°C")
        print("-" * 30)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
