from parcels import FieldSet, Field, VectorField
from parcels.tools.converters import GeographicPolar, Geographic
import numpy as np

def setup_fieldset(mesh_mask, files):
    filenames = {'U': {'lon': mesh_mask, 'lat': mesh_mask, 'depth': files[0], 'data': files},
                 'V': {'lon': mesh_mask, 'lat': mesh_mask, 'depth': files[0], 'data': files}}
    variables = {'U': 'u', 'V': 'v'}
    dimensions = {'U': {'lon': 'longitude', 'lat': 'latitude', 'depth': 'zc', 'time': 'time'},
                  'V': {'lon': 'longitude', 'lat': 'latitude', 'depth': 'zc', 'time': 'time'}}
    fieldset = FieldSet.from_netcdf(filenames, variables, dimensions, allow_time_extrapolation=True, chunksize='auto')
    return fieldset

def setup_wind_field(fieldset, mesh_mask, wind_effect,files):
    wind_filenames = {'lon': mesh_mask, 'lat': mesh_mask, 'data': files}
    wind_dimensions = {'lon': 'longitude', 'lat': 'latitude', 'time': 'time'}
    Uwind_field = Field.from_netcdf(wind_filenames, ('Uwind', 'wspeed_u'),
                                    wind_dimensions, fieldtype='U',
                                    allow_time_extrapolation=True,
                                    transpose=False, deferred_load=True)
    Vwind_field = Field.from_netcdf(wind_filenames, ('Vwind', 'wspeed_v'),
                                    wind_dimensions, fieldtype='V',
                                    allow_time_extrapolation=True,
                                    transpose=False, deferred_load=True)
    fieldset.add_field(Uwind_field)
    fieldset.add_field(Vwind_field)
    wind_field = VectorField('UVwind', Uwind_field, Vwind_field)
    fieldset.add_vector_field(wind_field)
    fieldset.add_constant('wind_percentage', wind_effect/100.0)
    fieldset.add_constant('first_change_depth', .5 * 86400)
    fieldset.add_constant('second_change_depth', 2.5 * 86400)
    return fieldset

def setup_displacement_field(fieldset, u_displacement, v_displacement):
    fieldset.add_field(Field('dispU', data=u_displacement,
                             lon=fieldset.U.grid.lon, lat=fieldset.U.grid.lat,
                             mesh='spherical'))
    fieldset.add_field(Field('dispV', data=v_displacement,
                             lon=fieldset.U.grid.lon, lat=fieldset.U.grid.lat,
                             mesh='spherical'))
    fieldset.dispU.units = GeographicPolar()
    fieldset.dispV.units = Geographic()
    return fieldset

def setup_shore_fields(fieldset, landmask, d_2_s):
    fieldset.add_field(Field('landmask', landmask,
                             lon=fieldset.U.grid.lon, lat=fieldset.U.grid.lat,
                             mesh='spherical'))
    fieldset.add_field(Field('distance2shore', d_2_s,
                             lon=fieldset.U.grid.lon, lat=fieldset.U.grid.lat,
                             mesh='spherical'))
    return fieldset
