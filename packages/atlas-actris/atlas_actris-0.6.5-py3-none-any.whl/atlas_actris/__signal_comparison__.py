#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 12:23:31 2024

@author: nikos
"""

import os, glob, warnings
from helper_functions import comparison_utils
import matplotlib
import numpy as np
from version import __version__
from visualizer.plotting.make_plot import make_filename_intercomparison
from visualizer.plotting.make_title import intercomparison
import pandas as pd
warnings.filterwarnings('ignore')

#------------------------------------------------------------------------------
# A) Inputs
#------------------------------------------------------------------------------

lidar_1 = "TONI"
lidar_2 = "POLIS"

#------------------------------------------------------------------------------
# 20251113
#------------------------------------------------------------------------------

# Path to the parent folder fs ATLAS 
filename_1 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/gar/TONI/203_246_1070_20251113_combined_20250412_022345/netcdf/preprocessor/gar_203_246_1070_20251113_210018_qck_ray_ATLAS_0.6.0_prepro.nc'
filename_2 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/mun/POLIS_9/9_9_9_20251113_20250412_010056/netcdf/preprocessor/mun_9_9_9_20251113_204513_qck_ray_ATLAS_0.6.0_prepro.nc'

# Path to the folder where the plots will be placed. If set to None
plot_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/plots/20251113_NR"
ascii_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/ascii/20251113_NR"

# Select time frame to process
slice_time = ['2100', '2147']

# Pair channels for comparison
channels_1 = ['0355xpar', '0355xppr', '0355xcat', '0355xcpt', '0387xvan', '0387xvpn', '0532xpar', '0532xppr', '0532xcat', '0532xcpt', '0607xvan', '0607xvpn', '1064xtax'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels
channels_2 = ['0355xpar', '0355xppr', '0355xcat', '0355xcpt', '0388xvan', '0388xvpn', '0532xpat', '0532xppt', '0532xcar', '0532xcpr', '0608xvan', '0608xvpn', '1064xpar'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels 

normalization_range = [4, 6] # in km. Set to None to skip normalization. All profiles will be normalized to their temporal mean

use_molecular = True # If set to True, the molecular attenuated backscatter profiles will also be plotted with the corresponding sig_1 and sig_2 and the two profiles will be normalized to with the molecular signal in the normalization range

x_range = [0,6] # Provide the xaxis limits (range or height) in km. Set to None to use automatic selection. Example: xlims = [0,20]

smoothing_window = None # in meters. Set to None to skip smoothing

smoothing_range = [0.05, 30] # in km. Set to None to smooth the whole profile. It will be applied only if the smoothing window is not None

#------------------------------------------------------------------------------
# 20251107
#------------------------------------------------------------------------------

## Path to the parent folder fs ATLAS 
# filename_1 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/gar/TONI/203_246_1070_20251107_combined_20250412_024709/netcdf/preprocessor/gar_203_246_1070_20251107_190627_qck_ray_ATLAS_0.6.0_prepro.nc'
# filename_2 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/mun/POLIS_9/9_9_9_20251107_20250412_004046/netcdf/preprocessor/mun_9_9_9_20251107_194722_qck_ray_ATLAS_0.6.0_prepro.nc'

## Path to the folder where the plots will be placed. If set to None
# plot_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/plots/20251107"
# ascii_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/ascii/20251107"

## Select time frame to process
# slice_time = ['1947', '2110']

## Pair channels for comparison
# channels_1 = ['0355xpar', '0355xppr', '0355xcat', '0355xcpt', '0387xvan', '0387xvpn', '0532xpar', '0532xppr', '0532xcat', '0532xcpt', '0607xvan', '0607xvpn', '1064xtax'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels
# channels_2 = ['0355xpar', '0355xppr', '0355xcat', '0355xcpt', '0388xvan', '0388xvpn', '0532xpat', '0532xppt', '0532xcar', '0532xcpr', '0608xvan', '0608xvpn', '1064xpar'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels 

#------------------------------------------------------------------------------
# 20251104
#------------------------------------------------------------------------------

## Path to the parent folder fs ATLAS 
# filename_1 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/gar/TONI/203_246_1070_20251104_combined_20250412_030832/netcdf/preprocessor/gar_203_246_1070_20251104_183955_qck_ray_ATLAS_0.6.0_prepro.nc'
# filename_2 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/mun/POLIS_1064/1064_1064_1064_20251104_20250312_224957/netcdf/preprocessor/mun_1064_1064_1064_20251104_182804_qck_ray_ATLAS_0.6.0_prepro.nc'

## Path to the folder where the plots will be placed. If set to None
# plot_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/plots/20251104"
# ascii_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/ascii/20251104"

## Select time frame to process
# slice_time = ['1840', '1938']

## Pair channels for comparison
# channels_1 = [ '1064xtax'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels
# channels_2 = ['1064xpar'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels

#------------------------------------------------------------------------------
# 20251105
#------------------------------------------------------------------------------

# # Path to the parent folder fs ATLAS 
# filename_1 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/gar/TONI/203_246_1070_20251105_combined_20250412_024406/netcdf/preprocessor/gar_203_246_1070_20251105_184946_qck_ray_ATLAS_0.6.0_prepro.nc'
# filename_2 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/mun/POLIS_1064/1064_1064_1064_20251105_20250312_225812/netcdf/preprocessor/mun_1064_1064_1064_20251105_190214_qck_ray_ATLAS_0.6.0_prepro.nc'

# # Path to the folder where the plots will be placed. If set to None
# plot_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/plots/20251105"
# ascii_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/ascii/20251105"

# # Select time frame to process
# slice_time = ['1902', '1940']

# # Pair channels for comparison
# channels_1 = [ '1064xtax'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels
# channels_2 = ['1064xpar'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels

#------------------------------------------------------------------------------
# 20251012 Day
#------------------------------------------------------------------------------

# # Path to the parent folder fs ATLAS 
# filename_1 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/gar/TONI/203_246_1071_20251012_combined_20250412_035946/netcdf/preprocessor/gar_203_246_1071_20251012_153251_qck_ray_ATLAS_0.6.0_prepro.nc'
# filename_2 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/mun/POLIS_9/9_9_9_20251012_20250412_001919/netcdf/preprocessor/mun_9_9_9_20251012_141000_qck_ray_ATLAS_0.6.0_prepro.nc'

# # Path to the folder where the plots will be placed. If set to None
# plot_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/plots/20251012"
# ascii_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/ascii/20251012"

# # Select time frame to process
# slice_time = ['1533', '1606']

# # Pair channels for comparison
# channels_1 = ['0355xpar', '0355xppr', '0355xcat', '0355xcpt', '0532xpar', '0532xppr', '0532xcat', '0532xcpt', '1064xtax'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels
# channels_2 = ['0355xpar', '0355xppr', '0355xcat', '0355xcpt', '0532xpat', '0532xppt', '0532xcar', '0532xcpr', '1064xpar'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels 

#------------------------------------------------------------------------------
# 20251012 Night FR
#------------------------------------------------------------------------------

# Path to the parent folder fs ATLAS 
filename_1 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/gar/TONI/203_246_1070_20251012_combined_20250412_035943/netcdf/preprocessor/gar_203_246_1070_20251012_180424_qck_ray_ATLAS_0.6.0_prepro.nc'
filename_2 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/mun/POLIS_1064/1064_1064_1064_20251012_20250312_222548/netcdf/preprocessor/mun_1064_1064_1064_20251012_170242_qck_ray_ATLAS_0.6.0_prepro.nc'

# Path to the folder where the plots will be placed. If set to None
plot_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/plots/20251012_Night_FR"
ascii_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/ascii/20251012_Night_FR"

# Select time frame to process
slice_time = ['1804', '1849']

# Pair channels for comparison
channels_1 = [ '1064xtax'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels
channels_2 = ['1064xpar'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels

normalization_range = [4, 6] # in km. Set to None to skip normalization. All profiles will be normalized to their temporal mean

use_molecular = True # If set to True, the molecular attenuated backscatter profiles will also be plotted with the corresponding sig_1 and sig_2 and the two profiles will be normalized to with the molecular signal in the normalization range

x_range = [0,30] # Provide the xaxis limits (range or height) in km. Set to None to use automatic selection. Example: xlims = [0,20]

smoothing_window = 500 # in meters. Set to None to skip smoothing

smoothing_range = [0.05, 30] # in km. Set to None to smooth the whole profile. It will be applied only if the smoothing window is not None

#------------------------------------------------------------------------------
# 20251012 Night NR
#------------------------------------------------------------------------------

# # Path to the parent folder fs ATLAS 
# filename_1 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/gar/TONI/203_246_1070_20251012_combined_20250412_035943/netcdf/preprocessor/gar_203_246_1070_20251012_180424_qck_ray_ATLAS_0.6.0_prepro.nc'
# filename_2 = '/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/mun/POLIS_1064/1064_1064_1064_20251012_20250312_222548/netcdf/preprocessor/mun_1064_1064_1064_20251012_170242_qck_ray_ATLAS_0.6.0_prepro.nc'

# # Path to the folder where the plots will be placed. If set to None
# plot_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/plots/20251012_Night_NR"
# ascii_folder = "/home/nikos/Big_Data/Intercomparison_Garmisch_2025/Analysis/comparison/ascii/20251012_Night_NR"

# # Select time frame to process
# slice_time = ['1804', '1849']

# # Pair channels for comparison
# channels_1 = [ '1064xtax'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels
# channels_2 = ['1064xpar'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels

# normalization_range = [4, 6] # in km. Set to None to skip normalization. All profiles will be normalized to their temporal mean

# use_molecular = True # If set to True, the molecular attenuated backscatter profiles will also be plotted with the corresponding sig_1 and sig_2 and the two profiles will be normalized to with the molecular signal in the normalization range

# x_range = [0,6] # Provide the xaxis limits (range or height) in km. Set to None to use automatic selection. Example: xlims = [0,20]

# smoothing_window = None # in meters. Set to None to skip smoothing

# smoothing_range = [0.05, 30] # in km. Set to None to smooth the whole profile. It will be applied only if the smoothing window is not None

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

timescale = None # Set to None to skip averaging. Use e.g. 10s for 10 second averages, 30min for 30 minute averages, or 1h for 1 hour averages. Use 'all' to average all files. Use None to apply no averaging

statistics_range = None # in km. Select a range to calculate statistics on signals to be displayed on the plots per channel. Statistics are calculated after averaging. Set to None to skip

gluing_range = None

calibration_factor = None

G = None

H = None

K = None
# mtype = 'ray' # set to either 'ray', 'drk', 'tlc', 'pcb' to plot the signals of the corresponding QA test 

colorscale = 'sequential' # select the colorscale ('sequential' or 'discrete') - If discrete is used 4 different colors will be applied iteratively for each measurement. If sequential is used, a colorscale of up to 256 colors will be used with the first/last measurement getting the first/last color repsectively. If there are more measurements than colors then the same colors might be used more than once for adjacent measurements   

custom_label = '' # provide a label to be added to the plot title. Use '' to skip

y_range_analog = None #[3.6, 4.1] # Add the default range in mv, applied to all analog channels. Example: y_range_analog = [0, 3]

y_range_photon = None # Add the default range in mv, applied to all analog channels.  Example: y_range_analog = [0, 3]


start_date = None


#------------------------------------------------------------------------------
# B) Calculations 
#------------------------------------------------------------------------------
# Path to the 'netcdf' folder that contains the files exported from ATLAS (more than 1 paths can be provided)
# netcdf_folder_1 = os.path.join(parent_folder_1, "netcdf")
# netcdf_folder_2 = os.path.join(parent_folder_2, "netcdf")

options = dict(plot_folder = plot_folder,
               timescale = timescale,
               smoothing_window = smoothing_window,
               smoothing_range = smoothing_range,
               normalization_range = normalization_range,
               statistics_range = statistics_range,
               # mtype = mtype,
               colorscale = colorscale,
               custom_label = custom_label,
               use_molecular = use_molecular,
               start_date = start_date,
               slice_time = slice_time)

comparison_utils.check_options(options)
comparison_utils.check_channel_lists(channels_1, channels_2)

#------------------------------------------------------------------------------
# C) Reading files 
#------------------------------------------------------------------------------
# fpath_list_1 = comparison_utils.get_fpaths(netcdf_folder = netcdf_folder_1, 
#                                            mtype = options['mtype'])

# fpath_list_2 = comparison_utils.get_fpaths(netcdf_folder = netcdf_folder_2, 
#                                            mtype = options['mtype'])
    
# for fpath in fpath_list_1:
sig_1, sig_err_1, atb_1, heights_1, metadata_1, stats_1 = \
    comparison_utils.get_prepro_signals(fpath = filename_1,
                                        options = options,
                                        channels = channels_1)
    
# for fpath in fpath_list_2:
sig_2, sig_err_2, atb_2, heights_2, metadata_2, stats_2 = \
    comparison_utils.get_prepro_signals(fpath = filename_2,
                                        options = options,
                                        channels = channels_2)

#------------------------------------------------------------------------------
# E) Plotting 
#------------------------------------------------------------------------------

# mask_heights_1 = (heights_1 >= normalization_range[0]) & (heights_1 <= normalization_range[1])
# mask_heights_2 = (heights_2 >= normalization_range[0]) & (heights_2 <= normalization_range[1])
# nrm_1 = sig_1.where(mask_heights_1).mean("bins")
# nrm_2 = sig_2.where(mask_heights_2).mean("bins")


if x_range == None:
    x_range = [0,20]

smoothing_options = {}

if smoothing_window != None:
    smoothing_options["smooth"] = True
    smoothing_options["smoothing_window"] = smoothing_window
else:
    smoothing_options["smooth"] = False
    smoothing_options["smoothing_window"] = smoothing_window
if smoothing_range != None:
    smoothing_options["smoothing_range"] = smoothing_range
else:
    smoothing_options["smoothing_range"] = x_range

smoothing_options["smooth_exponential"] = False

for ch_1, ch_2 in zip(channels_1,channels_2):
    
    # Make filename
    fname = make_filename_intercomparison(metadata_1 = metadata_1, 
                                          metadata_2 = metadata_2, 
                                          channel_1 = ch_1, 
                                          channel_2 = ch_2, 
                                          slice_time = slice_time,
                                          smoothing_window = smoothing_window,
                                          normalization_range = normalization_range,
                                          version = __version__)
    
    title = intercomparison(channel_1 = ch_1, 
                            channel_2 = ch_2, 
                            metadata_1 = metadata_1, 
                            metadata_2 = metadata_2, 
                            args = smoothing_options)

    X1 = heights_1.sel({"channel" : ch_1}).values
    X2 = heights_2.sel({"channel" : ch_2}).values

    Y1 = sig_1.sel({"channel" : ch_1}).values
    Y2 = sig_2.sel({"channel" : ch_2}).values

    Y1E = sig_err_1.sel({"channel" : ch_1}).values
    Y2E = sig_err_2.sel({"channel" : ch_2}).values
    
    Y1M = atb_1.sel({"channel" : ch_1}).values
    Y2M = atb_2.sel({"channel" : ch_2}).values
    
    delta_z_1 = X1[1] - X1[0]
    delta_z_2 = X2[1] - X2[0]
    
    B1 = sig_1.bins.values
    B2 = sig_2.bins.values
    
    if np.round(delta_z_1, 5) > np.round(delta_z_2, 5):
        B1_to_B2 = B1 * delta_z_1 / delta_z_2 + (X1[0] - X2[0]) / delta_z_2
        XC1 = X1
        YC1 = Y1
        YC1E = Y1E
        XC2 = heights_2.interp(bins=B1_to_B2, method="linear").sel({"channel" : ch_2}).values
        YC2 = sig_2.interp(bins=B1_to_B2, method="linear").sel({"channel" : ch_2}).values
        YC2E = sig_err_2.interp(bins=B1_to_B2, method="linear").sel({"channel" : ch_2}).values
        YCM = atb_2.interp(bins=B1_to_B2, method="linear").sel({"channel" : ch_2}).values
    else:
        B2_to_B1 = B2 * delta_z_2 / delta_z_1 + (X2[0] - X1[0]) / delta_z_1
        XC1 = heights_1.interp(bins=B2_to_B1, method="linear").sel({"channel" : ch_1}).values
        YC1 = sig_1.interp(bins=B2_to_B1, method="linear").sel({"channel" : ch_1}).values
        YC1E = sig_err_1.interp(bins=B2_to_B1, method="linear").sel({"channel" : ch_1}).values
        YCM = atb_1.interp(bins=B2_to_B1, method="linear").sel({"channel" : ch_1}).values
        XC2 = X2
        YC2 = Y2
        YC2E = Y2E
    
    
    # n_1 = nrm_1.sel({"channel" : ch_1}).values
    # n_2 = nrm_2.sel({"channel" : ch_2}).values
    
    min_range = max(np.min(XC1), np.min(XC2), x_range[0])
    max_range = min(np.max(XC1), np.max(XC2), x_range[1])

    mask_max_range_com = (XC1 >= min_range) & (XC1 <= max_range) & \
        (XC2 >= min_range) & (XC2 <= max_range)

    # Figure start
    png_file, export_pack = comparison_utils.plot_intercomparison(
        dir_out = plot_folder, 
        fname = f"{fname}.png", 
        title = title, 
        dpi_val = 150, 
        color_reduction = True, 
        use_lin = False, 
        norm_region = normalization_range,
        X1 = X1, 
        Y1 = Y1, 
        X2 = X2, 
        Y2 = Y2,
        Y1E = Y1E, 
        Y2E = Y2E,
        XC = XC1[mask_max_range_com], 
        YC1 = YC1[mask_max_range_com], 
        YC2 = YC2[mask_max_range_com],
        YC1E = YC1E[mask_max_range_com], 
        YC2E = YC2E[mask_max_range_com],
        YCM = YCM[mask_max_range_com],
        xlims = x_range, 
        x_axis_label = "Height [km]", 
        y_axis_label = "Normalized RC Signal", 
        label_1 = f"{lidar_1}_{ch_1}", 
        label_2 = f"{lidar_2}_{ch_2}"
        )
    
    ascii_file = os.path.join(ascii_folder, os.path.splitext(os.path.basename(png_file))[0] + ".csv")
    os.makedirs(os.path.dirname(ascii_file), exist_ok = True)
    pd.DataFrame(export_pack).to_csv(ascii_file, index=False)