import os
import sys
from datetime import timedelta
from glob import glob
import xarray as xr
from parcels import ParticleFile

def setup_output_file(particleset, parent_dir, release_start_day, polygon_id, wind_percentage):
    path = os.path.join(parent_dir, release_start_day)
    print(f"Path: {path}")
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{release_start_day}' created successfully")
    except OSError as error:
        print(f"Directory '{release_start_day}' can not be created")

    output_file = f"{path}/GBR1_H2p0_Coral_Release_{release_start_day}_Polygon_{polygon_id}_Wind_{wind_percentage}_percent_displacement_field.zarr"
    #folder_temp_out = "/home/por07g/Documents/Projects/GBR_modeling/GBR_oceanparcels/ocean_parcels_gbr/output/"
    #folder_temp_out = os.environ.get('MEMDIR') + '/out_temp'
    #pfile = ParticleFile(output_file, outputdt=timedelta(hours=1), tempwritedir=folder_temp_out)
    pfile = ParticleFile(output_file, particleset, outputdt=timedelta(hours=1))
    # Add metadata to pfile here...

    return output_file, pfile

def parse_args():
    polygon_id = int(sys.argv[1])
    release_start_day = sys.argv[2]
    release_start_hour = sys.argv[3]
    release_end_day = sys.argv[4]
    release_end_hour = sys.argv[5]
    num_particles_per_day = int(sys.argv[6])
    return polygon_id, release_start_day, release_start_hour, release_end_day, release_end_hour, num_particles_per_day

def setup_paths(data_path):
    files = sorted(glob(data_path+'gbr1_simple_*.nc'))
    mesh_mask = data_path + 'coordinates.nc'
    folderShape = data_path + "Shape_files/"
    originalfile = "gbr1_coral_1m_merged.shp"
    shapefile = folderShape + originalfile
    return files, mesh_mask, shapefile

def clean_output_file(output_file):
    with xr.open_dataset(output_file, decode_times=False) as ds:
        data = ds.load()
    new_nc = data.drop(['dU', 'dV', 'd2s'])
    new_nc.to_netcdf(path=output_file, mode='w')