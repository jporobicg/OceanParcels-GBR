from parcels import JITParticle, Variable, Field, FieldSet
from parcels.tools.converters import GeographicPolar, Geographic
import numpy as np
from netCDF4 import Dataset
import xarray as xr
import math
from datetime import timedelta
import sys
import os
from glob import glob
import geopandas as gpd
from shapely.geometry import Point

## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##
## ~            Displacement functions        ~ ##
## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##
def make_landmask(fielddata):
    """Returns landmask where land = 1 and ocean = 0
    fielddata is a netcdf file.
    """
    datafile = Dataset(fielddata)
    landmask = datafile.variables['u'][1, 39]
    landmask[landmask > 10] = np.nan
    landmask = np.ma.masked_invalid(landmask)
    landmask = landmask.mask.astype('int')
    return landmask

def moving_box_avg(fielddata):
    New_fielddata = np.full([(fielddata.shape[0]-1), (fielddata.shape[1]-1)], None)
    for rows in range(1, fielddata.shape[0]):
        for cols in range(1, fielddata.shape[1]):
            New_fielddata[rows-1, cols-1] = (fielddata[rows-1, cols-1] + fielddata[rows-1, cols] +
                                         fielddata[rows, cols] + fielddata[rows, cols-1]) * 0.25
    return New_fielddata

def get_coastal_nodes(landmask):
    """Function that detects the coastal nodes, i.e. the ocean nodes directly
    next to land. Computes the Laplacian of landmask.

    - landmask: the land mask built using `make_landmask`, where land cell = 1
                and ocean cell = 0.

    Output: 2D array array containing the coastal nodes, the coastal nodes are
            equal to one, and the rest is zero.
    """
    mask_lap = np.roll(landmask, -1, axis=0) + np.roll(landmask, 1, axis=0)
    mask_lap += np.roll(landmask, -1, axis=1) + np.roll(landmask, 1, axis=1)
    mask_lap -= 4*landmask
    coastal = np.ma.masked_array(landmask, mask_lap > 0)
    coastal = coastal.mask.astype('int')

    return coastal

def get_shore_nodes(landmask):
    """Function that detects the shore nodes, i.e. the land nodes directly
    next to the ocean. Computes the Laplacian of landmask.

    - landmask: the land mask built using `make_landmask`, where land cell = 1
                and ocean cell = 0.

    Output: 2D array array containing the shore nodes, the shore nodes are
            equal to one, and the rest is zero.
    """
    mask_lap = np.roll(landmask, -1, axis=0) + np.roll(landmask, 1, axis=0)
    mask_lap += np.roll(landmask, -1, axis=1) + np.roll(landmask, 1, axis=1)
    mask_lap -= 4*landmask
    shore = np.ma.masked_array(landmask, mask_lap < 0)
    shore = shore.mask.astype('int')

    return shore


def get_coastal_nodes_diagonal(landmask):
    """Function that detects the coastal nodes, i.e. the ocean nodes where
    one of the 8 nearest nodes is land. Computes the Laplacian of landmask
    and the Laplacian of the 45 degree rotated landmask.

    - landmask: the land mask built using `make_landmask`, where land cell = 1
                and ocean cell = 0.

    Output: 2D array array containing the coastal nodes, the coastal nodes are
            equal to one, and the rest is zero.
    """
    mask_lap = np.roll(landmask, -1, axis=0) + np.roll(landmask, 1, axis=0)
    mask_lap += np.roll(landmask, -1, axis=1) + np.roll(landmask, 1, axis=1)
    mask_lap += np.roll(landmask, (-1,1), axis=(0,1)) + np.roll(landmask, (1, 1), axis=(0,1))
    mask_lap += np.roll(landmask, (-1,-1), axis=(0,1)) + np.roll(landmask, (1, -1), axis=(0,1))
    mask_lap -= 8*landmask
    coastal = np.ma.masked_array(landmask, mask_lap > 0)
    coastal = coastal.mask.astype('int')
    return coastal

def get_shore_nodes_diagonal(landmask):
    """Function that detects the shore nodes, i.e. the land nodes where
    one of the 8 nearest nodes is ocean. Computes the Laplacian of landmask
    and the Laplacian of the 45 degree rotated landmask.
    - landmask: the land mask built using `make_landmask`, where land cell = 1
                and ocean cell = 0.
    Output: 2D array array containing the shore nodes, the shore nodes are
            equal to one, and the rest is zero.
    """
    mask_lap = np.roll(landmask, -1, axis=0) + np.roll(landmask, 1, axis=0)
    mask_lap += np.roll(landmask, -1, axis=1) + np.roll(landmask, 1, axis=1)
    mask_lap += np.roll(landmask, (-1,1), axis=(0,1)) + np.roll(landmask, (1, 1), axis=(0,1))
    mask_lap += np.roll(landmask, (-1,-1), axis=(0,1)) + np.roll(landmask, (1, -1), axis=(0,1))
    mask_lap -= 8*landmask
    shore = np.ma.masked_array(landmask, mask_lap < 0)
    shore = shore.mask.astype('int')
    return shore

def create_displacement_field(landmask, double_cell=False):
    """Function that creates a displacement field 1 m/s away from the shore.
    - landmask: the land mask dUilt using `make_landmask`.
    - double_cell: Boolean for determining if you want a double cell.
      Default set to False.
    Output: two 2D arrays, one for each camponent of the velocity.
    """
    shore = get_shore_nodes(landmask)
    shore_d = get_shore_nodes_diagonal(landmask) # bordering ocean directly and diagonally
    shore_c = shore_d - shore                    # corner nodes that only border ocean diagonally
    Ly = np.roll(landmask, -1, axis=0) - np.roll(landmask, 1, axis=0) # Simple derivative
    Lx = np.roll(landmask, -1, axis=1) - np.roll(landmask, 1, axis=1)
    Ly_c = np.roll(landmask, -1, axis=0) - np.roll(landmask, 1, axis=0)
    Ly_c += np.roll(landmask, (-1,-1), axis=(0,1)) + np.roll(landmask, (-1,1), axis=(0,1)) # Include y-component of diagonal neighbours
    Ly_c += - np.roll(landmask, (1,-1), axis=(0,1)) - np.roll(landmask, (1,1), axis=(0,1))
    Lx_c = np.roll(landmask, -1, axis=1) - np.roll(landmask, 1, axis=1)
    Lx_c += np.roll(landmask, (-1,-1), axis=(1,0)) + np.roll(landmask, (-1,1), axis=(1,0)) # Include x-component of diagonal neighbours
    Lx_c += - np.roll(landmask, (1,-1), axis=(1,0)) - np.roll(landmask, (1,1), axis=(1,0))
    v_x = -Lx*(shore)
    v_y = -Ly*(shore)
    v_x_c = -Lx_c*(shore_c)
    v_y_c = -Ly_c*(shore_c)
    v_x = v_x + v_x_c
    v_y = v_y + v_y_c
    magnitude = np.sqrt(v_y**2 + v_x**2)
    # the coastal nodes between land create a problem. Magnitude there is zero
    # I force it to be 1 to avoid problems when normalizing.
    ny, nx = np.where(magnitude == 0)
    magnitude[ny, nx] = 1
    v_x = v_x/magnitude
    v_y = v_y/magnitude
    return v_x, v_y

def rotate_vector(v_x, v_y, rotation_angle):
    """
    Rotate vectors in 2D arrays by a given angle in radians.    
    Parameters:
    v_x, v_y: 2D numpy arrays of shape (2000, 500) representing x and y components of vectors
    rotation_angle: angle in radians to rotate the vectors    
    Returns:
    Tuple of two 2D numpy arrays representing rotated x and y components
    """
    cos_theta = np.cos(rotation_angle)
    sin_theta = np.sin(rotation_angle)
    
    v_x_rotated = v_x * cos_theta - v_y * sin_theta
    v_y_rotated = v_x * sin_theta + v_y * cos_theta
    
    return v_x_rotated, v_y_rotated

def distance_to_shore(landmask, dx=1):
    """Function that computes the distance to the shore. It is based in the
    the `get_coastal_nodes` algorithm.
    - landmask: the land mask dUilt using `make_landmask` function.
    - dx: the grid cell dimension. This is a crude approxsimation of the real
    distance (be careful).
    Output: 2D array containing the distances from shore.
    """
    ci = get_coastal_nodes(landmask) # direct neighbours
    dist = ci*dx                     # 1 dx away
    ci_d = get_coastal_nodes_diagonal(landmask) # diagonal neighbours
    dist_d = (ci_d - ci)*np.sqrt(2*dx**2)       # sqrt(2) dx away
    return dist+dist_d


class GBRParticle_displacement(JITParticle):
    age = Variable('age', dtype=np.float32, initial=0.)
    dU = Variable('dU')
    dV = Variable('dV')
    d2s = Variable('d2s', initial=1e3)
    beached = Variable('beached', dtype=np.int32, initial=0.)


def set_displacement(particle, fieldset, time):
    particle.d2s = fieldset.distance2shore[time, particle.depth,
                               particle.lat, particle.lon]
    if  particle.d2s < 0.5:
        dispUab = fieldset.dispU[time, particle.depth, particle.lat,
                               particle.lon]
        dispVab = fieldset.dispV[time, particle.depth, particle.lat,
                               particle.lon]
        particle.dU = dispUab
        particle.dV = dispVab
    else:
        particle.dU = 0.
        particle.dV = 0.

def displace(particle, fieldset, time):
    if  particle.d2s < 0.5:
        particle.lon += particle.dU*particle.dt
        particle.lat += particle.dV*particle.dt
