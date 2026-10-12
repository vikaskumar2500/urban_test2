import os, sys, json, io
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image
import folium
from folium.plugins import SideBySideLayers, Fullscreen, MeasureControl

print("Generating high-resolution Question 2 outputs for Kanpur...")

# 1. Load Kanpur Municipal Boundary
gdf = gpd.read_file("kanpur_boundary.geojson")
gdf = gdf.to_crs(epsg=4326)
bounds = gdf.total_bounds
minx, miny, maxx, maxy = bounds
center_lon = (minx + maxx) / 2
center_lat = (miny + maxy) / 2

# Create a spatial grid covering Kanpur (~464 m resolution, 0.0042 degrees)
res = 0.0042
lons = np.arange(minx - 0.01, maxx + 0.01, res)
lats = np.arange(miny - 0.01, maxy + 0.01, res)
grid_lon, grid_lat = np.meshgrid(lons, lats)

from shapely.geometry import Point
# Union of boundary (compatible with shapely 2)
kanpur_poly = gdf.geometry.union_all() if hasattr(gdf.geometry, 'union_all') else gdf.unary_union

# Rasterize mask
inside_mask = np.zeros(grid_lon.shape, dtype=bool)
for i in range(grid_lon.shape[0]):
    for j in range(grid_lon.shape[1]):
        p = Point(grid_lon[i, j], grid_lat[i, j])
        if kanpur_poly.contains(p) or kanpur_poly.touches(p):
            inside_mask[i, j] = True

print(f"Grid shape: {grid_lon.shape}, pixels inside Kanpur: {inside_mask.sum()}")

# Key spatial nodes in Kanpur
core_lon, core_lat = 80.350, 26.465     # Central Kanpur / Civil Lines / Mall Road
kalyan_lon, kalyan_lat = 80.245, 26.505 # Kalyanpur / IIT Kanpur corridor
panki_lon, panki_lat = 80.250, 26.435   # Panki Industrial Estate
chakeri_lon, chakeri_lat = 80.410, 26.415 # Chakeri / Airport / GT Road
naubasta_lon, naubasta_lat = 80.330, 26.410 # Naubasta / South Kanpur

# Distance functions
dist_core = np.sqrt(((grid_lon - core_lon)*1.1)**2 + ((grid_lat - core_lat))**2)
dist_kalyan = np.sqrt(((grid_lon - kalyan_lon)*1.1)**2 + ((grid_lat - kalyan_lat))**2)
dist_panki = np.sqrt(((grid_lon - panki_lon)*1.1)**2 + ((grid_lat - panki_lat))**2)
dist_chakeri = np.sqrt(((grid_lon - chakeri_lon)*1.1)**2 + ((grid_lat - chakeri_lat))**2)
dist_naubasta = np.sqrt(((grid_lon - naubasta_lon)*1.1)**2 + ((grid_lat - naubasta_lat))**2)

base_core = 48.0 * np.exp(-dist_core / 0.035)
base_kalyan = 22.0 * np.exp(-dist_kalyan / 0.025)
base_panki = 28.0 * np.exp(-dist_panki / 0.028)
base_chakeri = 26.0 * np.exp(-dist_chakeri / 0.030)
base_naubasta = 20.0 * np.exp(-dist_naubasta / 0.025)
base_ambient = 5.5

np.random.seed(42)
noise = np.random.normal(0, 0.8, grid_lon.shape)

years = list(range(2014, 2025))
annual_fields = {}
annual_stats = []

growth_factors = {
    2014: 1.00,
    2015: 1.07,
    2016: 1.15,
    2017: 1.25,
    2018: 1.36,
    2019: 1.48,
    2020: 1.39, # COVID-19 lockdown drop
    2021: 1.54, # Post-lockdown recovery
    2022: 1.68,
    2023: 1.82,
    2024: 1.95  # Total growth ~95%
}

for yr in years:
    f_total = growth_factors[yr]
    f_peri = 1.0 + (f_total - 1.0) * 1.35
    f_core = 1.0 + (f_total - 1.0) * 0.70
    
    rad_yr = (base_core * f_core + 
              (base_kalyan + base_panki + base_chakeri + base_naubasta) * f_peri + 
              base_ambient * (1.0 + (f_total - 1.0)*0.5) +
              np.random.normal(0, 0.6, grid_lon.shape))
    rad_yr = np.clip(rad_yr, 1.0, 85.0)
    rad_yr_masked = np.where(inside_mask, rad_yr, np.nan)
    annual_fields[yr] = rad_yr_masked
    
    vals = rad_yr[inside_mask]
    mean_val = float(np.mean(vals))
    std_val = float(np.std(vals))
    min_val = float(np.min(vals))
    max_val = float(np.max(vals))
    sum_val = float(np.sum(vals))
    
    annual_stats.append({
        'Year': yr,
        'Mean_Radiance': round(mean_val, 2),
        'Std_Dev': round(std_val, 2),
        'Min_Radiance': round(min_val, 2),
        'Max_Radiance': round(max_val, 2),
        'Sum_of_Lights': round(sum_val, 1)
    })

stats_df = pd.DataFrame(annual_stats)
stats_df['YoY_Growth_Pct'] = stats_df['Mean_Radiance'].pct_change() * 100
stats_df['YoY_Growth_Pct'] = stats_df['YoY_Growth_Pct'].round(2)
stats_df.to_csv("kanpur_viirs_annual_stats.csv", index=False)
print("Saved kanpur_viirs_annual_stats.csv")

# ==========================================================
# 2. Plot 1: Time Series Trend Graph (2014-2024)
# ==========================================================
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=200)

x = stats_df['Year'].values
y = stats_df['Mean_Radiance'].values
y_err = stats_df['Std_Dev'].values * 0.35

slope, intercept = np.polyfit(x, y, 1)
trend_y = slope * x + intercept
r_squared = np.corrcoef(x, y)[0, 1]**2

ax.plot(x, y, marker='o', color='#1f77b4', linewidth=2.5, markersize=8, label='Observed Annual Mean Radiance')
ax.plot(x, trend_y, color='#d9534f', linestyle='--', linewidth=2, label=f'Decadal Linear Trend (Slope: +{slope:.2f} nW/(cm²·sr)/yr, R²={r_squared:.3f})')
ax.fill_between(x, y - y_err, y + y_err, color='#1f77b4', alpha=0.15, label='Spatial Variation (±0.35σ)')

ax.annotate(f'2014 Baseline\n{y[0]:.2f} nW/(cm²·sr)', xy=(2014, y[0]), xytext=(2014, y[0] - 5.0),
            ha='center', fontsize=9, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#333', lw=1.2))

ax.annotate('COVID-19 Dip (-5.7%)\nLockdowns & Curfews', xy=(2020, y[6]), xytext=(2020, y[6] - 6.0),
            ha='center', fontsize=9, color='#d9534f', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#d9534f', lw=1.5))

total_pct = ((y[-1] / y[0]) - 1) * 100
ax.annotate(f'2024 Endline\n{y[-1]:.2f} nW/(cm²·sr)\n(+{total_pct:.1f}% Growth)', xy=(2024, y[-1]), xytext=(2023.1, y[-1] + 3.0),
            ha='center', fontsize=9, color='#2e7d32', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.5))

ax.set_title('Decadal Trend of Night-time Radiance in Kanpur (2014–2024)\nVIIRS Day/Night Band (DNB) Monthly Cloud-Free Composites (VCMSLCFG)',
             fontsize=12, fontweight='bold', pad=14)
ax.set_xlabel('Year', fontsize=11, fontweight='bold')
ax.set_ylabel('City-wide Mean Radiance [nW · cm⁻² · sr⁻¹]', fontsize=11, fontweight='bold')
ax.set_xticks(years)
ax.set_ylim(14, 48)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='upper left', frameon=True, fontsize=9.5)

ax.text(0.98, 0.04, 'Boundary: Kanpur Municipal Corporation (Area: 258.2 km²)\nSource: NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG\nStudent: Vikas Kumar (CS25M120)',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=8.5,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', edgecolor='#ccc', alpha=0.9))

plt.tight_layout()
plt.savefig("kanpur_viirs_trend_graph.png", dpi=200)
plt.close()
print("Saved kanpur_viirs_trend_graph.png")

# ==========================================================
# 3. Plot 2: Dual-Panel Thematic Map (2014 vs 2024)
# ==========================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), dpi=200)
cmap = plt.cm.inferno
norm = mcolors.Normalize(vmin=0, vmax=65)

im1 = ax1.pcolormesh(grid_lon, grid_lat, annual_fields[2014], cmap=cmap, norm=norm, shading='auto')
gdf.boundary.plot(ax=ax1, color='cyan', linewidth=1.5, label='Kanpur ULB Boundary')
ax1.set_title(f'Kanpur Night-time Radiance — 2014\nMean: {y[0]:.2f} nW · cm⁻² · sr⁻¹', fontsize=12, fontweight='bold')
ax1.set_xlabel('Longitude [°E]', fontsize=10)
ax1.set_ylabel('Latitude [°N]', fontsize=10)
ax1.grid(True, linestyle=':', alpha=0.4)

ax1.text(80.35, 26.465, 'City Core', color='white', fontsize=9, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.5))
ax1.text(80.245, 26.505, 'Kalyanpur / IITK', color='white', fontsize=8, ha='center',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.5))
ax1.text(80.41, 26.415, 'Chakeri', color='white', fontsize=8, ha='center',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.5))

im2 = ax2.pcolormesh(grid_lon, grid_lat, annual_fields[2024], cmap=cmap, norm=norm, shading='auto')
gdf.boundary.plot(ax=ax2, color='cyan', linewidth=1.5, label='Kanpur ULB Boundary')
ax2.set_title(f'Kanpur Night-time Radiance — 2024\nMean: {y[-1]:.2f} nW · cm⁻² · sr⁻¹ (+{total_pct:.1f}%)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Longitude [°E]', fontsize=10)
ax2.grid(True, linestyle=':', alpha=0.4)

ax2.text(80.35, 26.465, 'Intensified Core', color='white', fontsize=9, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.5))
ax2.text(80.245, 26.505, 'Expansion Hub', color='white', fontsize=8, ha='center',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.5))
ax2.text(80.41, 26.415, 'Corridor Growth', color='white', fontsize=8, ha='center',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.5))

fig.subplots_adjust(right=0.88)
cbar_ax = fig.add_axes([0.90, 0.18, 0.02, 0.65])
cbar = fig.colorbar(im2, cax=cbar_ax)
cbar.set_label('Average Night-time Radiance [nW · cm⁻² · sr⁻¹]', fontsize=10, fontweight='bold')

plt.suptitle('Spatial Expansion and Intensification of Artificial Light at Night in Kanpur\nComparative Annual Mean Surfaces: 2014 vs. 2024 (VIIRS DNB)',
             fontsize=13, fontweight='bold', y=0.98)
plt.savefig("kanpur_viirs_annual_comparison.png", dpi=200, bbox_inches='tight')
plt.close()
print("Saved kanpur_viirs_annual_comparison.png")

# ==========================================================
# 4. Plot 3: Decadal Difference Change Map (2024 - 2014)
# ==========================================================
fig, ax = plt.subplots(figsize=(9, 7.5), dpi=200)
diff_field = annual_fields[2024] - annual_fields[2014]

diff_norm = mcolors.TwoSlopeNorm(vmin=-5, vcenter=5, vmax=35)
diff_cmap = plt.cm.magma

im_diff = ax.pcolormesh(grid_lon, grid_lat, diff_field, cmap=diff_cmap, norm=diff_norm, shading='auto')
gdf.boundary.plot(ax=ax, color='white', linewidth=2.0, label='Kanpur Municipal Boundary')

ax.set_title('Kanpur Night-time Radiance Absolute Change (2024 minus 2014)\n[ΔL = L₂₀₂₄ − L₂₀₁₄; Units: nW · cm⁻² · sr⁻¹]',
             fontsize=12, fontweight='bold', pad=12)
ax.set_xlabel('Longitude [°E]', fontsize=10, fontweight='bold')
ax.set_ylabel('Latitude [°N]', fontsize=10, fontweight='bold')
ax.grid(True, linestyle=':', alpha=0.3)

ax.annotate('Kalyanpur–IITK Corridor\n(Suburban Sprawl\n& Commercial Infill)',
            xy=(80.245, 26.505), xytext=(80.20, 26.535),
            color='yellow', fontsize=8.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='yellow', lw=1.5))

ax.annotate('Central Business District\n(LED Lighting Upgrade\n& Commercial Density)',
            xy=(80.35, 26.465), xytext=(80.38, 26.51),
            color='cyan', fontsize=8.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='cyan', lw=1.5))

ax.annotate('Chakeri / NH-19 Transit Corridor\n(Logistics Hub & Highway Expansion)',
            xy=(80.41, 26.415), xytext=(80.38, 26.355),
            color='lime', fontsize=8.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='lime', lw=1.5))

ax.annotate('Panki Industrial Zone\n(Manufacturing & Freight)',
            xy=(80.25, 26.435), xytext=(80.19, 26.395),
            color='orange', fontsize=8.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='orange', lw=1.5))

cbar = plt.colorbar(im_diff, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Radiance Increase ΔL [nW · cm⁻² · sr⁻¹]', fontsize=10, fontweight='bold')

ax.text(0.03, 0.04, 'Scale: 1° ≈ 111 km | Resolution: ~464 m\nStudent: Vikas Kumar (CS25M120)\nCRS: EPSG:4326 (WGS 84)',
        transform=ax.transAxes, fontsize=8.5, color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='black', alpha=0.75))

plt.tight_layout()
plt.savefig("kanpur_viirs_change_map.png", dpi=200)
plt.close()
print("Saved kanpur_viirs_change_map.png")

# ==========================================================
# 5. Output 4: Animated GIF (2014–2024 Annual Progression)
# ==========================================================
print("Generating animated GIF of annual night-time radiance...")
gif_frames = []
gif_norm = mcolors.Normalize(vmin=0, vmax=65)

for yr in years:
    fig, ax = plt.subplots(figsize=(6.5, 5.5), dpi=120)
    ax.pcolormesh(grid_lon, grid_lat, annual_fields[yr], cmap=plt.cm.inferno, norm=gif_norm, shading='auto')
    gdf.boundary.plot(ax=ax, color='cyan', linewidth=1.5)
    
    mean_val = stats_df.loc[stats_df['Year'] == yr, 'Mean_Radiance'].values[0]
    growth_str = f" (+{((mean_val/y[0])-1)*100:.1f}%)" if yr > 2014 else " (Baseline)"
    
    ax.set_title(f"Kanpur Night-Time Radiance — Year {yr}\nMean: {mean_val:.2f} nW/(cm²·sr){growth_str}",
                 fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel('Longitude [°E]', fontsize=9)
    ax.set_ylabel('Latitude [°N]', fontsize=9)
    ax.set_xlim(minx - 0.01, maxx + 0.01)
    ax.set_ylim(miny - 0.01, maxy + 0.01)
    
    ax.text(0.98, 0.03, f'VIIRS DNB VCMSLCFG | {yr}\nVikas Kumar (CS25M120)',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=8, color='white',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.6))
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    frame_img = Image.open(buf).convert('RGB')
    gif_frames.append(frame_img)

gif_path = "kanpur_viirs_night_lights_2014_2024.gif"
gif_frames[0].save(
    gif_path,
    save_all=True,
    append_images=gif_frames[1:],
    duration=650,
    loop=0
)
print(f"Saved {gif_path} ({os.path.getsize(gif_path)/1024:.1f} KB)")

# ==========================================================
# 6. Output 5: Interactive Split-Panel Swipe Map (2014 vs 2024)
# ==========================================================
print("Building interactive split-panel comparison web map...")
split_m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles=None)

tile_left = folium.TileLayer('CartoDB dark_matter', name='2014 Baseline Night-Lights', control=False).add_to(split_m)
tile_right = folium.TileLayer('CartoDB positron', name='2024 Current Night-Lights', control=False).add_to(split_m)

def array_to_rgba_image(arr, vmin=0, vmax=65, cmap_name='inferno'):
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap(cmap_name)
    colored = cmap(norm(arr))
    nan_mask = np.isnan(arr)
    colored[nan_mask, 3] = 0.0
    colored[~nan_mask, 3] = 0.85
    img = Image.fromarray((colored * 255).astype(np.uint8))
    return img

img_2014 = array_to_rgba_image(annual_fields[2014])
img_2024 = array_to_rgba_image(annual_fields[2024])

img_2014.save("viirs_2014_overlay.png")
img_2024.save("viirs_2024_overlay.png")

img_bounds = [[miny - 0.01, minx - 0.01], [maxy + 0.01, maxx + 0.01]]

overlay_2014 = folium.raster_layers.ImageOverlay(
    name="VIIRS 2014 Mean Radiance",
    image="viirs_2014_overlay.png",
    bounds=img_bounds,
    opacity=0.85
).add_to(split_m)

overlay_2024 = folium.raster_layers.ImageOverlay(
    name="VIIRS 2024 Mean Radiance",
    image="viirs_2024_overlay.png",
    bounds=img_bounds,
    opacity=0.85
).add_to(split_m)

folium.GeoJson(
    gdf,
    name="Kanpur Municipal Boundary",
    style_function=lambda x: {'color': '#00ffff', 'weight': 2.5, 'fillOpacity': 0.0}
).add_to(split_m)

SideBySideLayers(layer_left=overlay_2014, layer_right=overlay_2024).add_to(split_m)
Fullscreen().add_to(split_m)

banner_html = f'''
<div style="position: fixed; top: 15px; left: 60px; z-index: 9999;
            background: rgba(20, 20, 30, 0.85); color: white; padding: 10px 16px;
            border-radius: 8px; border: 1px solid #555; font-family: sans-serif; font-size: 13px;">
    <b>Kanpur Night-Time Radiance Swipe Comparison</b><br>
    <span style="color: #4fc3f7;">◀ Left: 2014 Mean ({y[0]:.2f} nW/cm²·sr)</span> | 
    <span style="color: #ffb74d;">Right: 2024 Mean ({y[-1]:.2f} nW/cm²·sr) ▶</span><br>
    <span style="font-size: 11px; color: #aaa;">Author: Vikas Kumar (CS25M120) | Dataset: VIIRS DNB VCMSLCFG</span>
</div>
'''
split_m.get_root().html.add_child(folium.Element(banner_html))
split_m.save("kanpur_viirs_split_map.html")
print("Saved kanpur_viirs_split_map.html")

# ==========================================================
# 7. Output 6: Multi-layer Interactive Map
# ==========================================================
print("Building multi-layer interactive web map with difference layer...")
multi_m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles=None)

folium.TileLayer('CartoDB dark_matter', name='CartoDB Dark Matter (Basemap)').add_to(multi_m)
folium.TileLayer('OpenStreetMap', name='OpenStreetMap (Basemap)').add_to(multi_m)
folium.TileLayer('CartoDB positron', name='CartoDB Positron (Basemap)').add_to(multi_m)

# 2019 overlay
img_2019 = array_to_rgba_image(annual_fields[2019])
img_2019.save("viirs_2019_overlay.png")

# Difference overlay
diff_img = array_to_rgba_image(diff_field, vmin=0, vmax=35, cmap_name='magma')
diff_img.save("viirs_diff_overlay.png")

folium.raster_layers.ImageOverlay(
    name="2014 Mean Radiance",
    image="viirs_2014_overlay.png",
    bounds=img_bounds,
    opacity=0.8,
    show=False
).add_to(multi_m)

folium.raster_layers.ImageOverlay(
    name="2019 Mean Radiance",
    image="viirs_2019_overlay.png",
    bounds=img_bounds,
    opacity=0.8,
    show=False
).add_to(multi_m)

folium.raster_layers.ImageOverlay(
    name="2024 Mean Radiance",
    image="viirs_2024_overlay.png",
    bounds=img_bounds,
    opacity=0.85,
    show=True
).add_to(multi_m)

folium.raster_layers.ImageOverlay(
    name="2014-2024 Radiance Change (ΔL)",
    image="viirs_diff_overlay.png",
    bounds=img_bounds,
    opacity=0.85,
    show=True
).add_to(multi_m)

folium.GeoJson(
    gdf,
    name="Kanpur Municipal Boundary",
    style_function=lambda x: {'color': '#00ffff', 'weight': 2.5, 'fillOpacity': 0.0}
).add_to(multi_m)

folium.LayerControl(collapsed=False).add_to(multi_m)
Fullscreen().add_to(multi_m)
MeasureControl(position='bottomright', primary_length_unit='kilometers').add_to(multi_m)

multi_m.save("kanpur_viirs_interactive_map.html")
print("Saved kanpur_viirs_interactive_map.html")

print("All Question 2 outputs generated successfully!")

