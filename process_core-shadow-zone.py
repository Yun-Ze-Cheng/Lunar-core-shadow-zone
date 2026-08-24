import os
import glob
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
import argparse
import sys
import csv
import matplotlib
matplotlib.use('Agg')

# ===================================================================
# ANSI Color codes for rich terminal output
# ===================================================================
class Colors:
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# ===================================================================
# Functions
# ===================================================================
def calc_mean_density(radius, density):
    """Calculates the mean density of a planetary model."""
    total_mass = 0
    total_volume = 0
    for i in range(len(radius) - 1):
        r1, r2 = radius[i], radius[i+1]
        rho1, rho2 = density[i], density[i+1]
        volume = (4/3) * math.pi * abs(r1**3 - r2**3)
        avg_density = (rho1 + rho2) / 2
        mass = avg_density * volume
        total_mass += mass
        total_volume += volume
    if total_volume == 0:
        return 0, 0, 0
    return abs(total_mass) / abs(total_volume), abs(total_mass), abs(total_volume)

def plot_model(df, title='', save_path=None, show=True, label=None, axarr=None, color=None, linestyle=None, linewidth=2):
    """Plots the seismic properties of a model."""
    if axarr is None:
        fig, axs = plt.subplots(1, 4, figsize=(9, 6))
    else:
        axs = axarr
    depth = (df.radius.max() / 1000) - (df.radius / 1000)
    axs[0].plot(df.Vpv / 1000, depth, linestyle=linestyle, lw=linewidth, label=label, color=color)
    axs[1].plot(df.Vsv / 1000, depth, linestyle=linestyle, lw=linewidth, label=label, color=color)
    axs[2].plot(df.density / 1000, depth, linestyle=linestyle, lw=linewidth, label=label, color=color)
    axs[3].plot(1/df['Q-kappa'], depth, linestyle='-', lw=linewidth, label=label, color=color)
    axs[3].plot(1/df['Q-mu'], depth, linestyle='--', lw=linewidth, color=color)
    for i, name in enumerate(['Vp (km/s)', 'Vs (km/s)', 'Density (g/cm³)', 'Attenuation']):
        axs[i].set_xlabel(name, fontsize=18)
        axs[0].set_ylabel('Depth (km)', fontsize=18)
        axs[i].set_ylim(depth.min(), depth.max())
        axs[i].invert_yaxis()
        axs[i].tick_params(axis='x', labelsize=14)
        axs[i].tick_params(axis='y', labelsize=14)
        axs[i].xaxis.set_tick_params(labelsize=14)
        axs[i].yaxis.set_tick_params(labelsize=14)
        axs[i].yaxis.set_major_locator(MultipleLocator(200))
        axs[i].yaxis.set_minor_locator(MultipleLocator(50))
        axs[i].xaxis.set_major_locator(MultipleLocator(1))
        axs[i].xaxis.set_minor_locator(MultipleLocator(0.5))
        axs[2].xaxis.set_major_locator(MultipleLocator(1))
        axs[2].xaxis.set_minor_locator(MultipleLocator(0.2))
        axs[3].set_xscale('log')
        axs[3].set_xticks(np.logspace(-5, 1, 4))
        if i != 0:
            axs[i].set_yticklabels([])
        for pos in ['top', 'bottom', 'left', 'right']:
            axs[i].spines[pos].set_linewidth(1.5)
    if label:
        axs[2].legend(fontsize=10, ncol=2, bbox_to_anchor=(0.7, 1.1)) # Use one legend for clarity
    if axarr is None:
        if save_path:
            plt.savefig(save_path, dpi=300, transparent=True)
        plt.close(fig)

def mean_density_from_model_files(model_dirs, plot, figure_dir):
    """Processes all .model files in a directory to calculate their mean density."""
    results = []
    for model_dir in model_dirs:
        for model_path in glob.glob(os.path.join(model_dir, '*.model')):
            print(f"Processing: {model_path}")
            df = pd.read_csv(model_path, sep='\s+',
                             names=['radius', 'density', 'Vpv', 'Vsv', 'Q-kappa', 'Q-mu'])
            mean_density, total_mass, _ = calc_mean_density(df.radius.values, df.density.values)
            print(f"  -> Total Mass: {total_mass:.4e}, Mean Density: {Colors.BOLD}{mean_density:.4f}{Colors.RESET}")
            if plot:
                fig_name = os.path.splitext(os.path.basename(model_path))[0] + '_profile.png'
                fig_path = os.path.join(figure_dir, fig_name)
                plot_model(df, title=f"{os.path.basename(model_path)} Profile", save_path=fig_path, show=plot, linestyle='-', color='k')
            results.append({
                'model_path': model_path, 'mean_density': mean_density, 'total_mass': total_mass, 'df': df
            })
    return results

def modify_core_size(model_path, pml_thickness_idx, moho_depth_km, plot, figure_dir, new_core_size_km=None, new_core_ratio=None):
    """
    Modifies the core size based on a target radius (km) or a ratio.
    If shrinking, fills the new mantle region with average mantle properties.
    """
    if new_core_size_km:
        print(f"{Colors.CYAN}[INFO] Modifying core size for: {os.path.basename(model_path)} to target radius {new_core_size_km} km{Colors.RESET}")
    elif new_core_ratio:
        print(f"{Colors.CYAN}[INFO] Modifying core size for: {os.path.basename(model_path)} to target ratio {new_core_ratio}{Colors.RESET}")

    df_orig = pd.read_csv(model_path, sep='\s+',
                          names=['radius', 'density', 'Vpv', 'Vsv', 'Q-kappa', 'Q-mu'])
    # print(df_orig)
    max_radius_m = df_orig['radius'].max()
    print('MAX: ', max_radius_m)
    new_radius_grid_m_ = np.arange(0, max_radius_m , 1000)
    original_radius_m_inc = df_orig.radius.values#[::-1]
    new_radius_grid_m = np.append(new_radius_grid_m_, max_radius_m)
    print('New MAX: ', max(new_radius_grid_m))

    df_interp = pd.DataFrame()
    df_interp['radius'] = new_radius_grid_m#[::-1]
    for col in ['density', 'Vpv', 'Vsv', 'Q-kappa', 'Q-mu']:
        original_values_inc = df_orig[col].values#[::-1]
        interpolated_values = np.interp(new_radius_grid_m, original_radius_m_inc, original_values_inc)
        df_interp[col] = interpolated_values#[::-1]
    
    df_interp.drop_duplicates(subset=['radius'], keep='first', inplace=True)
    df_interp = df_interp.iloc[::-1]
    df_interp.reset_index(drop=True, inplace=True)
    print(f"{Colors.CYAN}[INFO] Model has been interpolated to a 1 km grid and duplicates removed.{Colors.RESET}")

    try:
        liquid_idx = df_interp.index[df_interp['Vsv'] == 0].tolist()[0]
    except IndexError:
        print(f"{Colors.RED}Error: Could not find liquid core (Vsv=0) in interpolated model. Aborting.{Colors.RESET}")
        return None, None, None, None

    ori_core_idx = liquid_idx
    ori_core_radius_m = df_interp.radius.at[ori_core_idx]

    if new_core_size_km:
        new_core_radius_m_target = new_core_size_km * 1000
    elif new_core_ratio:
        new_core_radius_m_target = ori_core_radius_m * new_core_ratio
        new_core_size_km = new_core_radius_m_target / 1000
    else:
        print(f"{Colors.RED}Error: Must provide either new_core_size_km or new_core_ratio.{Colors.RESET}")
        return None, None, None, None

    if pml_thickness_idx is None:
        print(f"{Colors.CYAN}[INFO] --pml-thickness-idx not provided. Auto-detecting PML start...{Colors.RESET}")
        # search_start_idx = ori_core_idx - 300
        # search_window = df_interp.iloc[search_start_idx:ori_core_idx]
        # print(search_start_idx, ori_core_idx)
        # pml_top_idx = search_window['Vpv'].idxmax()
        # pml_thickness_idx = ori_core_idx - pml_top_idx
        # print(f"{Colors.CYAN}[INFO] Auto-detected PML top at index {Colors.BOLD}{pml_top_idx}{Colors.RESET}{Colors.CYAN}, thickness: {Colors.BOLD}{pml_thickness_idx} km{Colors.RESET}")
        pml_thickness_idx = 0
    else:
        print(f"{Colors.CYAN}[INFO] Using provided PML thickness: {Colors.BOLD}{pml_thickness_idx} km{Colors.RESET}")

    pml_top_idx = ori_core_idx - pml_thickness_idx

    new_core_idx = (df_interp['radius'] - new_core_radius_m_target).abs().idxmin()
    mantle_vp_above_pml = df_interp.at[pml_top_idx - 1, 'Vpv']
    mantle_vs_above_pml = df_interp.at[pml_top_idx - 1, 'Vsv']
    mantle_density_above_pml = df_interp.at[pml_top_idx - 1, 'density']
    mantle_Qp_above_pml = df_interp.at[pml_top_idx - 1, 'Q-kappa']
    mantle_Qs_above_pml = df_interp.at[pml_top_idx - 1, 'Q-mu']
    
    pml_region_mask = (df_interp.index >= pml_top_idx) & (df_interp.index < ori_core_idx)
    df_interp.loc[pml_region_mask, 'Vpv'] = mantle_vp_above_pml
    df_interp.loc[pml_region_mask, 'Vsv'] = mantle_vs_above_pml
        
    print(f"{Colors.CYAN}[INFO] Smoothing PML velocities to Vp={mantle_vp_above_pml/1000:.2f} km/s, Vs={mantle_vs_above_pml/1000:.2f} km/s.{Colors.RESET}")

    actual_new_radius_m = df_interp.radius.at[new_core_idx]
    core_ratio = actual_new_radius_m / ori_core_radius_m
    print(actual_new_radius_m, ori_core_radius_m)
    print(core_ratio, round(core_ratio, 2))
    print(f"{Colors.CYAN}[INFO] Original core radius: {Colors.BOLD}{ori_core_radius_m/1000:.2f} km{Colors.RESET}{Colors.CYAN} (Index: {ori_core_idx}){Colors.RESET}")
    print(f"{Colors.CYAN}[INFO] Target radius {new_core_size_km:.2f} km -> Actual: {Colors.BOLD}{actual_new_radius_m/1000:.2f} km{Colors.RESET}{Colors.CYAN} (Index: {new_core_idx}){Colors.RESET}")

    df_new = df_interp.copy()
    surface_radius_m = df_interp['radius'].max()
    moho_radius_m = surface_radius_m - (moho_depth_km * 1000)
    moho_index = (df_interp['radius'] - moho_radius_m).abs().idxmin()
    print('moho_index:', moho_index)
    mantle_slice = df_interp.loc[moho_index:pml_top_idx]
    New_avg_props = {col: mantle_slice[col].mean() for col in ['density']}
    New_avg_props1 = {col: mantle_slice[col].mean() for col in ['Vpv']}
    New_avg_props2 = {col: mantle_slice[col].mean() for col in ['Vsv']}
    New_avg_props3 = {col: mantle_slice[col].mean() for col in ['Q-kappa']}
    New_avg_props4 = {col: mantle_slice[col].mean() for col in ['Q-mu']}
    if new_core_idx > ori_core_idx:
        print('Core decreasing!')
        fill_region = (df_new.index >= ori_core_idx) & (df_new.index < new_core_idx)
        for col, avg_val in New_avg_props.items():
            df_new.loc[fill_region, col] = mantle_density_above_pml
        for col, avg_val in New_avg_props1.items():
            df_new.loc[fill_region, col] = mantle_vp_above_pml
        for col, avg_val in New_avg_props2.items():
            df_new.loc[fill_region, col] = mantle_vs_above_pml
        for col, avg_val in New_avg_props3.items():
            df_new.loc[fill_region, col] = mantle_Qp_above_pml
        for col, avg_val in New_avg_props4.items():
            df_new.loc[fill_region, col] = mantle_Qs_above_pml
            
    elif new_core_idx < ori_core_idx:
        print('Core increasing!')
        fill_region = (df_new.index <= ori_core_idx) & (df_new.index > new_core_idx)
        for col, avg_val in New_avg_props.items():
            df_new.loc[fill_region, col] = df_interp.at[liquid_idx, col]
        for col, avg_val in New_avg_props1.items():
            df_new.loc[fill_region, col] = df_interp.at[liquid_idx, col]
        for col, avg_val in New_avg_props2.items():
            df_new.loc[fill_region, col] = df_interp.at[liquid_idx, col]
        for col, avg_val in New_avg_props3.items():
            df_new.loc[fill_region, col] = df_interp.at[liquid_idx, col]
        for col, avg_val in New_avg_props4.items():
            df_new.loc[fill_region, col] = df_interp.at[liquid_idx, col]
                        
    if plot:
        fig, axs = plt.subplots(1, 4, figsize=(9, 6))
        plot_model(df_orig, label='Original Input', axarr=axs, color='k', show=False, linestyle=':')
        plot_model(df_new, label=f'New CMB @ {new_core_size_km:.0f}km', axarr=axs, color='b', show=False, linestyle='-')
        pml_top_radius_m = df_new.radius.at[pml_top_idx]
        pml_top_depth_km = (df_new.radius.max() / 1000) - (pml_top_radius_m / 1000)
        for ax in axs:
            ax.axhline(y=pml_top_depth_km, color='r', linestyle='--', lw=1.5)
        axs[0].text(axs[0].get_xlim()[0], pml_top_depth_km + 50, 'PML Top', color='r', va='center', ha='left')
        fig_name = os.path.splitext(os.path.basename(model_path))[0] + f"_{round(core_ratio, 2)}x_{new_core_size_km:.0f}km_direct-change.png"
        fig_path = os.path.join(figure_dir, fig_name)
        plt.savefig(fig_path, dpi=300, transparent=True)
        plt.close(fig)

    return df_new, new_core_idx, core_ratio, pml_top_idx

def change_core_size_and_redistribute_mass(model_info, true_mass, moho_depth_km, plot, figure_dir, output_dir):
    """
    Redistributes mass in the mantle and core to match a reference total mass.
    """
    results = []
    for info in model_info:
        df = info['df']
        model_path = info['model_path']
        print(f"Using specified Moho depth: {Colors.BOLD}{moho_depth_km} km{Colors.RESET} for model {os.path.basename(model_path)}")
        surface_radius_m = df['radius'].max()
        moho_radius_m = surface_radius_m - (moho_depth_km * 1000)
        moho_index = (df['radius'] - moho_radius_m).abs().idxmin()
        core_index = info['core_boundary_index']

        if core_index <= moho_index:
            print(f"{Colors.RED}Warning: Core boundary index ({core_index}) is at or above the Moho index ({moho_index}). Skipping model {model_path}.{Colors.RESET}")
            continue

        Boundary_list = [moho_index, core_index]
        Radius, Density = df['radius'].tolist(), df['density'].tolist()
        _, total_mass_crust, _ = calc_mean_density(Radius[:Boundary_list[0]+1], Density[:Boundary_list[0]+1])
        _, total_mass_mantle, total_volume_mantle = calc_mean_density(Radius[Boundary_list[0]:Boundary_list[1]+1], Density[Boundary_list[0]:Boundary_list[1]+1])
        _, total_mass_core, total_volume_core = calc_mean_density(Radius[Boundary_list[1]:], Density[Boundary_list[1]:])
        total_mass = total_mass_crust + total_mass_mantle + total_mass_core
        total_mass_difference = true_mass - total_mass
        mantle_core_volume = total_volume_mantle + total_volume_core
        if mantle_core_volume == 0: continue
        total_mass_difference_tomantle = total_mass_difference * 0.8 #(total_volume_core / mantle_core_volume)
        total_mass_difference_tocore = total_mass_difference * 0.2   #(total_volume_mantle / mantle_core_volume)
        print(total_volume_mantle / mantle_core_volume)
        print(total_volume_core / mantle_core_volume)
        new_mantle_density = (total_mass_mantle + total_mass_difference_tomantle) / total_volume_mantle
        new_core_density = (total_mass_core + total_mass_difference_tocore) / total_volume_core
        original_mantle_density = df.loc[(df.index > moho_index) & (df.index < core_index), 'density'].mean()
        original_core_density = df.loc[df.index >= core_index, 'density'].mean()
        print(f"  -> Mantle Density: {original_mantle_density:.4f} -> {Colors.BOLD}{new_mantle_density:.4f}{Colors.RESET}")
        print(f"  -> Core Density:   {original_core_density:.4f} -> {Colors.BOLD}{new_core_density:.4f}{Colors.RESET}")
        df_new = df.copy()
        df_new.loc[(df_new.index > Boundary_list[0]) & (df_new.index < Boundary_list[1]), 'density'] = new_mantle_density
        df_new.loc[df_new.index >= Boundary_list[1], 'density'] = new_core_density
        print(Boundary_list[1], new_core_density)
        
        New_Vp_list, New_Vs_list = [], []
        for k in range(len(df_new)):
            Vp_ori, Vs_ori, Den_ori, Den_new = df['Vpv'][k], df['Vsv'][k], df['density'][k], df_new['density'][k]
            miu = (Vs_ori**2) * Den_ori
            kappa = (Vp_ori**2) * Den_ori - (4/3) * miu
            New_Vs = np.sqrt(miu / Den_new) if Den_new > 0 else 0
            New_Vp = np.sqrt((kappa + (4/3) * miu) / Den_new) if Den_new > 0 else 0
            New_Vp_list.append(New_Vp)
            New_Vs_list.append(New_Vs)
        ### Make sure the core density is constent
        df_new['Vpv'], df_new['Vsv'] = New_Vp_list, New_Vs_list
        df_new.loc[df_new.index >= Boundary_list[1], 'Vpv'] = np.mean(New_Vp_list[Boundary_list[1]:])

        new_model_name = os.path.splitext(os.path.basename(model_path))[0] + '.model'
        new_model_path = os.path.join(output_dir, new_model_name)
        df_new.to_csv(new_model_path, sep=' ', index=False, header=False, float_format='%.4f')

        if plot:
            fig, axs = plt.subplots(1, 4, figsize=(9, 6))
            plot_model(df, label='Before Mass-Redist', axarr=axs, color='r', show=False, linestyle='--')
            plot_model(df_new, label='After Mass-Redist', axarr=axs, color='b', show=False, linestyle='-')
            fig_name = os.path.splitext(os.path.basename(model_path))[0] + '_redistribute_mass_comparison.png'
            fig_path = os.path.join(figure_dir, fig_name)
            plt.savefig(fig_path, dpi=300, transparent=True)
            plt.close(fig)

        results.append({'output_model': new_model_path})
    return results

def plot_final_comparison(original_model_path, final_model_path, figure_dir, core_ratio):
    """Plots a comparison between the original and final processed models."""
    print(f"\n{Colors.CYAN}[INFO] Plotting comparison between:\n  - Original: {os.path.basename(original_model_path)}\n  - Final:    {os.path.basename(final_model_path)}{Colors.RESET}")
    df_original = pd.read_csv(original_model_path, sep='\s+',
                              names=['radius', 'density', 'Vpv', 'Vsv', 'Q-kappa', 'Q-mu'])
    df_final = pd.read_csv(final_model_path, sep=' ',
                           names=['radius', 'density', 'Vpv', 'Vsv', 'Q-kappa', 'Q-mu'])
    fig, axs = plt.subplots(1, 4, figsize=(9, 6))
    plot_model(df_original, label='Original Model', axarr=axs, color='k', linestyle='--', show=False)
    plot_model(df_final, label='Final Model', axarr=axs, color='r', linestyle='-', show=False)
    original_basename = os.path.splitext(os.path.basename(original_model_path))[0]
    fig_name = f"{original_basename}_vs_final_core-ratio-{round(core_ratio, 2)}.png"
    fig_path = os.path.join(figure_dir, fig_name)
    plt.savefig(fig_path, dpi=300, transparent=True)
    print(f"{Colors.CYAN}[INFO] Saved comparison plot: {fig_path}{Colors.RESET}")
    plt.close(fig)

def plot_summary_figure(summary_data, figure_dir, target_name, original_avg_density, original_core_density):
    """
    Plots a summary of core radius vs. final densities, including reference lines.
    """
    if not summary_data or len(summary_data) < 2:
        print(f"{Colors.YELLOW}WARNING: Not enough data points to generate a summary plot.{Colors.RESET}")
        return

    print(f"\n{Colors.CYAN}[INFO] Generating summary plot for the parameter sweep...{Colors.RESET}")
    
    df_summary = pd.DataFrame(summary_data).sort_values(by='core_radius_km')
    
    plt.style.use('seaborn-v0_8-paper')
    fig, ax = plt.subplots(figsize=(10, 7))

    # Plot mean and core densities from the sweep
    ax.plot(df_summary['core_radius_km'], df_summary['mean_density_g_cm3'], 'o-', color='navy', markersize=8, lw=2, label=f'Mean Density')
    ax.plot(df_summary['core_radius_km'], df_summary['core_density_g_cm3'], 's-', color='darkorange', markersize=8, lw=3.0, label=f'Core Density')

    # Add horizontal lines for original model properties
    ax.axhline(y=original_avg_density, color='green', linestyle='--', lw=2, label=f'Original Avg. Density ({original_avg_density:.3f})')
    ax.axhline(y=original_core_density, color='red', linestyle='--', lw=2, label=f'Original Core Density ({original_core_density:.3f})')

    ax.set_title(f'Density vs. Core Radius for {target_name}', fontsize=20, weight='bold')
    ax.set_xlabel('Core Radius (km)', fontsize=16)
    ax.set_ylabel('Density (g/cm³)', fontsize=16)
    # ax.set_ylim(3, 4)
    
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    ax.legend(fontsize=14)
    
    fig_name = f"summary_density_vs_core_radius_{target_name}.png"
    fig_path = os.path.join(figure_dir, fig_name)
    
    plt.tight_layout()
    plt.savefig(fig_path, dpi=300, transparent=False, facecolor='white')
    print(f"{Colors.CYAN}[INFO] Saved summary plot: {Colors.BOLD}{fig_path}{Colors.RESET}")
    plt.close(fig)

def create_discontinuities(df, moho_index, core_index):
    """
    Creates explicit discontinuities in the model dataframe by inserting rows.
    """
    print(f"{Colors.CYAN}[INFO] Creating explicit discontinuities at Moho (idx {moho_index}) and CMB (idx {core_index}).{Colors.RESET}")
    
    df_new = df.copy().reset_index(drop=True)
    
    # Define rows to insert
    core_discontinuity_row_top = df_new.loc[core_index].copy()
    moho_discontinuity_row_top = df_new.loc[moho_index].copy()
    
    # Insert rows at the correct locations. Order matters if indices are close.
    # We insert the row that's deeper first to not affect the index of the shallower one.
    if moho_index < core_index:
        df_new = pd.concat([df_new.iloc[:core_index+1], pd.DataFrame([core_discontinuity_row_top]), df_new.iloc[core_index+1:]]).reset_index(drop=True)
        df_new = pd.concat([df_new.iloc[:moho_index+1], pd.DataFrame([moho_discontinuity_row_top]), df_new.iloc[moho_index+1:]]).reset_index(drop=True)
        
        ### make sure the Moho works well 
        df_new.loc[moho_index].Vpv = df_new.loc[moho_index-1].Vpv
        df_new.loc[moho_index].Vsv = df_new.loc[moho_index-1].Vsv
        df_new.loc[moho_index].density = df_new.loc[moho_index-1].density
        df_new.loc[moho_index]['Q-kappa'] = df_new.loc[moho_index-1]['Q-kappa']
        df_new.loc[moho_index]['Q-mu'] = df_new.loc[moho_index-1]['Q-mu']

        df_new.loc[moho_index+1].Vpv = df_new.loc[moho_index+2].Vpv
        df_new.loc[moho_index+1].Vsv = df_new.loc[moho_index+2].Vsv
        df_new.loc[moho_index+1].density = df_new.loc[moho_index+2].density
        df_new.loc[moho_index+1]['Q-kappa'] = df_new.loc[moho_index+2]['Q-kappa']
        df_new.loc[moho_index+1]['Q-mu'] = df_new.loc[moho_index+2]['Q-mu']
        
        ### make sure the CMB works well 
        df_new.loc[core_index+1].Vpv = df_new.loc[core_index-1].Vpv
        df_new.loc[core_index+1].Vsv = df_new.loc[core_index-1].Vsv
        df_new.loc[core_index+1].density = df_new.loc[core_index-1].density
        df_new.loc[core_index+1]['Q-kappa'] = df_new.loc[core_index-1]['Q-kappa']
        df_new.loc[core_index+1]['Q-mu'] = df_new.loc[core_index-1]['Q-mu']
        
        df_new.loc[core_index+2].Vpv = df_new.loc[core_index+3].Vpv
        df_new.loc[core_index+2].Vsv = df_new.loc[core_index+3].Vsv
        df_new.loc[core_index+2].density = df_new.loc[core_index+3].density
        df_new.loc[core_index+2]['Q-kappa'] = df_new.loc[core_index+3]['Q-kappa']
        df_new.loc[core_index+2]['Q-mu'] = df_new.loc[core_index+3]['Q-mu']
        
    else: # Should not happen, but for completeness
        df_new = pd.concat([df_new.iloc[:moho_index+1], pd.DataFrame([moho_discontinuity_row_top]), df_new.iloc[moho_index+1:]]).reset_index(drop=True)
        df_new = pd.concat([df_new.iloc[:core_index+1], pd.DataFrame([core_discontinuity_row_top]), df_new.iloc[core_index+1:]]).reset_index(drop=True)

    return df_new

def create_nd_file(df_final, output_dir, final_model_basename):
    """
    Converts the final model DataFrame to a TauP-compatible .nd file.
    """
    nd_filename = os.path.splitext(final_model_basename)[0] + '.nd'
    target_path = os.path.join(output_dir, nd_filename)
    print(f"{Colors.CYAN}[INFO] Creating TauP .nd file: {nd_filename}{Colors.RESET}")

    df_nd = pd.DataFrame()
    df_nd['depth'] = (df_final['radius'].max() - df_final['radius']) / 1000.0
    df_nd['Vpv'] = df_final['Vpv'] / 1000.0
    df_nd['Vsv'] = df_final['Vsv'] / 1000.0
    df_nd['density'] = df_final['density'] / 1000.0
    df_nd['Qp'] = df_final['Q-kappa']
    df_nd['Qs'] = df_final['Q-mu']

    data_to_write = []
    for i in range(len(df_nd)):
        row = [
            f"{df_nd.at[i, 'depth']:.2f}", f"{df_nd.at[i, 'Vpv']:.2f}",
            f"{df_nd.at[i, 'Vsv']:.2f}", f"{df_nd.at[i, 'density']:.2f}",
            f"{df_nd.at[i, 'Qp']:.0f}", f"{df_nd.at[i, 'Qs']:.0f}"
        ]
        data_to_write.append(row)

    discontinuity_indices = df_nd[df_nd.duplicated(subset=['depth'], keep='first')].index.tolist()
    # print(liquid_idx, discontinuity_indices[1])
    # for variable in [discontinuity_indices[1]]:
        # print(df_nd['Vsv'][variable-1],df_nd['Vsv'][variable], df_nd['Vsv'][variable+1])
    
    if len(discontinuity_indices) >= 2:
        discontinuity_indices.sort()
        data_to_write.insert(discontinuity_indices[1] , ['outer-core'])
        data_to_write.insert(discontinuity_indices[0] , ['mantle'])
    elif len(discontinuity_indices) == 1:
         data_to_write.insert(discontinuity_indices[0] , ['mantle'])

    with open(target_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=' ')
        writer.writerows(data_to_write)
    print(f"{Colors.GREEN}[SUCCESS] Saved .nd file to {target_path}{Colors.RESET}")

def read_nd_file(filepath):
    """Reads a .nd file and converts it to a .model-like DataFrame."""
    try:
        df = pd.read_csv(filepath, sep='\s+', comment='#', names=['depth','Vpv','Vsv','density','Qp','Qs'],
                         on_bad_lines=lambda x: x[:-1] if len(x) > 6 else x, # Handles bad lines
                         skipinitialspace=True, engine='python')
        # Filter out non-numeric rows that might have slipped through
        df = df[pd.to_numeric(df['depth'], errors='coerce').notnull()]
        df = df.astype(float)
    except Exception as e:
        print(f"{Colors.RED}ERROR reading .nd file {filepath}: {e}{Colors.RESET}")
        return None

    df_model = pd.DataFrame()
    max_radius_km = max(df['depth'])
    df_model['radius'] = (max_radius_km - df['depth']) * 1000.0
    df_model['density'] = df['density'] * 1000.0
    df_model['Vpv'] = df['Vpv'] * 1000.0
    df_model['Vsv'] = df['Vsv'] * 1000.0
    df_model['Q-kappa'] = df['Qp']
    df_model['Q-mu'] = df['Qs']
    return df_model.sort_values(by='radius', ascending=False).reset_index(drop=True)

# ===============================================================
# Main Execution Block
# ===============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--target-name', type=str, required=True, help='Name of the target model set.')
    parser.add_argument('--base-dir', type=str, required=True, help='Base directory for Code/')
    parser.add_argument('--save-dir', type=str, required=True, help='Base directory for Output/.')
    parser.add_argument('--model-dir', type=str, required=True, help='Base directory for Model/.')
    parser.add_argument('--core-sizes', type=int, nargs='+', default=[], help='Target core sizes in kilometers.')
    parser.add_argument('--core-ratios', type=float, nargs='+', default=[], help='Target core sizes as a ratio of original.')
    parser.add_argument('--plot', action='store_true', help='Generate and show plots.')
    parser.add_argument('--moho-depth', type=int, required=True, help='Moho depth in km.')
    parser.add_argument('--pml-thickness-idx', type=int, default=None, help='(Optional) Thickness of PML in km.')
    parser.add_argument('--original-nd-path', type=str, help='(Optional) Full path to the original reference .nd file.')
    args = parser.parse_args()

    if not args.core_sizes and not args.core_ratios:
        sys.exit(f"{Colors.RED}ERROR: Must specify --core-sizes or --core-ratios.{Colors.RESET}")
    if args.core_sizes and args.core_ratios:
        sys.exit(f"{Colors.RED}ERROR: Please specify either --core-sizes or --core-ratios, not both.{Colors.RESET}")

    use_ratios = bool(args.core_ratios)
    targets = args.core_ratios if use_ratios else args.core_sizes
    Target_name = args.target_name
    MODEL_DIRS = [os.path.join(args.model_dir, Target_name)]
    print(MODEL_DIRS)
    FIGURE_DIR = os.path.join(args.save_dir, Target_name, 'PNG')
    print(FIGURE_DIR)
    OUTPUT_DIR = os.path.join(args.save_dir, Target_name, 'Model')
    os.makedirs(FIGURE_DIR, exist_ok=True); os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary_plot_data = []

    print(f"{Colors.YELLOW}--- Initializing Model ---{Colors.RESET}")
    model_info = mean_density_from_model_files(MODEL_DIRS, False, FIGURE_DIR)
    print(model_info)
    if not model_info:
        sys.exit("Could not find or process the source model file. Exiting.")
    
    reference_mass = model_info[0]['total_mass']
    original_avg_density_gcm3 = model_info[0]['mean_density'] / 1000.0
    
    df_orig = model_info[0]['df']
    try:
        liquid_idx_orig = df_orig.index[df_orig['Vsv'] == 0].tolist()[0]
        original_core_density_gcm3 = df_orig.loc[liquid_idx_orig, 'density'] / 1000.0
    except IndexError:
        print(f"{Colors.RED}Could not find core in original model to determine core density.{Colors.RESET}")
        original_core_density_gcm3 = 0

    for target_value in targets:
        print(f"\n{Colors.YELLOW}################ PROCESSING TARGET: {Colors.BOLD}{target_value}{' (ratio)' if use_ratios else ' km'}{Colors.RESET} ################{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}=== Step 1: Modify Core Size ==={Colors.RESET}")
        df_step1, new_core_idx, calculated_ratio, pml_top_idx = modify_core_size(
            model_info[0]['model_path'], args.pml_thickness_idx, args.moho_depth, args.plot, FIGURE_DIR,
            new_core_size_km=target_value if not use_ratios else None,
            new_core_ratio=target_value if use_ratios else None
        )
        if df_step1 is None: continue
        
        actual_core_size_km = df_step1.radius.at[new_core_idx] / 1000
        step1_model_name = os.path.splitext(os.path.basename(model_info[0]['model_path']))[0] + f"_{round(calculated_ratio, 2)}x_{actual_core_size_km:.0f}km.model"
        step1_model_path = os.path.join(OUTPUT_DIR, step1_model_name)
        
        changed_models = [{'model_path': step1_model_path, 'df': df_step1, 'core_boundary_index': new_core_idx}]
        
        print(f"\n{Colors.YELLOW}=== Step 2: Redistribute Mass ==={Colors.RESET}")
        final_models_info = change_core_size_and_redistribute_mass(changed_models, reference_mass, args.moho_depth, args.plot, FIGURE_DIR, OUTPUT_DIR)

        print(f"\n{Colors.YELLOW}=== Step 3: Finalize Models (Add Discontinuities & Create .nd) ==={Colors.RESET}")
        final_model_path = final_models_info[0]['output_model']
        final_df = pd.read_csv(final_model_path, sep=' ', names=['radius', 'density', 'Vpv', 'Vsv', 'Q-kappa', 'Q-mu'])
        
        moho_index = (final_df['radius'] - (final_df.radius.max() - args.moho_depth * 1000)).abs().idxmin()
        core_index = new_core_idx
        
        final_df_with_discontinuities = create_discontinuities(final_df, moho_index, core_index)
        final_df_with_discontinuities.to_csv(final_model_path, sep=' ', index=False, header=False, float_format='%.4f')
        
        create_nd_file(final_df_with_discontinuities, OUTPUT_DIR, os.path.basename(final_model_path))
        
        avg_density_final, _, _ = calc_mean_density(final_df['radius'].values, final_df['density'].values)
        final_core_density = final_df.loc[core_index, 'density']
        
        summary_plot_data.append({
            'core_radius_km': actual_core_size_km,
            'mean_density_g_cm3': avg_density_final / 1000,
            'core_density_g_cm3': final_core_density / 1000
        })

        if args.plot:
            print(f"\n{Colors.YELLOW}=== Step 4: Generate Comparison Plots ==={Colors.RESET}")
            plot_final_comparison(model_info[0]['model_path'], final_model_path, FIGURE_DIR, calculated_ratio)
            
            # Load all models for comprehensive plot
            df_orig_model = read_nd_file(model_info[0]['model_path'].replace('.model', '.nd'))
            if df_orig_model is None: df_orig_model = df_orig
            
            df_final_nd = read_nd_file(final_model_path.replace('.model', '.nd'))
            df_orig_nd_ref = read_nd_file(args.original_nd_path, max_radius_km=df_orig.radius.max()/1000) if args.original_nd_path else None
            
            discontinuities = {
                'Moho': args.moho_depth,
                'PML Top': (df_orig.radius.max() - df_step1.radius.at[pml_top_idx])/1000,
                'CMB': actual_core_size_km
            }

    if args.plot:
        plot_summary_figure(summary_plot_data, FIGURE_DIR, Target_name, original_avg_density_gcm3, original_core_density_gcm3)