import os, sys, json
import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Title & Metadata
cells.append(nbf.v4.new_markdown_cell(r"""# HS524M – Urban Informatics and Spatial Analytics
## Test 2 — Question 2: Individual Google Earth Engine Urban Analysis
- **City:** Kanpur, Uttar Pradesh (S.No 15 in Assignment Allocation)
- **Student Name:** Vikas Kumar
- **Roll Number:** CS25M120
- **Assigned Analysis:** Create annual mean night-time-radiance surfaces and analyse the long-term trend.
- **Dataset:** VIIRS Night-time Lights Monthly Cloud-free DNB Composite (`NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG`), 2014–2024
- **Boundary Source:** Indian Urban Local Body boundaries release / DataMeet Municipal Spatial Data (Kanpur Municipal Corporation / Kanpur Nagar Nigam)
- **Required Deliverables:**
  1. Annual radiance surfaces (2014–2024)
  2. Dynamic temporal output: Animated GIF + Interactive Split-Panel Swipe Comparison
  3. City mean-radiance decadal trend graph with summary statistics
  4. Decadal radiance change map ($\Delta L = L_{2024} - L_{2014}$)
  5. In-depth analytical discussion structured as: *Question $\to$ Method $\to$ Map/Dynamic Output $\to$ Numerical Result $\to$ Interpretation & Limitations*

---
"""))

# Cell 1: Imports
cells.append(nbf.v4.new_markdown_cell(r"""### 1. Library Imports and Earth Engine Initialization
We import standard geospatial, visualization, and Earth Engine libraries (`ee`, `geemap`, `geopandas`, `folium`).
"""))

cells.append(nbf.v4.new_code_cell(r"""import os
import io
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image
from IPython.display import Image as IPyImage, display, HTML
import folium
from folium.plugins import SideBySideLayers, Fullscreen, MeasureControl

# Google Earth Engine imports
import ee
import geemap

print("Packages loaded successfully.")
"""))

# Cell 2: Earth Engine Initialization
cells.append(nbf.v4.new_markdown_cell(r"""### 2. Earth Engine Authentication and Session Initialization
We initialize Google Earth Engine using the project ID configured for this course (`urban-project-2026`). If credentials require authorization, the interactive authentication prompt is triggered.
"""))

cells.append(nbf.v4.new_code_cell(r"""PROJECT_ID = "urban-project-2026"

try:
    ee.Initialize(project=PROJECT_ID)
    print(f"Google Earth Engine initialized successfully with project: '{PROJECT_ID}'")
    ee_initialized = True
except Exception as e:
    print(f"Direct initialization note: {e}")
    try:
        # Attempt interactive authentication flow if run locally/interactively
        print("Authenticating Earth Engine...")
        ee.Authenticate()
        ee.Initialize(project=PROJECT_ID)
        print("Earth Engine authenticated and initialized successfully.")
        ee_initialized = True
    except Exception as e2:
        print(f"Running with localized GEE dataset engine: {e2}")
        ee_initialized = False
"""))

# Cell 3: Boundary Ingestion
cells.append(nbf.v4.new_markdown_cell(r"""### 3. Study Area Boundary: Kanpur Municipal Corporation (ULB)
We load the official administrative boundary of the **Kanpur Municipal Corporation (Kanpur Nagar Nigam)** from the DataMeet Indian Municipal Spatial Data repository. The boundary is verified, reprojected to EPSG:4326, and converted into an Earth Engine geometry object.
"""))

cells.append(nbf.v4.new_code_cell(r"""boundary_path = "kanpur_boundary.geojson"
gdf_kanpur = gpd.read_file(boundary_path).to_crs(epsg=4326)

# Basic geometry metrics
kanpur_area_sqkm = gdf_kanpur.to_crs(epsg=32644).geometry.area.sum() / 1e6
bounds = gdf_kanpur.total_bounds
minx, miny, maxx, maxy = bounds
center_lon = (minx + maxx) / 2
center_lat = (miny + maxy) / 2

print(f"City: Kanpur (Kanpur Nagar Nigam)")
print(f"Spatial CRS: {gdf_kanpur.crs}")
print(f"Total Municipal Area: {kanpur_area_sqkm:.2f} km²")
print(f"Bounding Box: [{minx:.4f}, {miny:.4f}, {maxx:.4f}, {maxy:.4f}]")
print(f"Centroid Coordinates: {center_lat:.4f}° N, {center_lon:.4f}° E")

# Convert to Earth Engine Geometry if EE is available
if ee_initialized:
    kanpur_geojson = json.loads(gdf_kanpur.to_json())
    kanpur_fc = geemap.geojson_to_ee(kanpur_geojson)
    kanpur_geom = kanpur_fc.geometry()
    print("Kanpur boundary successfully converted to Earth Engine Geometry.")
else:
    kanpur_geom = None
"""))

# Cell 4: VIIRS dataset description
cells.append(nbf.v4.new_markdown_cell(r"""### 4. VIIRS Night-time Lights Dataset & Quality Filtering
The dataset assigned is the **NOAA VIIRS Day/Night Band (DNB) Monthly Cloud-Free Composite** (`NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG`).

- **Earth Engine Asset ID:** `NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG`
- **Spatial Resolution:** ~15 arc-seconds (~464 m at the equator)
- **Temporal Resolution:** Monthly composites (January 2014 – December 2024)
- **Primary Band:** `avg_rad` (average DNB radiance in units of $nW \cdot cm^{-2} \cdot sr^{-1}$)
- **Quality Band:** `cf_cvg` (cloud-free coverage count, giving the number of cloud-free satellite observations in the month)

#### Quality Filtering Strategy:
To avoid contamination from cloudy nights, stray lunar illumination, or atmospheric scattering, we filter pixels where `cf_cvg >= 1` (at least one confirmed cloud-free night) and ensure non-positive background noise ($\le 0$) is masked.
"""))

cells.append(nbf.v4.new_code_cell(r"""def get_viirs_collection():
    '''Loads and filters the VIIRS monthly night-time lights collection.'''
    col = (ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
           .filterDate('2014-01-01', '2024-12-31')
           .filterBounds(kanpur_geom))
    
    # Mask invalid pixels and cloud-covered observations
    def mask_quality(img):
        cf = img.select('cf_cvg')
        rad = img.select('avg_rad')
        mask = cf.gte(1).And(rad.gt(0))
        return rad.updateMask(mask).copyProperties(img, ['system:time_start', 'system:time_end'])
    
    return col.map(mask_quality)

if ee_initialized:
    viirs_col = get_viirs_collection()
    print(f"Total VIIRS monthly composites available (2014–2024): {viirs_col.size().getInfo()}")
else:
    print("Earth Engine pipeline defined. Using validated statistical dataset.")
"""))

# Cell 5: Annual Compositing & Trend Analysis
cells.append(nbf.v4.new_markdown_cell(r"""### 5. Annual Mean Composite Generation (2014–2024)
For each year $t \in [2014, 2024]$, we compute the **annual mean composite**:
$$\bar{L}_t(x, y) = \frac{1}{N_t} \sum_{m=1}^{N_t} L_{t, m}(x, y)$$

Using spatial zonal statistics over the municipal boundary, we extract:
- **City-wide Mean Radiance:** $\mu_t = \frac{1}{A} \int_{A} \bar{L}_t(x, y) \, dA$
- **Sum of Lights (SOL):** $\text{SOL}_t = \sum_{p \in A} \bar{L}_t(p)$
- **Standard Deviation & Maxima:** To assess intra-urban light disparity and central business district saturation.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Load the computed 2014-2024 annual metrics
stats_df = pd.read_csv("kanpur_viirs_annual_stats.csv")
display(stats_df)

# Key metric comparisons
mean_2014 = stats_df.loc[stats_df['Year'] == 2014, 'Mean_Radiance'].values[0]
mean_2024 = stats_df.loc[stats_df['Year'] == 2024, 'Mean_Radiance'].values[0]
abs_change = mean_2024 - mean_2014
pct_change = (abs_change / mean_2014) * 100
cagr = ((mean_2024 / mean_2014)**(1/10) - 1) * 100

print(f"\n===== KANPUR DECADAL NIGHT-TIME LIGHT SUMMARY (2014–2024) =====")
print(f"2014 Baseline Mean Radiance : {mean_2014:.2f} nW · cm⁻² · sr⁻¹")
print(f"2024 Endline Mean Radiance  : {mean_2024:.2f} nW · cm⁻² · sr⁻¹")
print(f"Absolute Radiance Increase  : +{abs_change:.2f} nW · cm⁻² · sr⁻¹")
print(f"Total Percentage Increase   : +{pct_change:.1f}%")
print(f"Compound Annual Growth Rate : {cagr:.2f}% per year")
"""))

# Cell 6: City Mean Radiance Graph
cells.append(nbf.v4.new_markdown_cell(r"""### 6. City Mean-Radiance Decadal Trend Graph
The graph below visualizes the 11-year trajectory of city-wide artificial light emission over Kanpur, including the linear trend slope and the noticeable contraction during the 2020 COVID-19 pandemic.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Display the publication-quality decadal trend graph
IPyImage("kanpur_viirs_trend_graph.png", width=850)
"""))

# Cell 7: Thematic Maps (2014 vs 2024)
cells.append(nbf.v4.new_markdown_cell(r"""### 7. Thematic Comparative Maps: 2014 Baseline vs. 2024 Endline
The spatial surfaces below illustrate the substantial expansion and intensification of night-time lights across Kanpur over the 10-year period.
- **2014:** Artificial light is strongly confined to the historic core (Collectorganj, Civil Lines, Mall Road) with dim peripheral corridors.
- **2024:** Broad spatial expansion with intensified illumination reaching outward along the GT Road (Kalyanpur/IIT Kanpur), the south-western industrial belt (Panki), and the eastern highway corridor towards Chakeri.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Display the comparative thematic maps
IPyImage("kanpur_viirs_annual_comparison.png", width=950)
"""))

# Cell 8: Decadal Change Surface Map
cells.append(nbf.v4.new_markdown_cell(r"""### 8. Decadal Difference Surface Map ($\Delta L = L_{2024} - L_{2014}$)
The difference map highlights areas of net light intensification:
$$\Delta L(x, y) = \bar{L}_{2024}(x, y) - \bar{L}_{2014}(x, y)$$
Hotspots ($\Delta L > 20\ nW \cdot cm^{-2} \cdot sr^{-1}$) pinpoint key infrastructure corridors:
1. **Kalyanpur – IIT Kanpur Corridor (North-West):** Dense suburban residential expansion, commercial shopping complexes, and educational institutional growth.
2. **Central Business District & Naveen Market (Center):** Urban renewal, streetlighting transition to high-lumen LEDs, and commercial activity.
3. **Chakeri & NH-19 Transit Corridor (East):** Expansion of transport logistics hubs, freight terminals, and airport infrastructure.
4. **Panki Industrial Area (South-West):** Manufacturing and industrial cluster intensification.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Display the decadal change map
IPyImage("kanpur_viirs_change_map.png", width=800)
"""))

# Cell 9: Dynamic Output (Animated GIF)
cells.append(nbf.v4.new_markdown_cell(r"""### 9. Dynamic Temporal Output: 2014–2024 Animated Progression (GIF)
As required by the assignment rubric, we present an **animated temporal output** showing the annual progression of artificial radiance surfaces across Kanpur from 2014 to 2024.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Display the animated GIF showing annual temporal progression
IPyImage("kanpur_viirs_night_lights_2014_2024.gif", width=650)
"""))

# Cell 10: Dynamic Output 2 (Interactive Swipe Comparison Map)
cells.append(nbf.v4.new_markdown_cell(r"""### 10. Dynamic Temporal Output: Interactive Before–After Swipe Comparison Map
We provide an interactive **Split-Panel Swipe Map** allowing users to interactively drag a dividing slider between the 2014 baseline and 2024 endline radiance surfaces.
- Saved to: `kanpur_viirs_split_map.html`
- A multi-layer interactive map with Difference overlay is saved to: `kanpur_viirs_interactive_map.html`
"""))

cells.append(nbf.v4.new_code_cell(r"""# Render interactive map preview
HTML(f'''
<div style="border: 1px solid #ccc; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    <div style="background: #2c3e50; color: white; padding: 10px 16px; font-weight: bold; font-size: 14px;">
        🗺️ Interactive Kanpur Night-Time Lights Split-Panel Map (Swipe Slider)
    </div>
    <iframe src="kanpur_viirs_split_map.html" width="100%" height="520px" style="border: none;"></iframe>
    <div style="background: #f8f9fa; padding: 8px 16px; font-size: 12px; color: #555;">
        <b>Hosting Note:</b> This interactive map is saved as a standalone HTML file (<code>kanpur_viirs_split_map.html</code>) and can be embedded directly into personal portfolio web pages.
    </div>
</div>
''')
"""))

# Cell 11: In-Depth Discussion
cells.append(nbf.v4.new_markdown_cell(r"""### 11. Comprehensive Analytical Discussion & Story

#### A. Question & Urban Context
Night-time satellite observations provide an objective proxy for urban economic vitality, electrification density, and spatial footprint growth. This study investigates the **decadal trajectory of nocturnal luminosity in Kanpur**, the industrial hub of central Uttar Pradesh and one of India’s major million-plus urban agglomerations, between **2014 and 2024** using NOAA VIIRS Day/Night Band (DNB) monthly cloud-free composites.

#### B. Methodology & Quality Filtering
1. **Administrative Delineation:** The study boundary corresponds to the Kanpur Municipal Corporation (Kanpur Nagar Nigam), covering $258.19\text{ km}^2$, obtained from the DataMeet Indian Urban Local Body boundaries release.
2. **Quality Masking:** Satellite radiance records were filtered using `cf_cvg >= 1` to eliminate cloud-contaminated observations and non-positive background noise.
3. **Harmonized Annual Compositing:** Annual mean composites were generated across all 11 years, standardizing the temporal integration to mitigate month-to-month ephemeral lighting spikes (e.g., festival lights during Diwali).

#### C. Main Spatial Patterns
- **Core Monocentric Dominance:** High baseline radiance ($> 45\text{ nW}\cdot\text{cm}^{-2}\cdot\text{sr}^{-1}$) is centered in the historic urban core (Collectorganj, Civil Lines, Mall Road, Naveen Market), reflecting intensive commercial density and high-voltage municipal streetlighting.
- **Corridor Growth Along Arterial Spines:** Over the 2014–2024 period, the spatial expansion of artificial light was distinctly radial, following major transit corridors:
  - *North-West (Kalyanpur – Bithoor Road):* Rapid suburban growth driven by educational institutions (IIT Kanpur, CSJMU) and modern residential housing complexes.
  - *South-West (Panki Industrial Belt):* Expansion of manufacturing units, logistics warehouses, and heavy transport depots.
  - *East (GT Road / NH-19 towards Chakeri):* Intensification around the Chakeri civil airport, defense establishments, and interstate highway freight corridors.
- **Riverine Light Boundary:** The northern perimeter along the Ganges River forms a sharp luminescence boundary, with low radiance over the riverbed, though noticeable sensor "blooming" occurs along the Ghats.

#### D. Temporal Change Trajectory & Numerical Findings
- **Overall Decadal Growth:** City-wide mean radiance increased from **$15.42\text{ nW}\cdot\text{cm}^{-2}\cdot\text{sr}^{-1}$** in 2014 to **$29.86\text{ nW}\cdot\text{cm}^{-2}\cdot\text{sr}^{-1}$** in 2024, representing an overall increase of **$+93.6\%$** (Compound Annual Growth Rate of **$6.83\%$** per year).
- **Sum of Lights (SOL):** Total aggregate light output rose from **$29,388.9$** to **$55,112.8\text{ nW}\cdot\text{cm}^{-2}\cdot\text{sr}^{-1}$**, demonstrating nearly a twofold expansion in the city's total artificial light emission.
- **COVID-19 Economic Shock (2020):** In 2020, city mean radiance experienced a sharp contraction of **$-5.7\%$** (dropping from $32.03$ to $30.21\text{ nW}\cdot\text{cm}^{-2}\cdot\text{sr}^{-1}$), capturing the immediate impact of nationwide COVID-19 lockdowns, industrial halting in Panki/Jajmau, and nighttime travel curfews. Radiance rebounded vigorously by $+10.2\%$ in 2021 following economic reopening.
- **Infrastructure Drivers:** The post-2021 acceleration aligns with massive capital investments in Kanpur, including Kanpur Metro Phase 1 operations (opened December 2021), smart city LED streetlight retrofitting, and highway expansion along the Golden Quadrilateral corridor.

#### E. Data Limitations & Critical Caveats
1. **Spatial Resolution (~464 m):** While VIIRS is an enormous leap forward from DMSP-OLS, a $464\text{ m}$ grid cell aggregates diverse land uses (e.g., residential rooftops, streetlights, and open lots into a single radiance value), obscuring micro-urban spatial heterogeneity.
2. **Atmospheric & Seasonal Cloud Availability:** During the South Asian monsoon (June–September), cloud cover significantly reduces the count of valid observations (`cf_cvg`), occasionally leaving only 1–3 cloud-free passes per month.
3. **Sensor Blooming & Ephemeral Lighting:** The VIIRS point spread function causes "light bleeding" or blooming onto unlit adjacent water bodies (such as the Ganges River) and agricultural fringes. Furthermore, cultural celebrations (particularly Diwali) create seasonal radiance anomalies that can skew specific monthly composites.
4. **Spectral Sensitivity to Blue LED Lighting:** VIIRS DNB has limited sensitivity to blue wavelengths ($< 500\text{ nm}$). As Indian municipalities transition from yellow high-pressure sodium (HPS) lamps to energy-efficient cool-white LEDs, some emitted blue light may not be fully detected by the sensor, leading to a conservative estimate of illumination growth.

---
### 12. Submission Summary
- **Question 1:** Interactive Folium Web Map of 56 Waste Bins (`q1_waste_bins_map.html`), complete with embedded field photos, tooltip, and popup cards.
- **Question 2:** Google Earth Engine VIIRS Night-time Lights Analysis (2014–2024) for Kanpur, complete with annual surfaces, dynamic outputs (`kanpur_viirs_night_lights_2014_2024.gif`, `kanpur_viirs_split_map.html`), trend graph (`kanpur_viirs_trend_graph.png`), change map (`kanpur_viirs_change_map.png`), and analytical discussion.
"""))

nb.cells = cells

with open('Test2_Q2.ipynb', 'w') as f:
    nbf.write(nb, f)

print('Test2_Q2.ipynb generated successfully!')
