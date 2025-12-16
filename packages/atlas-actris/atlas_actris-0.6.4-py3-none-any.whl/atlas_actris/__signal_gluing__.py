#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 12:23:31 2024

@author: nikos
"""

import os, glob, warnings
from helper_functions import gluing_utils
import matplotlib
import numpy as np
from version import __version__
from visualizer.plotting.make_plot import make_filename_intercomparison
from visualizer.plotting.make_title import intercomparison
from helper_functions.time_conversions import iso_to_datetimes, datetimes_to_iso
import pandas as pd
warnings.filterwarnings('ignore')

#------------------------------------------------------------------------------
# A) Inputs
#------------------------------------------------------------------------------
# Path to the parent folder fs ATLAS 
filename_1 = '/home/nikos/Big_Data/Intercomparison/Analysis/POLIS/9_9_9_20251107/netcdf/preprocessor/mun_9_9_9_20251107_194711_qck_ray_ATLAS_0.5.1_unofficial_prepro.nc'
filename_2 = '/home/nikos/Big_Data/Intercomparison/Analysis/POLIS/9_9_9_20251107/netcdf/preprocessor/mun_9_9_9_20251107_194711_qck_ray_ATLAS_0.5.1_unofficial_prepro.nc'
# parent_folder_2 = '/home/nikos/Big_Data/Intercomparison/Toni/203_246_823_20251007_2'
# parent_folder = os.path.join('/home/nikos/Nextcloud/ACTRIS-CARS-LMU/Instruments (POLIS-6, POLIS-1064)/POLIS-1064/Laser/Interspersion_measurements_APD_flex/',
#                              '20250219','50us_pretrigger')

# Path to the folder where the plots will be placed. If set to None
plot_folder = "/home/nikos/Big_Data/Intercomparison/Analysis/comparison/plots/20251107/near_range"
ascii_folder = "/home/nikos/Big_Data/Intercomparison/Analysis/comparison/plots/20251107/"

#drk_plastic_det_mount_all_det
#drk_plastic_det_mount_all_det_cross_cable_not_touching_frame
#drk_plastic_det_mount_one_det

timescale = None # Set to None to skip averaging. Use e.g. 10s for 10 second averages, 30min for 30 minute averages, or 1h for 1 hour averages. Use 'all' to average all files. Use None to apply no averaging

smoothing_window = None # in meters. Set to None to skip smoothing

smoothing_range = None # in km. Set to None to smooth the whole profile. It will be applied only if the smoothing window is not None

normalization_range = [1.5, 2.5] # in km. Set to None to skip normalization. All profiles will be normalized to their temporal mean

statistics_range = None # in km. Select a range to calculate statistics on signals to be displayed on the plots per channel. Statistics are calculated after averaging. Set to None to skip

gluing_range = None

calibration_factor = None

G = None

H = None

K = None
# mtype = 'ray' # set to either 'ray', 'drk', 'tlc', 'pcb' to plot the signals of the corresponding QA test 

lidar_1 = "TONI"
lidar_2 = "POLIS"

channels_1 = ['0355xpar', '0355xppr', '0355xcat', '0355xcpt', '0387xvan', '0387xvpn', '0532xpar', '0532xppr', '0532xcat', '0532xcpt', '0607xvan', '0607xvpn'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels

channels_2 = ['0355xpar', '0355xppr', '0355xcat', '0355xcpt', '0388xvan', '0388xvpn', '0532xpat', '0532xppt', '0532xcar', '0532xcpr', '0608xvan', '0608xvpn'] # use the ATLAS IDs to plot only specific channels, can be a list or scalar, set to None to plot all channels 


colorscale = 'sequential' # select the colorscale ('sequential' or 'discrete') - If discrete is used 4 different colors will be applied iteratively for each measurement. If sequential is used, a colorscale of up to 256 colors will be used with the first/last measurement getting the first/last color repsectively. If there are more measurements than colors then the same colors might be used more than once for adjacent measurements   

custom_label = '' # provide a label to be added to the plot title. Use '' to skip

x_range = [0,4] # Provide the xaxis limits (range or height) in km. Set to None to use automatic selection. Example: xlims = [0,20]

y_range_analog = None #[3.6, 4.1] # Add the default range in mv, applied to all analog channels. Example: y_range_analog = [0, 3]

y_range_photon = None # Add the default range in mv, applied to all analog channels.  Example: y_range_analog = [0, 3]

start_date = None

slice_time = None

#------------------------------------------------------------------------------
# B) Calculations 
#------------------------------------------------------------------------------
# Path to the 'netcdf' folder that contains the files exported from ATLAS (more than 1 paths can be provided)
# netcdf_folder_1 = os.path.join(parent_folder_1, "netcdf")
# netcdf_folder_2 = os.path.join(parent_folder_2, "netcdf")

options = dict(plot_folder = plot_folder,
               timescale = timescale,
               colorscale = colorscale,
               start_date = start_date,
               slice_time = slice_time)

gluing_utils.check_options(options)
gluing_utils.check_channel_lists(channels_1, channels_2)

#------------------------------------------------------------------------------
# C) Reading files 
#------------------------------------------------------------------------------
# fpath_list_1 = comparison_utils.get_fpaths(netcdf_folder = netcdf_folder_1, 
#                                            mtype = options['mtype'])

# fpath_list_2 = comparison_utils.get_fpaths(netcdf_folder = netcdf_folder_2, 
#                                            mtype = options['mtype'])
    
# for fpath in fpath_list_1:
sig_1, sig_err_1, atb_1, heights_1, metadata_1, stats_1 = \
    gluing_utils.get_prepro_signals(fpath = filename_1,
                                        options = options,
                                        channels = channels_1)
    
# for fpath in fpath_list_2:
sig_2, sig_err_2, atb_2, heights_2, metadata_2, stats_2 = \
    gluing_utils.get_prepro_signals(fpath = filename_2,
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
    pd.DataFrame(export_pack).to_csv(ascii_file, index=False)