import numpy as np
import pandas as pd
import xarray as xr
from netCDF4 import Dataset

"""[ License:
     This file is part of the NorDataNet adcplot repository (https://github.com/NorDataNet/adcplot).
     NorDataNet adcplot is licensed under GPL-3.0 (https://github.com/NorDataNet/adcplot/blob/master/LICENSE)]
"""

def get_valid_vars(nc_url):
    var_list = []
    nc_fid = Dataset(nc_url, 'r')
    dimension = [i for i in nc_fid.dimensions]
    for i in list(nc_fid.variables.keys()): 
        try: 
            nc_fid.variables[i][:] 
            if i not in dimension:
                var_list.append(i)
        except RuntimeError:
            print('non valid variable:', i)
            pass 
    return var_list


# RESAMPLING
#
#
# Frequency
#
# 'D' Calendar day
# 'W' Weekly
# 'M' Month end
# 'Q' Quarter end
# 'A' Year end
# 'AS' Year start
# 'H' Hourly frequency
# 'T', min Minutely frequency
#
#
# Methods
#
# 'max' Maximum data value
# 'mean' Mean of values in time range
# 'median' Median of values in time range
# 'min' Minimum data value
# 'std' Standard deviation of values
# 'var' Variance of values



def get_plottable_variables(nc_url):
    print("#################### VAR CHECK 1 ######################")
    try:
        ds = xr.open_dataset(nc_url)
        num_dims = len(ds.dims)
        num_coords = len(ds.coords)
        valid_dims = [i for i in ds.dims if np.unique(ds[i]).shape[0] != 1]
        valid_coords = [i for i in ds.coords if np.unique(ds[i]).shape[0] != 1]
        var_list = [i for i in ds if len(ds[i].shape) == num_coords if list(ds[i].dims) == valid_coords]
        if len(var_list)<= 0:
            var_list = [i for i in ds if len(ds[i].values.shape) != 0 if list(ds[i].dims) == valid_coords]
        if len(var_list)<= 0:
            var_list = [i for i in ds if len(ds[i].shape) == num_coords if list(ds[i].dims) == valid_dims]       
        if all(len(ds[i].coords) == len(valid_coords) for i in var_list) and num_dims >= 2 and num_coords >=2 or len(valid_dims) != num_dims:
            axis_name = 'x_axis'
        else:
            axis_name = 'y_axis'
        print(var_list)
    except: 
        var_list = []
        axis_name = 'y_axis'
        nc_fid = Dataset(nc_url, 'r')
        print("#################### VAR CHECK 2 ######################")
        for i in list(nc_fid.variables.keys()): 
            try: 
                nc_fid.variables[i][0] 
                var_list.append(i)
            except RuntimeError:
                pass 
    var_dict = {axis_name: var_list}
    return var_dict


def get_plottable_data(nc_url, level):
    ds = xr.open_dataset(nc_url)
    variables = get_plottable_variables(nc_url)
    data = {i: {'dims': (level),
                'data': ds[i].values,
                'attrs': ds[i].attrs} for i in variables[list(variables.keys())[0]]}
    dataset = xr.Dataset.from_dict(data)
    dataset.attrs = ds.attrs
    dataset = dataset.assign_coords({level: ds[level]})
    return dataset



def get_nc_data(nc_url, nc_variable=None, resample=None):
    ds = xr.open_dataset(nc_url)
    valid_vars = get_valid_vars(nc_url)
    ds = ds[valid_vars]
    # TODO: the following is an hack to bypass bad/weird dataset
    if len(ds.coords) != len(ds.dims):
        valid_levels = [i for i in ds.dims if np.unique(ds[i]).shape[0] != 1]
        try:
            ds = get_plottable_data(nc_url, valid_levels[0])
        except ValueError:
            ds = get_plottable_data(nc_url, valid_levels[1])
        if len(valid_levels) >= 2:
            print('WORNING, skipping:', valid_levels[1:], 'dimensions')

    data = ds.to_dataframe()
    data.replace(9.96921e+36, np.NaN, inplace=True)
    if nc_variable:
        data = data[nc_variable]
    if resample:
        data = data.resample(resample).mean()
    data = pd.DataFrame(data)
    data.dataset_metadata = ''
    data.dataset_metadata = ds.attrs
    data.dataset_metadata['dimension'] = list(ds.dims)

    if nc_variable:
        data.variable_metadata = ''
        data.variable_metadata = ds[nc_variable].attrs
    else:
        data.variable_metadata = ''
        data.variable_metadata = {i: ds[i].attrs for i in ds}

    if 'featureType' not in data.dataset_metadata:
        if len(ds.dims) == 1 and 'time' in [i.lower() for i in list(ds.dims)]:
            data.dataset_metadata['featureType'] = 'timeSeries'
    return data


def get_vp_data(nc_url, nc_variable='sal', resample=None):
    profile = get_nc_data(nc_url, nc_variable=nc_variable)
    if 'featureType' not in profile.dataset_metadata:
        profile.dataset_metadata['featureType'] = ''
        profile.dataset_metadata['featureType'] = 'profile'
    if len(profile.index.names) == 2:
        vertical_level, time_level = profile.index.names
        df = profile.swaplevel()
        profile_dict = {str(v): df.loc[[df.index.get_level_values(0)[i]]].reset_index(level=time_level, drop=True)[
            nc_variable].values for i, v in enumerate(df.index.unique(level=time_level))}
        flat_df = pd.DataFrame.from_dict(profile_dict)
        flat_df.index = df.index.unique(level=vertical_level)
        flat_df.variable_metadata = ""
        flat_df.dataset_metadata = ""
        flat_df.variable_metadata = profile.variable_metadata
        flat_df.dataset_metadata = profile.dataset_metadata
        profile = flat_df
        if 'featureType' not in profile.dataset_metadata:
            profile.dataset_metadata['featureType'] = ''
            profile.dataset_metadata['featureType'] = 'timeSeriesProfile'
        # crazy dataset can have a nanosecond resolution and a step of
        # hours which doen't add up to something that make sense
        # here I resample the data column to a timestamp roundet at 1 second
        # profile.columns = pd.DatetimeIndex(profile.columns).round('1s')
        keys = profile.columns.values
        values = [str(i).rsplit('.')[0] for i in pd.DatetimeIndex(profile.columns).round('1s').values]
        dictionary = dict(zip(keys, values))
        profile.rename(columns=dictionary, inplace=True)
    return profile
