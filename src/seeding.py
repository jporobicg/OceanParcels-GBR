import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import sys

def seed_polygon_shape(shapefile_name, release_site_id, fieldset, num_particles, release_depth):
    
    try :
        print('Using shapefile!!!! ' + shapefile_name)
        data_shape = gpd.read_file(shapefile_name)
        value_index = list(data_shape.loc[data_shape['FID'] == release_site_id].index)
        value_index = int("".join(map(str, value_index)))
        area = data_shape['area'][value_index]
        polygon = data_shape['geometry'][value_index]
        base_polygon = gpd.GeoSeries([polygon])
        num_sites = data_shape.shape[0]
        print('Number of sites : ', num_sites)
    except Exception:
        print("Error while attempting to load the shapefile " + shapefile_name)
        sys.exit()
    bounds = polygon.bounds
    z = np.ones((num_particles, 1)) * release_depth
    min_lon = bounds[0]
    max_lon = bounds[2]
    del_lon = max_lon - min_lon
    min_lat = bounds[1]
    max_lat = bounds[3]
    del_lat = max_lat - min_lat
    num_in_polygon = 0
    num_attempts = 0
    x_in = []
    y_in = []
    fieldset.check_complete()
    fieldset.computeTimeChunk(0, 1)
    while num_in_polygon < num_particles:
        xc = min_lon + np.random.random(num_particles) * del_lon
        yc = min_lat + np.random.random(num_particles) * del_lat
        pts = gpd.GeoSeries([Point(x, y) for x, y in zip(xc, yc)])
        # Are these points inside the polygon?
        p = base_polygon.apply(lambda x: pts.within(x))
        m = p.to_numpy().reshape(num_particles, 1)
        valid_indices = np.argwhere(m == True)
        valid_indices = valid_indices[:, 0]

        if len(valid_indices) > 0:
            xc = xc[valid_indices]
            yc = yc[valid_indices]

            for index in range(0, len(valid_indices)):
               # Be sure that we are seeding in water
                # try:
                #     (u, v) = fieldset.UV[0, release_depth, yc[index], xc[index]]
                # except FieldSamplingError:
                #     print('FieldSamplingError')
                #     continue
                x_in.append(xc[index])
                y_in.append(yc[index])
                num_in_polygon = len(x_in)
                if num_in_polygon >= num_particles:
                    break
        num_attempts = num_attempts + 1
        if num_attempts > 2 and num_in_polygon == 0:
            break
        if num_attempts > 10:
            break
    if num_attempts > 10:
        print('\nfailed to find valid points for ' + str(release_site_id))
        return
    # have we ended up with too many particles?
    if num_in_polygon > num_particles:
        x_in = x_in[0:num_particles]
        y_in = y_in[0:num_particles]
        num_in_polygon = len(x_in)
    if num_in_polygon == num_particles:
        print('Sucessfully seeded particles\n')
        print('num_attempts = ' + str(num_attempts))
    else:
        print('\nfailed to find valid points for ' + str(release_site_id))
        print('found ' + str(num_in_polygon) + ' locations')
    return(x_in, y_in, z, area)

def release_times_per_day(time_origin, num_particles_per_day, release_start_hour, release_end_hour, release_start_day, release_end_day, time_zone):
## conversion
    simulation_start_day = np.datetime64(release_start_day,'D')
    simulation_end_day   = np.datetime64(release_end_day,'D')
    new_time_origin      = np.datetime64(time_origin)
    release_times=[]
    number_days = (1 + simulation_end_day-simulation_start_day).astype(int)
    for day in range(0, number_days):
        release_start=np.datetime64(release_start_day + release_start_hour) + np.timedelta64(day,'D')
        release_end=np.datetime64(release_start_day +  release_end_hour) + np.timedelta64(day,'D')
        if time_zone == 'GMT+10' :
            release_start= release_start - np.timedelta64(10,'h')
            release_end = release_end - np.timedelta64(10,'h')
        diff = release_end - release_start
        offset = (release_start - new_time_origin)
        offset = np.timedelta64(offset, 's') / np.timedelta64(1, 's')
        q = int(np.timedelta64(diff, 's') / np.timedelta64(1, 's'))
        p = np.random.randint(0, q, num_particles_per_day)
        p = (np.round(p/3600) * 3600).astype(int)
        release_times=np.append(release_times, offset + p)
    num_particles = num_particles_per_day * number_days
    return release_times, p, num_particles

