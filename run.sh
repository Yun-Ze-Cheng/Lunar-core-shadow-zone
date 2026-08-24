#!/bin/bash

# ====================================================================
#         MASTER SCRIPT FOR SEISMIC MODEL PARAMETER SWEEP
# ====================================================================
# This script orchestrates a parameter sweep by looping through
# multiple target models and a range of core sizes or ratios.
# ====================================================================

# --- Stop script on any error
set -e

# --- ANSI Color Codes for better output visibility ---
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# --- CONFIGURATION: SET YOUR PARAMETERS HERE ---

# Array of target models to process
TARGET_NAMES=(
    "Garcia-2019-M2_playground"
)

# ### NEW ### Choose ONE of the following: core sizes in km or core ratios.
# --- Option 1: Define core sizes in kilometers ---
# Generate a sequence from 200km to 700km with a 50km step
# CORE_SIZES_KM=($(seq 1401 100 2001))
#($(seq 1501 100 2001))
#($(seq 1300 100 2100))

# --- Option 2: Define core sizes as a ratio of the original ---
CORE_RATIOS=(0.8 1.4 2.0)
#(0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0)

# Set the thickness of the Partial Melting Layer (PML) above the core in km (grid points).
# If this variable is empty or commented out, the Python script will auto-detect the layer.
# PML_THICKNESS_IDX=150

# Set to "true" to generate plots, "false" to disable.
DO_PLOTS=true

# Base directory for the project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="${SCRIPT_DIR}/"
SAVE_DIR="${SCRIPT_DIR}/Output"
MODEL_DIR="${SCRIPT_DIR}/Model"
# Name of your main python processing script
MAIN_PYTHON_SCRIPT="process_core-shadow-zone.py"


# --- SCRIPT EXECUTION ---

echo -e "${YELLOW}============================================================${NC}"
echo -e "${YELLOW}Starting Seismic Model Parameter Sweep${NC}"
echo -e "${YELLOW}============================================================${NC}"
echo -e "${BOLD}Target Models:${NC} ${TARGET_NAMES[*]}"

# ### NEW ### Conditionally set arguments for core size or ratio
CORE_ARG=""
if [[ -v CORE_SIZES_KM ]]; then
    echo -e "${BOLD}Mode:${NC} Core Sizes (km)"
    echo -e "${BOLD}Values:${NC} ${CYAN}${CORE_SIZES_KM[*]}${NC}"
    CORE_ARG="--core-sizes ${CORE_SIZES_KM[*]}"
elif [[ -v CORE_RATIOS ]]; then
    echo -e "${BOLD}Mode:${NC} Core Ratios"
    echo -e "${BOLD}Values:${NC} ${CYAN}${CORE_RATIOS[*]}${NC}"
    CORE_ARG="--core-ratios ${CORE_RATIOS[*]}"
else
    echo -e "[${YELLOW}ERROR${NC}] You must define either 'CORE_SIZES_KM' or 'CORE_RATIOS' in the script."
    exit 1
fi

if [ -n "${PML_THICKNESS_IDX}" ]; then
    echo -e "${BOLD}PML Thickness (km):${NC} ${CYAN}${PML_THICKNESS_IDX}${NC} (Manual)"
else
    echo -e "${BOLD}PML Thickness (km):${NC} ${CYAN}Auto-detect${NC}"
fi
echo "------------------------------------------------------------"

# Argument for plotting
PLOT_ARG=""
if [ "${DO_PLOTS}" = "true" ]; then
    PLOT_ARG="--plot"
fi

# Conditionally build PML argument
PML_ARG=""
if [ -n "${PML_THICKNESS_IDX}" ]; then
    PML_ARG="--pml-thickness-idx ${PML_THICKNESS_IDX}"
fi

# Loop through each target model
for TARGET_NAME in "${TARGET_NAMES[@]}"; do
    
    echo ""
    echo -e "${YELLOW}************************************************************${NC}"
    echo -e "${YELLOW}Processing Target Model: ${BOLD}${TARGET_NAME}${NC}"
    echo -e "${YELLOW}************************************************************${NC}"

    # Set the default Moho depth based on the target name
    case "${TARGET_NAME}" in
        "Garcia-2019-M2_playground")   MOHO_DEPTH_KM=28 ;;
        *)
            echo -e "[${YELLOW}WARNING${NC}] No default Moho depth defined for '${TARGET_NAME}'. Skipping."
            continue
            ;;
    esac

    echo -e "${BOLD}Using Moho Depth:${NC} ${CYAN}${MOHO_DEPTH_KM} km${NC}"

    # Call the Python script with the parameters for this specific model
    python3 "${MAIN_PYTHON_SCRIPT}" \
        --target-name "${TARGET_NAME}" \
        --moho-depth ${MOHO_DEPTH_KM} \
        --base-dir "${BASE_DIR}" \
        --save-dir "${SAVE_DIR}" \
        --model-dir "${MODEL_DIR}" \
        ${CORE_ARG} \
        ${PML_ARG} \
        ${PLOT_ARG}

    echo "Finished processing for ${TARGET_NAME}."

done

echo -e "${YELLOW}============================================================${NC}"
echo -e "${YELLOW}Parameter sweep finished successfully.${NC}"
echo -e "${YELLOW}============================================================${NC}"
