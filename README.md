# Informations:
This code generates a series of self-consistent models from a chosen lunar reference model.

Please find more details in the paper below:
Yun-Ze Cheng and Hrvoje Tkalčić (202*), Large lunar core constrained by S-wave shadow zone onsets from Apollo data, 
Nature Communications, *****.

Authors are from the Research School of Earth Sciences, The Australian National University, 142 Mills Road, 2601 ACT, Canberra, Australia

# Instructions:
1. Functions used here are listed in requirement.txt

2. The Input is a reference model in the directory called "Model".

3. You could simply run (./run.sh)

4. The output will be generated in the directory called "Output", including the model file and figures.

5. The output on your terminal will be...

============================================================
Starting Seismic Model Parameter Sweep
============================================================
Target Models: Garcia-2019-M2_playground
Mode: Core Ratios
Values: 0.8 1.4 2.0
PML Thickness (km): Auto-detect
------------------------------------------------------------

************************************************************
Processing Target Model: Garcia-2019-M2_playground
************************************************************
Using Moho Depth: 28 km
['/Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Model/Garcia-2019-M2_playground']
/Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Output/Garcia-2019-M2_playground/PNG
--- Initializing Model ---
Processing: /Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Model/Garcia-2019-M2_playground/G19-M2_updateQ.model
  -> Total Mass: 7.3644e+22, Mean Density: 3354.0744
[{'model_path': '/Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Model/Garcia-2019-M2_playground/G19-M2_updateQ.model', 'mean_density': 3354.0743772603005, 'total_mass': 7.3643726952665375e+22, 'df':          radius  density     Vpv     Vsv   Q-kappa     Q-mu
0           0.0   4550.0  4000.0     0.0  57823.00     1.00
1        1100.0   4550.0  4000.0     0.0  57823.00     1.00
2        2100.0   4550.0  4000.0     0.0  57823.00     1.00
3        3100.0   4550.0  4000.0     0.0  57823.00     1.00
4        4100.0   4550.0  4000.0     0.0  57823.00     1.00
...         ...      ...     ...     ...       ...      ...
1735  1733100.0   2600.0  3200.0  1800.0   6667.84  2963.48
1736  1734100.0   2600.0  3200.0  1800.0   6667.84  2963.48
1737  1735100.0   2600.0  3200.0  1800.0   6667.84  2963.48
1738  1736100.0   2600.0  3200.0  1800.0   6667.84  2963.48
1739  1737100.0   2600.0  1000.0   500.0   6667.84  2963.48

[1740 rows x 6 columns]}]

################ PROCESSING TARGET: 0.8 (ratio) ################

=== Step 1: Modify Core Size ===
[INFO] Modifying core size for: G19-M2_updateQ.model to target ratio 0.8
MAX:  1737100.0
New MAX:  1737100.0
[INFO] Model has been interpolated to a 1 km grid and duplicates removed.
[INFO] --pml-thickness-idx not provided. Auto-detecting PML start...
[INFO] Smoothing PML velocities to Vp=8.07 km/s, Vs=4.48 km/s.
331000.0 414000.0
0.7995169082125604 0.8
[INFO] Original core radius: 414.00 km (Index: 1324)
[INFO] Target radius 331.20 km -> Actual: 331.00 km (Index: 1407)
moho_index: 29
Core decreasing!

=== Step 2: Redistribute Mass ===
Using specified Moho depth: 28 km for model G19-M2_updateQ_0.8x_331km.model
0.9927346290487524
0.007265370951247449
  -> Mantle Density: 3401.8751 -> 3381.5653
  -> Core Density:   4549.7922 -> 4712.6002
1407 4712.600154471094

=== Step 3: Finalize Models (Add Discontinuities & Create .nd) ===
[INFO] Creating explicit discontinuities at Moho (idx 29) and CMB (idx 1407).
[INFO] Creating TauP .nd file: G19-M2_updateQ_0.8x_331km.nd
[SUCCESS] Saved .nd file to /Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Output/Garcia-2019-M2_playground/Model/G19-M2_updateQ_0.8x_331km.nd

=== Step 4: Generate Comparison Plots ===

[INFO] Plotting comparison between:
  - Original: G19-M2_updateQ.model
  - Final:    G19-M2_updateQ_0.8x_331km.model
[INFO] Saved comparison plot: /Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Output/Garcia-2019-M2_playground/PNG/G19-M2_updateQ_vs_final_core-ratio-0.8.png

################ PROCESSING TARGET: 1.4 (ratio) ################

=== Step 1: Modify Core Size ===
[INFO] Modifying core size for: G19-M2_updateQ.model to target ratio 1.4
MAX:  1737100.0
New MAX:  1737100.0
[INFO] Model has been interpolated to a 1 km grid and duplicates removed.
[INFO] --pml-thickness-idx not provided. Auto-detecting PML start...
[INFO] Smoothing PML velocities to Vp=8.07 km/s, Vs=4.48 km/s.
580000.0 414000.0
1.4009661835748792 1.4
[INFO] Original core radius: 414.00 km (Index: 1324)
[INFO] Target radius 579.60 km -> Actual: 580.00 km (Index: 1158)
moho_index: 29
Core increasing!

=== Step 2: Redistribute Mass ===
Using specified Moho depth: 28 km for model G19-M2_updateQ_1.4x_580km.model
0.9609107090685044
0.03908929093149572
  -> Mantle Density: 3391.4805 -> 3362.9339
  -> Core Density:   4365.3993 -> 4086.9642
1158 4086.964245341359

=== Step 3: Finalize Models (Add Discontinuities & Create .nd) ===
[INFO] Creating explicit discontinuities at Moho (idx 29) and CMB (idx 1158).
[INFO] Creating TauP .nd file: G19-M2_updateQ_1.4x_580km.nd
[SUCCESS] Saved .nd file to /Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Output/Garcia-2019-M2_playground/Model/G19-M2_updateQ_1.4x_580km.nd

=== Step 4: Generate Comparison Plots ===

[INFO] Plotting comparison between:
  - Original: G19-M2_updateQ.model
  - Final:    G19-M2_updateQ_1.4x_580km.model
[INFO] Saved comparison plot: /Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Output/Garcia-2019-M2_playground/PNG/G19-M2_updateQ_vs_final_core-ratio-1.4.png

################ PROCESSING TARGET: 2.0 (ratio) ################

=== Step 1: Modify Core Size ===
[INFO] Modifying core size for: G19-M2_updateQ.model to target ratio 2.0
MAX:  1737100.0
New MAX:  1737100.0
[INFO] Model has been interpolated to a 1 km grid and duplicates removed.
[INFO] --pml-thickness-idx not provided. Auto-detecting PML start...
[INFO] Smoothing PML velocities to Vp=8.07 km/s, Vs=4.48 km/s.
828000.0 414000.0
2.0 2.0
[INFO] Original core radius: 414.00 km (Index: 1324)
[INFO] Target radius 828.00 km -> Actual: 828.00 km (Index: 910)
moho_index: 29
Core increasing!

=== Step 2: Redistribute Mass ===
Using specified Moho depth: 28 km for model G19-M2_updateQ_2.0x_828km.model
0.8862726755128632
0.11372732448713697
  -> Mantle Density: 3379.9750 -> 3320.2637
  -> Core Density:   4250.0808 -> 3944.3182
910 3944.3182044226714

=== Step 3: Finalize Models (Add Discontinuities & Create .nd) ===
[INFO] Creating explicit discontinuities at Moho (idx 29) and CMB (idx 910).
[INFO] Creating TauP .nd file: G19-M2_updateQ_2.0x_828km.nd
[SUCCESS] Saved .nd file to /Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Output/Garcia-2019-M2_playground/Model/G19-M2_updateQ_2.0x_828km.nd

=== Step 4: Generate Comparison Plots ===

[INFO] Plotting comparison between:
  - Original: G19-M2_updateQ.model
  - Final:    G19-M2_updateQ_2.0x_828km.model
[INFO] Saved comparison plot: /Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Output/Garcia-2019-M2_playground/PNG/G19-M2_updateQ_vs_final_core-ratio-2.0.png

[INFO] Generating summary plot for the parameter sweep...
[INFO] Saved summary plot: /Tdata/yunze/Project-1_Core-shadow-zone-modelling/Code/Code-for-NC/Output/Garcia-2019-M2_playground/PNG/summary_density_vs_core_radius_Garcia-2019-M2_playground.png
Finished processing for Garcia-2019-M2_playground.
============================================================
Parameter sweep finished successfully.
============================================================