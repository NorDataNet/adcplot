from app.nc_transform import get_plottable_variables, get_plottable_data, get_nc_data, get_vp_data

from fastapi import HTTPException

"""[ License:
     This file is part of the NorDataNet adcplot repository (https://github.com/NorDataNet/adcplot).
     NorDataNet adcplot is licensed under GPL-3.0 (https://github.com/NorDataNet/adcplot/blob/master/LICENSE)]
"""


def get_variables(resource_url):
    try:
        plottable_variables = get_plottable_variables(resource_url)
        return plottable_variables
    except IOError:
        raise HTTPException(
            status_code=422, detail="URL To invalid or not supported NetCDF resource")

def get_data(resource_url, variable, axis):
    print(resource_url, variable, axis)
    if axis == 'y_axis':
        try:
            data = get_nc_data(resource_url, variable, resample=None)
        except IOError:
            raise HTTPException(status_code=422,
                                    detail="NetCDF resource is valid, but the routine failed to retrieve the timeSeries data")
    if axis == 'x_axis':
        try:
            data = get_vp_data(resource_url, variable, resample=None)
        except IOError:
            raise HTTPException(status_code=422,
                                detail="NetCDF resource is valid, but the routine failed to retrieve the timeSeries data")
    return data
