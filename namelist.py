#!/usr/bin/env python

"""
Namelist for barotropic model
"""

import os
import numpy as np
import forcing 

##############
###############


# Time stepping
nsteps = 1000       # Number of time steps to integrate
dt = 20.*60.       # Timestep (seconds)
nforward = 20      # Forward step every # timesteps

tau=5.*86400. #for friction : 5 days

# Spectral operators
trunc = None # Truncation (if None, defaults to # latitudes)
realm='s'
rsphere = 6.3712e6  # Planetary radius
legfunc = 'stored'  # Legendre functions

#input files
dfile_um=os.getcwd()+'/input_data/meanzonalu.nc' ## path should work and not have to be changed 
dfile_topo=os.getcwd()+'/input_data/world_topography.T42.nc'

# real or simple topo case######
topo_case= 'real' #real or simple


# I/O
output_dir = os.path.join(os.getcwd(), 'output')  # Output directory
output_freq = 6     # Freq. of output in hours (0 = no data saved)

plot_dir = os.path.join(os.getcwd(), 'figures')   # Figure directory
plot_freq = 6       # Freq. of output figures in hours (0 = no plots)
movie=True #plot movie True or False?

# ideal topo forcing
topo_clatd=45. #center lat (degrees)
topo_clond = 80. # center lon (degrees), changed to better mimic the location of the Himalayas
topo_height =2500. #topo height (m) little h in topo forcing eqn



H=10.e3# scale height of atmosphere
omega = 7.292e-05  # unit: s-1
        # Gravitational acceleration
g = 9.8

# misc
dtype = np.float32 #precision
