#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:51:27 2020

@author: julieedwards
"""

import numpy as np
from xarray_IO import xarray_IO
import namelist as nl

class forcing:
    def __init__(self,latr,lonr):
        self.dtype=nl.dtype
        
        self.latr=latr
        self.lonr=lonr
        
        self.rlons,self.rlats=np.meshgrid(lonr,latr)
        
        self.latd=np.rad2deg(latr)
        self.lond=np.rad2deg(lonr)
        
        self.ny=len(self.latr)
        self.nx=len(self.lonr)
        
        ## Topo forcing
        self.topo = np.zeros((self.ny,self.nx), dtype=self.dtype)
        self.topo_clatr = np.deg2rad(nl.topo_clatd)
        self.topo_clonr = np.deg2rad(nl.topo_clond)
        self.topo_height = nl.topo_height
        
        
        ####
        
    def topography_simple(self):
        
        self.topo= np.cos(self.rlats) * \
            np.exp(-(self.rlons-self.topo_clonr)**2/.1)* \
            np.exp(-(self.rlats-self.topo_clatr)**2/.3)
            
        self.topo = self.topo_height * (self.topo / np.amax(self.topo))
        
        return self.topo
    
    def topography_real(self):
        self.topo=xarray_IO(nl.dfile_topo).get_values('topo')
        return self.topo