import math
import numpy as np
from parcels import ParticleSet
from parcels.tools.converters import GeographicPolar, Geographic
from displacement import GBRParticle_displacement



def DeleteParticle(particle, fieldset, time):
    print("Particle [%d] lost !! (%g %g %g %g)" % (particle.id, particle.lon, particle.lat, particle.depth, particle.time))
    particle.delete()


def GBRVerticalMovement(particle, fieldset, time):
    ## different depth for each of the phases
    if particle.age >= fieldset.first_change_depth:
        particle.depth = -10
    elif particle.age >= fieldset.second_change_depth:
        particle.depth = -15

def ageing(particle, fieldset, time):
     particle.age += math.fabs(particle.dt)

def FollowSurface(particle, fieldset, time) :
    if(particle.age < fieldset.first_change_depth):
        ## if the particle is at another depth than the initial depth of release,  it should comeback to the initial value
        if particle.depth < fieldset.release_depth:
            particle.depth = fieldset.release_depth
            ## checking velocity field at currrenth depth
            (u, v) = fieldset.UV[time, particle.depth, particle.lat, particle.lon]
            if math.fabs(u) < 1e-14 and math.fabs(v) < 1e-14 and particle.beached  == 0:
                new_depth = particle.depth
                while math.fabs(u) < 1e-14 and math.fabs(v) < 1e-14 and particle.beached  == 0:
                    new_depth = new_depth - 0.1
                    (u, v) = fieldset.UV[time, new_depth, particle.lat, particle.lon]
                    if(new_depth < -5):
                        particle.beached = 1
                particle.depth = new_depth
    else:
        (u, v) = fieldset.UV[time, particle.depth, particle.lat, particle.lon]
        if math.fabs(u) < 1e-14 and math.fabs(v) < 1e-14 and particle.beached  == 0:
            particle.beached = 1

def WindAdvectionRK4(particle, fieldset, time):
    """Advection of particles using fourth-order Runge-Kutta integration.
     Function needs to be converted to Kernel object before execution"""
    if particle.beached == 0 and particle.age < fieldset.first_change_depth:
        wp = fieldset.wind_percentage ## this need to be add to the fieldset
        if wp > 0:
            (wind_u1, wind_v1) = fieldset.UVwind[time, particle.depth, particle.lat, particle.lon]
            wind_u1 = wind_u1 * wp
            wind_v1 = wind_v1 * wp
            wind_lon1, wind_lat1 = (particle.lon + wind_u1*.5*particle.dt, particle.lat + wind_v1*.5*particle.dt)
            (wind_u2 ,wind_v2) = fieldset.UVwind[time + .5 * particle.dt, particle.depth, wind_lat1, wind_lon1]
            wind_u2 = wind_u2 * wp
            wind_v2 = wind_v2 * wp
            wind_lon2, wind_lat2 = (particle.lon + wind_u2*.5*particle.dt, particle.lat + wind_v2*.5*particle.dt)
            (wind_u3, wind_v3) = fieldset.UVwind[time + .5 * particle.dt, particle.depth, wind_lat2, wind_lon2]
            wind_u3 = wind_u3 * wp
            wind_v3 = wind_v3 * wp
            wind_lon3, wind_lat3 = (particle.lon + wind_u3*particle.dt, particle.lat + wind_v3*particle.dt)
            (wind_u4, wind_v4) = fieldset.UVwind[time + particle.dt, particle.depth, wind_lat3, wind_lon3]
            wind_u4 = wind_u4 * wp
            wind_v4 = wind_v4 * wp
            particle.lon += (wind_u1 + 2*wind_u2 + 2*wind_u3 + wind_u4) / 6. * particle.dt
            particle.lat += (wind_v1 + 2*wind_v2 + 2*wind_v3 + wind_v4) / 6. * particle.dt


def find_particle_index(latitudes, longitudes, part_lat, part_lon):
    """"This function looks for the indexes of each particle in the Xi-Yi
    In which grid cell each particle is located.
    Use this function after setting the particles and before executing the run"""
    diff_grid = np.abs(part_lat - latitudes) + np.abs(part_lon - longitudes)
    XiYi = np.where(diff_grid == diff_grid.min())
    indexes = [XiYi[0].item(), XiYi[1].item()]
    return(indexes)

def create_particle_set(fieldset, x, y, z, release_times):
    pset = ParticleSet.from_list(fieldset, pclass=GBRParticle_displacement,
                                 lon=x, lat=y, depth=z, time=release_times)
    return pset