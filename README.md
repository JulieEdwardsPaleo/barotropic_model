# barotropic_model READ ME

## 1. Introduction
The purpose of this project is to create an atmosphere toy model to solve barotropic vorticity equations. It has several different settings which can be modified, such as using linear or nonlinear dynamics, different forcing scenarios, etc... I only coded out the linear dynamics and made an attempt at nonlinear dynamics and we only coded out topographic forcing but we could have added thermal forcing too. For the topogrpahic forcing you have the option to use 'real' or 'simple' topography, which will be described in more detail in **Section 3**. One main goal of this code is to see how well we can replicate the orographically-forced modeled streamfunction of more complex models. Even the first ever computer circulation model does a pretty amazing job at matching the real meridional mean stream function. Solving for vorticity is key to modelling Rossby waves, which are a key feature of the climate system. 

## 2. Model Dynamics
To spatially solve for vorticity, we're using spherical harmonics through the **windspharm** Python package. One disadvantage of spectral methods is the presence of Gibbs osciallations, which are apparent in the topography field. Then for time integration we're mostly using a forward scheme and switching to a centered scheme every 20 steps, as determined by the variable *forward* in **namelist.py**. To code up the equations we will be solving, first we start out with the absolute vorticity tendancy set to zero:
> <img src="readmeimages/Eqn1.gif" /> 
This equation is then expanded into:
> <img src="readmeimages/Eqn2.gif" /> 
Linearized, this equation is:
> <img src="readmeimages/Eqn3.gif" /> 
