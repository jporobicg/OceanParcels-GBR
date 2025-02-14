import sys
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the current directory to the Python path
sys.path.append(current_dir)

# If your custom modules are in a subdirectory, uncomment and modify the following line:
sys.path.append(os.path.join(current_dir, 'src'))

import numpy as np
import xarray as xr
from datetime import timedelta
from parcels import ErrorCode, AdvectionRK4

from inout import parse_args, setup_paths, setup_output_file, clean_output_file
from fielsets import setup_fieldset, setup_wind_field, setup_displacement_field, setup_shore_fields
from displacement import make_landmask, create_displacement_field, distance_to_shore, rotate_vector, set_displacement, displace
from seeding import seed_polygon_shape, release_times_per_day
from particles import create_particle_set, DeleteParticle, GBRVerticalMovement, ageing, FollowSurface, WindAdvectionRK4

# Constants and Paths
TIME_ZONE = 'GMT+10'
RELEASE_DEPTH = -1
WIND_PERCENTAGE = 3

# Local paths
LOCAL_DATA_PATH = '/home/por07g/Documents/Projects/GBR_modeling/GBR_oceanparcels/ocean_parcels_gbr/data/'
LOCAL_OUTPUT_PATH = '/home/por07g/Documents/Projects/GBR_modeling/GBR_oceanparcels/ocean_parcels_gbr/outputs/'

# HPC or alternative paths
HPC_HYDRO_PATH  = '/scratch3/por07g/Data/GBR1_Simple/'
HPC_DATA_PATH = '/datasets/work/oa-coconet/work/OceanParcels-GBR/data/'
HPC_OUTPUT_PATH = '/datasets/work/oa-coconet/work/OceanParcels-GBR/outputs/Coral/'

# Set the active paths here
DATA_PATH = HPC_DATA_PATH
OUTPUT_PATH = HPC_OUTPUT_PATH
HYDRO_PATH = HPC_HYDRO_PATH

def main():
    # Parse command-line arguments
    polygon_id, release_start_day, release_start_hour, release_end_day, release_end_hour, num_particles_per_day = parse_args()

    # Setup paths and files
    files, mesh_mask, shapefile = setup_paths(DATA_PATH, HYDRO_PATH)

    # Load grid data
    grid = xr.open_dataset(mesh_mask)
    grd_lat, grd_lon = grid['latitude'], grid['longitude']

    # Setup fieldset
    fieldset = setup_fieldset(mesh_mask, files)
    fieldset.add_constant('release_depth', RELEASE_DEPTH)
    fieldset = setup_wind_field(fieldset, mesh_mask, WIND_PERCENTAGE, files)

    # Setup displacement field
    landmask = make_landmask(files[0])
    u_displacement, v_displacement = create_displacement_field(landmask)
    u_displacement, v_displacement = rotate_vector(u_displacement, v_displacement, np.radians(28))
    d_2_s = distance_to_shore(landmask)
    fieldset = setup_displacement_field(fieldset, u_displacement, v_displacement)
    fieldset = setup_shore_fields(fieldset, landmask, d_2_s)

    # Setup release parameters
    time_origin = fieldset.U.grid.time_origin.time_origin
    release_times, _, num_particles = release_times_per_day(time_origin, num_particles_per_day,
                                                            release_start_hour, release_end_hour,
                                                            release_start_day, release_end_day, TIME_ZONE)

    # Create particle set
    x, y, z, area = seed_polygon_shape(shapefile, polygon_id, fieldset, num_particles, RELEASE_DEPTH)
    pset = create_particle_set(fieldset, x, y, z, release_times)

    # find grid cell number where particle is
    # this is critcal for dinding the location of the particles inside the model domain
    # the issue is that in stretched grid, the simple searching algorith has difficulty finding the correct grid cell
    for p in pset:
        yi, xi = find_particle_index(grd_lat, grd_lon, p.lat, p.lon)
        p.xi = np.array([xi], dtype=np.int32)
        p.yi = np.array([yi], dtype=np.int32)

    # Setup output file
    output_file, pfile = setup_output_file(pset, OUTPUT_PATH, release_start_day, polygon_id, WIND_PERCENTAGE)
    # Execute particle tracking
    kernels = pset.Kernel(displace) + pset.Kernel(AdvectionRK4) + pset.Kernel(WindAdvectionRK4) + \
              pset.Kernel(set_displacement) + pset.Kernel(ageing) + pset.Kernel(FollowSurface) + \
              pset.Kernel(GBRVerticalMovement)

    pset.execute(kernels, runtime=timedelta(days=35), dt=timedelta(minutes=30), output_file=pfile,
                 recovery={ErrorCode.ErrorOutOfBounds: DeleteParticle})
    ## check attributes for pfile

    pfile.close()
    # Convert the output to NetCDF
    ds = xr.open_zarr(output_file)
    print(output_file)
    nc_output_file = output_file.replace('.zarr', '.nc')
    print(nc_output_file)
    ds.to_netcdf(nc_output_file)
    ds.close()
    # remove the zarr file
    os.remove(output_file)

    # clean the output file
    clean_output_file(nc_output_file)
    print(f"NetCDF output saved to: {nc_output_file}")

if __name__ == "__main__":
    main()
