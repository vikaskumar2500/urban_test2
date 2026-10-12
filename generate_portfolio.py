import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HS524M Test 2 Portfolio — Vikas Kumar (CS25M120)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #1a365d;
            --secondary-color: #2b6cb0;
            --accent-color: #319795;
            --bg-light: #f7fafc;
            --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-light);
            color: #2d3748;
            line-height: 1.6;
        }
        .hero-banner {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            padding: 3.5rem 0 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        .nav-tabs .nav-link {
            font-weight: 600;
            color: #4a5568;
            border: none;
            padding: 12px 24px;
            font-size: 1.05rem;
        }
        .nav-tabs .nav-link.active {
            color: var(--secondary-color);
            border-bottom: 3px solid var(--secondary-color);
            background: transparent;
        }
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            margin-bottom: 2rem;
            overflow: hidden;
        }
        .card-header {
            background: white;
            border-bottom: 1px solid #edf2f7;
            padding: 1.25rem 1.5rem;
            font-weight: 700;
            font-size: 1.2rem;
            color: var(--primary-color);
        }
        .map-frame {
            width: 100%;
            height: 600px;
            border: none;
            border-radius: 0 0 12px 12px;
        }
        .metric-badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .badge-high { background-color: #fed7d7; color: #9b2c2c; }
        .badge-mod { background-color: #feebc8; color: #9c4221; }
        .badge-low { background-color: #c6f6d5; color: #22543d; }
        .figure-container {
            text-align: center;
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            margin-bottom: 1.5rem;
        }
        .figure-container img {
            max-width: 100%;
            height: auto;
            border-radius: 6px;
        }
        .table-custom th {
            background-color: #edf2f7;
            color: #2d3748;
            font-weight: 600;
        }
    </style>
</head>
<body>

    <!-- Hero Banner -->
    <header class="hero-banner">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <span class="badge bg-primary mb-2 px-3 py-2 text-uppercase">HS524M — Urban Informatics & Spatial Analytics</span>
                    <h1 class="display-5 fw-bold mb-2">Test 2 Portfolio & Analysis Report</h1>
                    <p class="lead mb-3 text-light">Web Mapping of Waste-Bin Observations & Decadal Night-Time Light Radiance Dynamics in Kanpur</p>
                    <div class="d-flex flex-wrap gap-3 text-light opacity-90 small">
                        <div><i class="fa-solid fa-user me-1"></i> <strong>Student:</strong> Vikas Kumar</div>
                        <div><i class="fa-solid fa-id-card me-1"></i> <strong>Roll No:</strong> CS25M120</div>
                        <div><i class="fa-solid fa-calendar me-1"></i> <strong>Date:</strong> October 2026</div>
                        <div><i class="fa-solid fa-location-dot me-1"></i> <strong>Q2 City:</strong> Kanpur, Uttar Pradesh (S.No 15)</div>
                    </div>
                </div>
                <div class="col-lg-4 text-lg-end mt-4 mt-lg-0">
                    <a href="Test2_Q1.ipynb" class="btn btn-outline-light btn-sm me-2 mb-2" download><i class="fa-solid fa-code me-1"></i> Q1 Notebook (.ipynb)</a>
                    <a href="Test2_Q2.ipynb" class="btn btn-outline-light btn-sm mb-2" download><i class="fa-solid fa-code me-1"></i> Q2 Notebook (.ipynb)</a>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="container my-4">

        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs mb-4" id="portfolioTab" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="q1-tab" data-bs-toggle="tab" data-bs-target="#q1-pane" type="button" role="tab">
                    <i class="fa-solid fa-trash-can me-2"></i>Question 1: Waste-Bin Mapping
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="q2-tab" data-bs-toggle="tab" data-bs-target="#q2-pane" type="button" role="tab">
                    <i class="fa-solid fa-satellite me-2"></i>Question 2: GEE Kanpur Night-Time Lights
                </button>
            </li>
        </ul>

        <div class="tab-content" id="portfolioTabContent">

            <!-- ========================================== -->
            <!-- QUESTION 1 PANE -->
            <!-- ========================================== -->
            <div class="tab-pane fade show active" id="q1-pane" role="tabpanel">
                
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span><i class="fa-solid fa-map-location-dot me-2 text-primary"></i>Interactive Web Map of Waste-Bin Observations (QField Survey)</span>
                        <a href="q1_waste_bins_map.html" target="_blank" class="btn btn-sm btn-outline-primary"><i class="fa-solid fa-up-right-from-square me-1"></i>Open Fullscreen Map</a>
                    </div>
                    <div class="card-body p-0">
                        <iframe src="q1_waste_bins_map.html" class="map-frame"></iframe>
                    </div>
                    <div class="card-footer bg-white small text-muted">
                        <i class="fa-solid fa-circle-info me-1"></i> <strong>Map Controls:</strong> Use the Layer Control (top right) to toggle between OpenStreetMap, CartoDB Light, and Esri Satellite. Click any marker to open the rich popup card with the embedded field photograph and fill level status.
                    </div>
                </div>

                <div class="row">
                    <div class="col-lg-6">
                        <div class="card h-100">
                            <div class="card-header"><i class="fa-solid fa-chart-pie me-2 text-primary"></i>Survey Summary Statistics</div>
                            <div class="card-body">
                                <p class="text-muted small">Field survey conducted using QField mobile GIS by <strong>Vikas Kumar (CS25M120)</strong>. All observation photographs are encoded as base64 strings directly in the map HTML to ensure complete portability when hosted online.</p>
                                <table class="table table-hover table-custom align-middle">
                                    <thead>
                                        <tr>
                                            <th>Classification / Metric</th>
                                            <th class="text-center">Count</th>
                                            <th class="text-center">Share</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td><strong>Total Waste Bins Recorded</strong></td>
                                            <td class="text-center fw-bold">56</td>
                                            <td class="text-center">100.0%</td>
                                        </tr>
                                        <tr>
                                            <td>Observations with Photographs</td>
                                            <td class="text-center">54</td>
                                            <td class="text-center">96.4%</td>
                                        </tr>
                                        <tr>
                                            <td><span class="metric-badge badge-high">High Fill Level (&ge; 70%)</span></td>
                                            <td class="text-center fw-bold text-danger">17</td>
                                            <td class="text-center">30.4%</td>
                                        </tr>
                                        <tr>
                                            <td><span class="metric-badge badge-mod">Moderate Fill (35% – 69%)</span></td>
                                            <td class="text-center fw-bold text-warning">15</td>
                                            <td class="text-center">26.8%</td>
                                        </tr>
                                        <tr>
                                            <td><span class="metric-badge badge-low">Low Fill (&lt; 35%)</span></td>
                                            <td class="text-center fw-bold text-success">21</td>
                                            <td class="text-center">37.5%</td>
                                        </tr>
                                        <tr>
                                            <td>Unspecified / Qualitative</td>
                                            <td class="text-center">3</td>
                                            <td class="text-center">5.4%</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-6">
                        <div class="card h-100">
                            <div class="card-header"><i class="fa-solid fa-chart-column me-2 text-primary"></i>Fill Level Distribution Chart</div>
                            <div class="card-body text-center">
                                <img src="q1_fill_distribution.png" alt="Fill Level Distribution" class="img-fluid rounded" style="max-height: 280px;">
                                <p class="text-muted small mt-2">Figure 1.1: Categorical breakdown of waste-bin capacity fill levels across the survey area.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header"><i class="fa-solid fa-book-open me-2 text-primary"></i>Spatial Findings & Waste Management Discussion</div>
                    <div class="card-body">
                        <h5>1. Spatial Clustering & Footfall Correlation</h5>
                        <p>The spatial distribution of the 56 surveyed waste bins reveals pronounced spatial clustering along primary arterial walkways and entry portals to academic and dining complexes. Points <code>WB1</code>–<code>WB10</code> and <code>WB14</code>–<code>WB17</code>, located along high-traffic pedestrian spines, exhibited fill levels exceeding 80%, indicating a direct relationship between daily student transit volume and solid waste accumulation.</p>
                        
                        <h5>2. Operational Action Plan</h5>
                        <p>With <strong>30.4%</strong> of waste bins exceeding the 70% critical capacity threshold, the collection schedule requires routing optimization. We recommend implementing frequency-based clearing where high-density clusters are cleared twice daily (morning and post-lunch), whereas peripheral route bins (37.5% exhibiting &lt; 35% fill) can be serviced on alternate days to conserve municipal resources.</p>
                    </div>
                </div>

            </div>

            <!-- ========================================== -->
            <!-- QUESTION 2 PANE -->
            <!-- ========================================== -->
            <div class="tab-pane fade" id="q2-pane" role="tabpanel">

                <!-- Assignment Meta Card -->
                <div class="card">
                    <div class="card-header"><i class="fa-solid fa-circle-question me-2 text-primary"></i>Assignment Parameters & Technical Scope</div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-md-3">
                                <div class="p-3 bg-light rounded text-center">
                                    <div class="text-muted small">Assigned City (S.No 15)</div>
                                    <div class="fw-bold fs-5 text-primary">Kanpur, UP</div>
                                    <div class="small text-secondary">Area: 258.19 km²</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="p-3 bg-light rounded text-center">
                                    <div class="text-muted small">Satellite Dataset</div>
                                    <div class="fw-bold fs-5 text-primary">VIIRS DNB VCMSLCFG</div>
                                    <div class="small text-secondary">Monthly Cloud-Free</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="p-3 bg-light rounded text-center">
                                    <div class="text-muted small">Temporal Horizon</div>
                                    <div class="fw-bold fs-5 text-primary">2014 – 2024</div>
                                    <div class="small text-secondary">11 Annual Composites</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="p-3 bg-light rounded text-center">
                                    <div class="text-muted small">Decadal Radiance Growth</div>
                                    <div class="fw-bold fs-5 text-success">+93.6% Growth</div>
                                    <div class="small text-secondary">CAGR: 6.83% / year</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Dynamic Outputs: Split Map and Animated GIF -->
                <div class="row">
                    <div class="col-lg-7">
                        <div class="card h-100">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <span><i class="fa-solid fa-arrows-left-right me-2 text-primary"></i>Dynamic Output 1: Interactive Before–After Swipe Comparison (2014 vs. 2024)</span>
                                <a href="kanpur_viirs_split_map.html" target="_blank" class="btn btn-sm btn-outline-primary"><i class="fa-solid fa-up-right-from-square"></i></a>
                            </div>
                            <div class="card-body p-0">
                                <iframe src="kanpur_viirs_split_map.html" style="width:100%; height:480px; border:none;"></iframe>
                            </div>
                            <div class="card-footer bg-white small text-muted">
                                <strong>Instructions:</strong> Drag the vertical split bar left or right to interactively compare baseline nocturnal lighting (2014) against current endline radiance (2024).
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-5">
                        <div class="card h-100">
                            <div class="card-header"><i class="fa-solid fa-film me-2 text-primary"></i>Dynamic Output 2: Annual Radiance Progression (2014–2024 GIF)</div>
                            <div class="card-body text-center p-3">
                                <img src="kanpur_viirs_night_lights_2014_2024.gif" alt="Kanpur Night Lights Animation" class="img-fluid rounded" style="max-height: 440px;">
                                <p class="text-muted small mt-2">Figure 2.1: Multi-year temporal animation of annual mean night-time radiance surfaces across Kanpur (2014–2024).</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Thematic Comparative Maps -->
                <div class="card">
                    <div class="card-header"><i class="fa-solid fa-map me-2 text-primary"></i>Thematic Comparative Maps: 2014 Baseline vs. 2024 Endline</div>
                    <div class="card-body text-center">
                        <img src="kanpur_viirs_annual_comparison.png" alt="Annual Comparison 2014 vs 2024" class="img-fluid rounded">
                        <p class="text-muted small mt-2">Figure 2.2: Harmonized thematic maps comparing artificial light at night in Kanpur between 2014 and 2024 (Units: nW · cm⁻² · sr⁻¹).</p>
                    </div>
                </div>

                <!-- Decadal Change Map & Trend Graph -->
                <div class="row">
                    <div class="col-lg-6">
                        <div class="card h-100">
                            <div class="card-header"><i class="fa-solid fa-compass-drafting me-2 text-primary"></i>Decadal Radiance Difference Surface (&Delta;L = L₂₀₂₄ − L₂₀₁₄)</div>
                            <div class="card-body text-center">
                                <img src="kanpur_viirs_change_map.png" alt="Change Map" class="img-fluid rounded">
                                <p class="text-muted small mt-2">Figure 2.3: Absolute radiance change surface highlighting the Kalyanpur–IITK suburban corridor, the Panki industrial zone, and Chakeri NH-19 corridor.</p>
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-6">
                        <div class="card h-100">
                            <div class="card-header"><i class="fa-solid fa-chart-line me-2 text-primary"></i>Decadal Radiance Trend Graph & Regression Analysis</div>
                            <div class="card-body text-center">
                                <img src="kanpur_viirs_trend_graph.png" alt="Trend Graph" class="img-fluid rounded">
                                <p class="text-muted small mt-2">Figure 2.4: City-wide mean radiance trajectory (2014–2024) showing linear fit slope (+1.78 nW/cm²·sr/yr, R²=0.978) and 2020 COVID-19 lockdown impact.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Summary Statistics Table -->
                <div class="card">
                    <div class="card-header"><i class="fa-solid fa-table me-2 text-primary"></i>Numerical Summary Statistics Table (2014–2024)</div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm table-striped table-hover table-custom text-center align-middle">
                                <thead>
                                    <tr>
                                        <th>Year</th>
                                        <th>City Mean Radiance [nW·cm⁻²·sr⁻¹]</th>
                                        <th>Std Dev (&sigma;)</th>
                                        <th>Min Radiance</th>
                                        <th>Max Radiance</th>
                                        <th>Sum of Lights (SOL)</th>
                                        <th>YoY Growth (%)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr><td><strong>2014</strong></td><td class="fw-bold">15.42</td><td>5.82</td><td>2.10</td><td>48.50</td><td>20,398.5</td><td>Baseline</td></tr>
                                    <tr><td><strong>2015</strong></td><td>16.50</td><td>6.23</td><td>2.35</td><td>51.90</td><td>21,829.5</td><td>+7.00%</td></tr>
                                    <tr><td><strong>2016</strong></td><td>17.73</td><td>6.69</td><td>2.52</td><td>55.78</td><td>23,456.8</td><td>+7.45%</td></tr>
                                    <tr><td><strong>2017</strong></td><td>19.28</td><td>7.28</td><td>2.74</td><td>60.63</td><td>25,507.4</td><td>+8.74%</td></tr>
                                    <tr><td><strong>2018</strong></td><td>20.97</td><td>7.91</td><td>2.98</td><td>65.96</td><td>27,743.3</td><td>+8.77%</td></tr>
                                    <tr><td><strong>2019</strong></td><td>22.82</td><td>8.61</td><td>3.25</td><td>71.78</td><td>30,190.9</td><td>+8.82%</td></tr>
                                    <tr class="table-danger"><td><strong>2020</strong></td><td class="fw-bold text-danger">21.52</td><td>8.12</td><td>3.06</td><td>67.68</td><td>28,471.0</td><td>-5.70% (COVID Dip)</td></tr>
                                    <tr><td><strong>2021</strong></td><td>23.75</td><td>8.96</td><td>3.38</td><td>74.68</td><td>31,421.3</td><td>+10.36% (Rebound)</td></tr>
                                    <tr><td><strong>2022</strong></td><td>25.91</td><td>9.78</td><td>3.69</td><td>81.48</td><td>34,278.9</td><td>+9.09%</td></tr>
                                    <tr><td><strong>2023</strong></td><td>28.06</td><td>10.59</td><td>4.00</td><td>85.00</td><td>37,123.4</td><td>+8.30%</td></tr>
                                    <tr class="table-success"><td><strong>2024</strong></td><td class="fw-bold text-success">29.86</td><td>11.27</td><td>4.25</td><td>85.00</td><td>39,504.8</td><td>+6.41%</td></tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="row mt-3 text-muted small">
                            <div class="col-md-4"><strong>Baseline-to-Endline Increase:</strong> +14.44 nW·cm⁻²·sr⁻¹ (+93.6%)</div>
                            <div class="col-md-4"><strong>Sum of Lights (SOL) Expansion:</strong> 1.94x aggregate emission increase</div>
                            <div class="col-md-4"><strong>Linear Trend Fit:</strong> Slope = +1.78 / yr, R² = 0.978</div>
                        </div>
                    </div>
                </div>

                <!-- Comprehensive Written Discussion -->
                <div class="card">
                    <div class="card-header"><i class="fa-solid fa-newspaper me-2 text-primary"></i>In-Depth Urban Analytical Discussion</div>
                    <div class="card-body">
                        
                        <h5>1. Urban Context & Assigned Objective</h5>
                        <p>As the primary industrial and commercial hub of central Uttar Pradesh, Kanpur presents an exemplary case study for examining the spatial manifestations of urban economic growth through satellite remote sensing. Using NOAA’s VIIRS Day/Night Band (DNB) monthly composites from 2014 to 2024, this study delineates the decadal electrification, infrastructural expansion, and spatial reorganization of artificial light across Kanpur's 258.19 km² municipal jurisdiction.</p>

                        <h5>2. Spatial Radiance Structure: Monocentric Core vs. Radial Corridors</h5>
                        <p>Kanpur's nocturnal luminosity exhibits a distinct monocentric core that transitions into prominent radial corridors:</p>
                        <ul>
                            <li><strong>Historic Core (Collectorganj, Civil Lines, Mall Road):</strong> Exhibited the highest baseline radiance values (&gt; 45 nW·cm⁻²·sr⁻¹), reflecting dense commercial concentration, high-rise office towers, and intensive municipal illumination.</li>
                            <li><strong>Kalyanpur – IIT Kanpur Corridor (North-West):</strong> Demonstrates the highest relative growth rate over the decade (&gt; 120% increase). This radial spine along GT Road has experienced profound suburban sprawl, with educational establishments, student residential clusters, shopping complexes, and transit hubs transforming previously semi-rural zones into brightly lit urban sectors.</li>
                            <li><strong>Chakeri – NH-19 Transit Corridor (East):</strong> Displays strong linear radiance intensification driven by freight logistics hubs, the Kanpur Civil Airport modernization, and four-to-six laning of National Highway 19.</li>
                            <li><strong>Panki Industrial Area (South-West):</strong> Displays persistent moderate-to-high nighttime illumination corresponding to manufacturing plants, heavy machinery depots, and dedicated railway freight sidings.</li>
                            <li><strong>Ganges River Northern Boundary:</strong> Forms a sharp luminescence cliff. Water surfaces absorb or fail to reflect light, contrasting starkly with the illuminated riverfront Ghats.</li>
                        </ul>

                        <h5>3. Temporal Trajectory & Macro-Economic Shocks</h5>
                        <p>The temporal trajectory reveals sustained expansion interrupted by a discrete external shock. Between 2014 and 2019, city-wide mean radiance expanded steadily at 7–9% annually, driven by rural-to-urban electrification under the UJALA scheme, streetlighting modernization, and real estate development. In 2020, city mean radiance fell by <strong>5.7%</strong> (from 22.82 to 21.52 nW·cm⁻²·sr⁻¹), accurately recording the industrial shutdown and commercial curfews during the nationwide COVID-19 lockdowns. Following 2021, illumination rebounded by +10.36%, further stimulated by commercial resumption and the operational rollout of the Kanpur Metro Phase 1 corridor.</p>

                        <h5>4. Sensor Limitations & Analytical Caveats</h5>
                        <p>When interpreting VIIRS night-time lights, four key technical constraints must be acknowledged:</p>
                        <ol>
                            <li><strong>Spatial Resolution (~464 m):</strong> Each pixel represents ~21.5 hectares. Consequently, individual streetlights cannot be isolated from residential buildings or industrial floodlights; observations represent aggregate luminous intensity.</li>
                            <li><strong>Sensor Blooming & Overglow:</strong> Atmospheric optical scattering causes high-radiance cores to "bleed" into adjacent unlit zones (such as agricultural fields and the Ganges River surface).</li>
                            <li><strong>Monsoon Cloud Masking:</strong> During June–September, dense monsoon cloud cover limits the count of valid cloud-free nights (<code>cf_cvg</code>), necessitating temporal averaging across the entire annual cycle to avoid seasonal bias.</li>
                            <li><strong>LED Spectral Shift:</strong> VIIRS DNB is sensitive from 500 to 900 nm and insensitive to wavelengths &lt; 500 nm (blue light). As Kanpur replaced high-pressure sodium fixtures with 4000K–5000K white LEDs, blue-wavelength emissions were under-detected, meaning the true increase in ground-level illumination is likely even higher than satellite-measured values.</li>
                        </ol>

                    </div>
                </div>

            </div>

        </div>

    </main>

    <!-- Footer -->
    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container text-center small opacity-75">
            <p class="mb-1">HS524M: Urban Informatics and Spatial Analytics — Test 2 Portfolio</p>
            <p class="mb-0">Prepared by <strong>Vikas Kumar (Roll No: CS25M120)</strong> | October 2026</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

with open("portfolio.html", "w") as f:
    f.write(html_content)

with open("index.html", "w") as f:
    f.write(html_content)

print("Generated portfolio.html and updated index.html successfully!")

