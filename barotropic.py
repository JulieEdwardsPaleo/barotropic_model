#!/usr/bin/env python

import os
import sys
import numpy as np

from datetime import datetime, timedelta

from xarray_IO import xarray_IO
from spectral import spectral
from plot_tools import plot_tools
from forcing import forcing

import namelist as nl

#############################


class barotropic:
    """
    Barotropic vorticity model
    """

    def __init__(self):
        
        #height of atmosphere 10k meters
        #++initialize plot tools
        self.pp=plot_tools()
        # +++ Initialize time stepping +++ #
        self.nsteps = nl.nsteps
        self.dt = nl.dt
        self.nforward=nl.forward #forward step every # steps

#        self.start_time = datetime(2020, 10, 9, 0)
        self.start_time = datetime.now()

        # +++ Initialize model grid +++ #
        self.latd=xarray_IO(nl.dfile_um).get_values('lat')[::-1] #have to flip to start at north pole and go down but reads in at SP and goes up
        self.lond=xarray_IO(nl.dfile_um).get_values('lon')
        
        self.latr=np.deg2rad(self.latd) # degree to radians
        self.lonr=np.deg2rad(self.lond)
        
        self.ny=len(self.latd) # getting the number of steps
        self.nx=len(self.lond)
        

        # +++ Initialize spectral routines +++ #
        self.s=spectral(self.latd,self.lond)
        
        

        # +++ Initialize model fields +++ #
        self.vortp_tend = np.zeros((self.ny,self.nx))
        self.vort_tend = np.zeros((self.ny,self.nx))

        self.vortp_div = np.zeros((self.ny,self.nx)) # 2 dimensions
        self.vortp = np.zeros((self.ny,self.nx,3)) # 3 dimensions
        self.vort = np.zeros((self.ny,self.nx,3))
    #initialize v,u prime and f that you need to solve vorticity prime
        #f is coriolis parameter 
        self.vp = np.zeros((self.ny,self.nx))
        self.up = np.zeros((self.ny,self.nx))

        self.f = self.s.planetaryvorticity()
        _,self.dyf=self.s.gradient(self.f) #underscore is a way to disregard the x direction derivative of f, which is always zero
        
        self.um=xarray_IO(nl.dfile_um).get_values('u')[::-1,:] #read in zonal mean winds,flipped using [] part 
        self.vm=np.zeros((self.ny,self.nx))


    

        # +++ Initialize forcing +++ #
        self.forcing=forcing(self.latr,self.lonr)
        if nl.topo_case =='real': ##### If else statement to toggle between topo cases, defined in namelist
            self.topo=self.forcing.topography_real()[::-1,:] 

        else:
            self.topo=self.forcing.topography_simple() 
        self.dxtopo,self.dytopo=self.s.gradient(self.topo) #
        #calc dh/dx in forcing

        # +++ Model diagnostics +++ #
        # netCDF output
        self.output_freq = nl.output_freq
        self.output_dir = nl.output_dir
        # Create directory if not existing
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        # Plot figures
        self.plot_freq = nl.plot_freq
        self.plot_dir = nl.plot_dir
        # Create directory if not existing
        if not os.path.isdir(self.plot_dir):
            os.mkdir(self.plot_dir)

    #############################

    def integrate_linear_dynamics(self):
        """
        Linear dynamics
        """
        #initialize loop indices
        im=2
        ic=0
        ip=1


        for it in range(self.nsteps):

            # reset tendencies
            up,vp = self.s.vrtdiv2uv(self.vortp[:,:,ic], self.vortp_div) #pull out up and vp from vorticity field at current timestep
            self.vortp_tend *=0.
                
            self.topoF=-self.um*(self.f/nl.H)*self.dxtopo
 
            

            # +++ Dynamics +++ #
            
            self.vortm,_=self.s.uv2vrtdiv(self.um,self.vm) #get mean vort
            self.dxvortm,self.dyvortm=self.s.gradient(self.vortm) #meanvort/dx
            
            self.zetap,_=self.s.uv2vrtdiv(up,vp)
            self.dxzetap,self.dyzetap=self.s.gradient(self.vortm)
            
            self.vortp_tend=self.topoF-self.um*(self.dxzetap)-vp*self.dyvortm-vp*self.dyf      # solving for tendancy
            
            self.vortp_tend=self.vortp_tend - (1/nl.tau)*self.zetap # friction to multiply against perturbation field

            ######

            # +++ Timestep +++ #
            if it % self.nforward ==0:
            #Forward step
                self.vortp[:,:,ip]= self.vortp[:,:,ic] + self.vortp_tend*self.dt

            #Centered (leapfrog) step - setting to centered scheme every few steps
            else:
                self.vortp[:,:,ip]= self.vortp[:,:,im] + self.vortp_tend*2.*self.dt

            # update time-pointers (cyclic permutation)
            itmp = im
            im = ic
            ic = ip
            ip = itmp

            ######
            psip,velp=self.s.uv2sfvp(up,vp)
            psim,velm=self.s.uv2sfvp(self.um,self.vm)
            

            # +++ Diagnostics +++ #
            if nl.movie==True:
                self.pp3=plot_tools() # makig a new pp also works here
                self.pp3.plot_movie(self.latd, self.lond, psip, self.topo, field='psi', diff=True)
            else:
                pass

            # Current hour and integration time
            chr = (it+1) * self.dt / 3600.
            itime = self.start_time + timedelta(hours=chr)

            # Plot figures

            if self.plot_freq != 0 and chr % self.plot_freq == 0:
                print('-- Step {}: plotting fields'.format(it))
                self.pp2=plot_tools() #resetting plotting functionality

                self.pp2.plot_field(self.latd, self.lond,
                   var_cf=psip, field_cf='psi', diff_cf=True, var_cr=None, field_cr=None, diff_cr=False,
                   title='psip{}'.format(it),save=True, ofile='./figures/psip{}'.format(it))  # figure names based on the time step
            ###

            # Save output data
            if self.output_freq != 0 and chr % self.output_freq == 0:
                print('-- Step {}: saving data'.format(it))
                dsout = xarray_IO() 
    
                dsout.create_dimension(self.latd, 'lat',
                                        units='degrees_north',
                                        long_name='latitude')
                dsout.create_dimension(self.lond, 'lon',
                                        units='degrees_east',
                                        long_name='longitude')
          
    
                dsout.create_variable(psip, 'psip', dims=('lat','lon'),
                                      units='m2/s', # streamfunction unit
                                      long_name='stream function')
                
                ofile = './output/psip{}.nc'.format(it) #nc file name based on time step, to be joined later
                dsout.write_netcdf(ofile)



########## call save output codes from xarray_IO, create variables and attributes for u and v wind fields and stream function (psi), vorticity, forcing (thermal and topo)
##########

        # self.pp.quick_plot(self.latd, self.lond, psip) #diagnostic check plot
        # sys.exit()
    #############################

    def integrate_nonlinear_dynamics(self):
        """
        Nonlinear dynamics
        """
        #initialize loop indices
        im=2
        ic=0
        ip=1
        for it in range(self.nsteps):

            up,vp = self.s.vrtdiv2uv(self.vortp[:,:,ic], self.vortp_div) #pull out up and vp from vorticity field at current timestep
            self.vort_tend *=0.
                
            self.topoF=-self.um*(self.f/nl.H)*self.dxtopo    
            u=self.um+up 
            v=vp



            # +++ Dynamics +++ #

            self.zeta,_=self.s.uv2vrtdiv(u,v)
            self.dxvort,self.dyvort=self.s.gradient(self.zeta) 
            
            self.vort_tend=self.topoF-u*(self.dxvort)-v*self.dyvort-v*self.dyf           


            ######

            # +++ Timestep +++ #
            if it % self.nforward ==0:
            #Forward step
                self.vort[:,:,ip]= self.vort[:,:,ic] + self.vort_tend*self.dt

            #Centered (leapfrog) step
            else:
                self.vort[:,:,ip]= self.vort[:,:,im] + self.vort_tend*2.*self.dt

            # update time-pointers (cyclic permutation)
            itmp = im
            im = ic
            ic = ip
            ip = itmp


            ######
            psi,vel=self.s.uv2sfvp(u,v)
           # psim,velm=self.s.uv2sfvp(self.um,self.vm)
            
            # +++ Diagnostics +++ #

            # Current hour and integration time
            chr = (it+1) * self.dt / 3600.
            itime = self.start_time + timedelta(hours=chr)

            # Plot figures
            if self.plot_freq != 0 and chr % self.plot_freq == 0:
                print('-- Step {}: plotting fields'.format(it))

            ###

            # Save output data
            if self.output_freq != 0 and chr % self.output_freq == 0:
                print('-- Step {}: saving data'.format(it))

            ###

            self.pp.plot_movie(self.X,self.Y,psi,self.topo)

#############################

if __name__ == '__main__':
    pass

#############################
### +++ END OF SCRIPT +++ ###
#############################
