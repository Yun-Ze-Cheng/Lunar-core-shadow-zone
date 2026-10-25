# Informations:
This code generates a series of self-consistent models from a chosen lunar reference model.

Please find more details in the paper below:
Yun-Ze Cheng and Hrvoje Tkalčić (202*), Large lunar core constrained by S-wave shadow zone onsets from Apollo data, 
Nature Communications, *****.

We also provided the synthetics. 1-hour synthetic seismograms are computed using Yspec (1), in the frequency band 0.001–0.5 Hz. The source mechanism simulates tidal forces by placing the source on a horizontal fault plane at 900 km (2, 3) with a similar moment magnitude (~3, 10e13 Nm, 4). Stations are placed along the equator with an inter-station distance of 1˚ for the end-member models with multi-layering attenuation factors for P and S from previous seismic data analysis (3, 4) to deep moonquake M2 (5), LCM, M3 (5), and W11 (6). The waveforms of the N-component could be treated as Transverse-component based on the setting.

1. Al-Attar, D. & Woodhouse, J. H. Calculation of seismic displacement fields in self-gravitating earth models—applications of minors vectors and symplectic structure. Geophys. J. Int. 175, 1176–1208, 2008.
2. Wang, Y., Takenaka, H., Jiang, X. & Lei, J. Modelling two-dimensional global seismic wave propagation in a laterally heterogeneous whole-Moon model. Geophys. J. Int. 192, 1271–1287 (2013).
3.	Wang, Y., Luo, Y., Qin, Y. & Zhang, X. Global SH-wavefield calculation for a two-dimensional whole-Earth model with the parallel hybrid PSM/FDM algorithm. Earthq. Sci. 27, 277–284 (2014).
4. Onodera, K., Kawamura, T., Tanaka, S., Ishihara, Y. & Maeda, T. Quantitative Evaluation of the Lunar Seismic Scattering and Comparison Between the Earth, Mars, and the Moon. J. Geophys. Res.: Planets 127, (2022).
5. Garcia, R. F. et al. Lunar Seismology: An Update on Interior Structure Models. Space Sci. Rev. 215, 50, 2019.
6. Weber, R. C., Lin, P.-Y., Garnero, E. J., Williams, Q. & Lognonné, P. Seismic Detection of the Lunar Core. Science 331, 309–312, 2011.

Authors are from the Research School of Earth Sciences, The Australian National University, 142 Mills Road, 2601 ACT, Canberra, Australia.

# Instructions for the code:
1. Functions used here are listed in requirement.txt

2. The Input is a reference model in the directory called "Model".

3. You could simply run (./run.sh)

4. The output will be generated in the directory called "Output", including the model file and figures.
