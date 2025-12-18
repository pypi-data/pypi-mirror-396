import htrdr
import numpy as np
import scipy.constants as cst

'''
This a an exemple script to generate a reflectance spectrum with htrdr-planets.
It has not been tested but should work (almost) correctly and at least, provides
an correct overview of the structure of such a code.
'''

# atmosphere parameters
nLat = 50
nLon = 50
radius = 2575 * cst.kilo

# source parameters
distance2sun = 1 * cst.au
sunRadius = 7e5 * cst.kilo
sunTemperature = 5772 K

# observation parameters
observation = {
        'azimut': ,
        'phase': ,
        'incidence': ,
        'emergence'
        }

# list of wavelengths
wavelengths = np.array([...])

# name for the created folders and files
name = "spectrum_exemple"

file = "/path/to/input/file"

def readInput(file):
    nLevel = 
    nLat = 
    nWavelengths = 
    nWeights = 

    wavelength = np.zeros(nWavelengths)
    bandsLow = np.zeros(nWavelengths)
    bandsUp = np.zeros(nWavelengths)
    altitudes = np.zeros(nLevel)
    absorption = np.zeros((nWavelengths, nLevel, nWeights))
    scattering = np.zeros((nWavelengths, nLevel, nWeights))
    singleAlbedo = np.zeros((nWavelengths, nLevel, nWeights))
    assymetry = np.zeros((nWavelengths, nLevel, nWeights))
    surfaceAlbedo = np.zeros(nWavelengths)
    temperatures = np.zeros(nLevel)

    surfaceTemperature = 

    return {
            "nLevel": nLevel,
            "nLat": nLat,
            "nCoeff": nWeights,
            "nWavelengths": nWavelengths,
            "weights": gweight,
            "altitude (m)": altitudes
            "scattering (m-1)": scattering,
            "absorption (m-1)": absorption,
            "temperature (K)": temperatures,
            "assymetry": assymetry,
            "wavelength": wavelength,
            "band low": bandsLow,
            "band up": bandsUp,
            "surface albedo": surfaceAlbedo,
            "surface temperature": surfaceTemperature
            }


dictionnary = readInput(file)

# we create the Data object that will manage the creation of htrdr input files
data = htrdr.Data(radius, nTheta=nLat, nPhi=nLon, name=name)

                        #
                       # #
                      # # #
                     #  #  #
                    #   #   #
                   ###########
### IN PLAN PARALLEL, THE RADIUS IS USED AS X AND Y DIMENSION.
### THE VALUE MUST BE LARGE ENOUGH TO SIMULATE AN INFINITE MEDIUM

# we provide the atmosphere optical and physical properties to the Data object
data.makeAtmosphereFrom1D(data)    # will generate a horizontally homogeneous sphere
#data.makeAtmosphereFrom1D_PP(data) # will generate a plan parallel atmosphere

# we create the brdf dictionnary
brdf = {
        "kind": "lambertian",
        "albedo": np.array(dictionnary["surface albedo"]),
        "bands": np.array([dictionnary["band low"], dt["band up"]]).T
        }
# we provide the ground optical and physical properties to the Data object
data.makeGroundFrom1D(brdf=brdf,    # will generate a horizontally homogeneous sphere
                      SurfaceTemperature=dictionnary['surface temperatrure'])
# data.makeGroundFrom1D_PP(brdf=brdf, # will generate a flat ground
#                          SurfaceTemperature=dictionnary['surface temperatrure'])

# we generate the input and VTK files
data.writeInputs()
data.writeVTKfiles() # VTK files are not mandatory but help the visualisation of the inputs

# we create the observation geometry generated from Azimut, Phase, Incident and
# Emergent angles
geometry = htrdr.geometry()
geometry.geometryFromAPIE(observation=observation,
                          distance=100*cst.kilo,
                          radius=radius,
                          cameraFOV=1e-10,
                          sourceDist=distance2sun,
                          sourceRad=sunRadius,
                          sourceTemp=sunTemperature)

# we generate the script, here a reflectance spectrum in the exemple
script = htrdr.Script()
script.reflectanceSpectrum(geometry, 'sw', wavelengths, MPIcmd="mpirun -np 4")

# we call the script on the data
script(data)

# we post-process the spectrum which will be written in a result file
pp = htrdr.Postprocess(script)

# we remove the input files (not mandatory)
data.cleanInputs()
