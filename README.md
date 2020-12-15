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
Since we want to solve for the vorticity tendancy, we want to set everything to the right side of the equation:
> <img src="readmeimages/Eqn4.gif" /> 

## 3. Code Documentation
The main script where we're solving the equations from **Section 2** is **barotropic.py**. This script initializes all the variables we need and the linear dynamics (nonlinear dyamics pending). This script also includes plot and output saving and diagnostics. **forcing.py** is where we set up the topographic forcing. The 'simple' topography (*topography_simple*) is created by a gaussian function. The 'real' topography (*topography_real*) is read in from a file using a function from **xarray_IO.py**. **xarray_OI.py** contains functions fro reading in netCDFs, creating variables and dimenstions for output netCDFs, and eventually writing the netCDF output. The **namelist.py** script should be the only script you should need to edit. The main veriables you should be changing in **namelist.py** are *topo_case* depending out which topography you want to use (real or simple), the *plot_freq* and *output_freq* variables for how often you want plot and data output. You could also change the location of the 'simple' topography with *topo_clatd* and *topo_clond*. *plot_tools.py* includes plotting functions used in the **barotropic.py** script. **spectral.py** includes the functions needed for using spherical harmonics and is where we calculate the coriolis effect. Finally, **runscript.py** is what you want to use to actually run the model. This is also where you decide if you want to run the linear or nonlinear dynamics version. Each script bascially has a singular class in it, that has the same name as the script. We're using object oriented programming so each classe structures data into objects, which can have variables and functions in them. A benefit of using classes is that we can have a singular class but run the same functions over different instances, so it avoids duplication, keeps the code cleaner, and makes it easier to change inputs in the namelist. We can initialize one class within another class, for example when we initialize the plot_tools class within the barotropic class, now we have access to the structure and functions within plot_tools. 

**Bugs and unwanted features:** We had to initialize the plot_tools class 3 different times in the barotropic class so that the plots showed up and saved correctly. We also had to be careful about flipping the latitude field of the input zonal wind field and the topography field. The latitude direction is important for calculations in spherical harmonics code.

## 4. Code Walkthrough
To run the code as is, just run **runscript.py**. We only coded out the linear dynamics but once we code out the nonlinear dynamics you can specify this in the **runscript.py** on line 18
model.integrate_linear_dynamics()  or model.integrate_nonlinear_dynamics()







