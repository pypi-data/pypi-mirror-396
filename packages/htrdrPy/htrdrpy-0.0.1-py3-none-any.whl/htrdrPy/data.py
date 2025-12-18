import numpy as np
import pathlib
import os
import scipy.constants as cst
import netCDF4 as nc
import warnings
from scipy.spatial import Delaunay
from threading import Thread, active_count
import subprocess

from htrdrPy.include.meshgen import *
from htrdrPy.include.meshvisual import *
from htrdrPy.include.write import *
from htrdrPy.include.read import *

from htrdrPy.helperFunctions import *


class Data:
    _count = 0

    def __init__(self, radius, nTheta=None, nPhi=None, mass=None, gravity=None,
                 name=""):
        ''' The Data module aims at managing the input data
         (atmospheric profiles, ground properties, ...) to generate the
         necessary input files.
        # Input:
        - radius (float [m]): planet radius
        - nTheta (optional, default=0, not requested if meshes loaded from
          file): number of longitude points in range [-180°,180°]
        - nPhi (optional, default=0, not requested if meshes loaded from file):
          number of latitude points in range [0°,360°]
        - mass (optional, default=0, float [kg], requested only for GCM data to
          extract the altitude grid from the geopotential): planet mass
        - name (oprional, default: count the number of Data instance, str or
                int): name for the dataset. Useful when working with multiple
        dataset in the same working directory to avoid conflicts between files.
        '''

        self.nTheta = nTheta
        self.nPhi = nPhi
        self.radius = radius
        self.mass = mass
        self.gravity = gravity
        if (not self.gravity) and self.mass:
            self.gravity = cst.G * self.mass / self.radius**2

        self.dataGround = None
        self.dataAtm = None

        self.workingDirectory = pathlib.Path().resolve()
        if name:
            self.name = name
        else:
            self.name = f"{Data._count}"
        self.inputPath = f'{self.workingDirectory}/inputs_{self.name}/'
        self.outputPath = f'{self.workingDirectory}/outputs_{self.name}/'
        self.vtkPath = f"{self.workingDirectory}/VTK_{self.name}/"

        self.groundGeometry = f'{self.inputPath}groundGeometry.bin'
        self.groundSurfaceProperties = f'{self.inputPath}groundSurfaceProperties.bin'
        self.groundMaterialList = f'{self.inputPath}groundMaterialList.txt'
        self.atmosphereGeometry = f'{self.inputPath}atmosphereGeometry.bin'
        self.gasTempearture = f'{self.inputPath}gasTempearture.bin'
        self.gasOpticalProperties = f'{self.inputPath}gasOpticalProperties.bin'
        self.particleOpticalProperties = f'{self.inputPath}particleOpticalProperties.bin'
        self.phaseFunctionList = f'{self.inputPath}phaseFunctionList.txt'
        self.phaseFunctionFile = f'{self.inputPath}phaseFunction.bin'
        try:
            os.mkdir(self.outputPath)
        except FileExistsError:
            pass
        try:
            os.mkdir(self.inputPath)
        except FileExistsError:
            pass
        self.surfTemperature = False
        Data._count += 1
        return

    def makeGroundFrom1D_PP(self, SurfaceTemperature, brdf):
        ''' Generates spherical ground considering uniform temperature and
        optical properties
        # Input
        - SurfaceTemperature (float [K]): uniform temperature of the surface
        - brdf (dictionnary): contains the surface reflectivity data with the
          following items:
            - "kind" (str = "lambertian" or "specular"): kind of brdf function
              to use
            - "albedo" (list or numpy 1-D array (shape=(nWavelength), float
              [])): wavelength dependent surface albedos (should match the size
              of "wavelengths" or "bands")
            - "wavelengths" or "bands":
                - if "wavelengths" (list or numpy 1-D array
                  (shape=(nWavelength), float [m]) wavelengths where the albedo
                  is defined
                - if "bands" (numpy 2-D array (shape=(nWavelength,2), float [m])) 
                wavelengths bands where the
                albedo is defined, the values corresponds to the bands limits
                '''
        # Generate mesh
        node_coord,cell_ids = cubic_ground_mesh(self.radius, self.radius, self.radius)
        print('generating bin...')

        Temperature = np.ones(len(cell_ids)) * SurfaceTemperature

        brdfFile = f"{self.inputPath}material.dat"
        self.__writeBRDFfile(brdfFile, brdf)
            

        with open(self.groundMaterialList, 'w') as f:
            f.write("\t 1 ")
            f.write(f"\n{brdfFile}")

        brdfIndices = np.zeros(len(cell_ids), dtype=int)

        self.ground = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": Temperature,
            "brdf indices": brdfIndices

        }
        return

    def makeGroundFrom1D(self, SurfaceTemperature, brdf):
        '''
        Generates spherical ground considering uniform temperature and optical properties
        # Input
        - SurfaceTemperature (float [K]): uniform temperature of the surface
        - brdf (dictionnary): contains the surface reflectivity data with the following items:
            - "kind" (str = "lambertian" or "specular"): kind of brdf function to use
            - "albedo" (list or numpy 1-D array (shape=(nWavelength), float [])): wavelength dependent surface albedos (should match the size of "wavelengths" or "bands")
            - "wavelengths" or "bands":
                - if "wavelengths" (list or numpy 1-D array (shape=(nWavelength), float [m]) wavelengths where the albedo is defined
                - if "bands" (numpy 2-D array (shape=(nWavelength,2), float [m])) wavelengths bands where the albedo is defined, the values corresponds to the bands limits
        '''
        # Generate mesh
        node_coord,cell_ids = sphere_ground_mesh(self.nTheta, self.nPhi, self.radius)
        print('generating bin...')

        Temperature = np.ones(len(cell_ids)) * SurfaceTemperature

        brdfFile = f"{self.inputPath}material.dat"
        self.__writeBRDFfile(brdfFile, brdf)
            

        with open(self.groundMaterialList, 'w') as f:
            f.write("\t 1 ")
            f.write(f"\n{brdfFile}")

        brdfIndices = np.zeros(len(cell_ids), dtype=int)

        self.ground = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": Temperature,
            "brdf indices": brdfIndices

        }
        return

    def makeGroundFrom2D(self, SurfaceTemperature, brdf):
        '''
        Generates spherical ground considering properties varying along the latitude.
        # Input
        - SurfaceTemperature (1-D array, (shape=nLat), float [K]): temperature of the surface
        - brdf (dictionnary): contains the surface reflectivity data with the following items:
            - "kind" (str = "lambertian" or "specular"): kind of brdf function to use
            - "albedo" (list or numpy 2-D array (shape=(nWavelength, nLat), float [])): wavelength dependent surface albedos (first dimension should match the size of "wavelengths" or "bands")
            - "latitude" (1-D array, (shape=nLat), float [°]): latitudes
            - "wavelengths" or "bands":
                - if "wavelengths" (list or numpy 1-D array (shape=(nWavelength), float [m]) wavelengths where the albedo is defined
                - if "bands" (numpy 2-D array (shape=(nWavelength,2), float [m])) wavelengths bands where the albedo is defined, the values corresponds to the bands limits
        '''
        self.latitudeGrd = brdf["latitude"]
        self.nTheta = len(brdf["latitude"])
        # Generate mesh
        node_coord,cell_ids = sphere_ground_mesh(self.nTheta, self.nPhi, self.radius)
        print('generating bin...')

        with open(self.groundMaterialList, 'w') as f:
            f.write(f"\t {self.nTheta} ")
            for iLat in range(self.nTheta):
                brdfFile = f"{self.inputPath}material_{iLat}.dat"
                f.write(f"\n{brdfFile}")
                if "bands" in brdf.keys(): key = "bands"
                elif "wavelengths" in brdf.keys(): key = "wavelengths"
                else: raise KeyError("wavelengths or bands not found in the brdf dictionnary")
                brdfLat = {
                    "kind": brdf["kind"],
                    "albedo": brdf["albedo"][:,iLat],
                    key: brdf[key]
                }
                self.__writeBRDFfile(brdfFile, brdfLat)

        latitudeNodes = np.array([cart2sphere(node)[1] for node in node_coord])         # calculate nodes latitude
        latitudeCells = latitudeNodes[cell_ids].mean(axis=-1)                           # calculate cell centers latitude
        indices = abs(self.latitudeGrd[None,:] - latitudeCells[:,None]).argmin(axis=1)  # find the indices corresponding

        print(cell_ids.shape)
        print(latitudeCells.shape)
        print(indices.shape)

        brdfIndices = indices
        Temperature = SurfaceTemperature[indices]   # asigning temperature

        self.ground = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": Temperature,
            "brdf indices": brdfIndices

        }
        return

    def makeGroundFrom3D(self, SurfaceTemperature, brdf):
        '''
        Generates spherical ground considering properties varying along the latitude.
        # Input
        - SurfaceTemperature (1-D array, (shape=(nLat, nLon)), float [K]): temperature of the surface
        - brdf (dictionnary): contains the surface reflectivity data with the following items:
            - "kind" (str = "lambertian" or "specular"): kind of brdf function to use
            - "albedo" (list or numpy 2-D array (shape=(nWavelength, nLat, nLon), float [])): wavelength dependent surface albedos (first dimension should match the size of "wavelengths" or "bands")
            - "latitude" (1-D array, (shape=nLat), float [°]): latitudes
            - "longitude" (1-D array, (shape=nLon), float [°]): longitudes
            - "wavelengths" or "bands":
                - if "wavelengths" (list or numpy 1-D array (shape=(nWavelength), float [m]) wavelengths where the albedo is defined
                - if "bands" (numpy 2-D array (shape=(nWavelength,2), float [m])) wavelengths bands where the albedo is defined, the values corresponds to the bands limits
        '''
        self.latitudeGrd = brdf["latitude"]
        self.longitudeGrd = brdf["longitude"]
        self.nTheta = len(brdf["latitude"])
        self.nPhi = len(brdf["longitude"])
        # Generate mesh
        node_coord,cell_ids = sphere_ground_mesh(self.nTheta, self.nPhi, self.radius)
        print('generating bin...')

        indLatLon = np.zeros((self.nTheta, self.nPhi), dtype=int)
        ind = 0
        with open(self.groundMaterialList, 'w') as f:
            f.write(f"\t {self.nTheta*self.nPhi} ")
            for iLat,iLon in np.ndindex(self.nTheta, self.nPhi):
                indLatLon[iLat,iLon] = ind
                ind += 1
                brdfFile = f"{self.inputPath}material_{iLat}_{iLon}.dat"
                f.write(f"\n{brdfFile}")
                if "bands" in brdf.keys(): key = "bands"
                elif "wavelengths" in brdf.keys(): key = "wavelengths"
                else: raise KeyError("wavelengths or bands not found in the brdf dictionnary")
                brdfCol = {
                    "kind": brdf["kind"],
                    "albedo": brdf["albedo"][:,iLat,iLon],
                    key: brdf[key]
                }
                self.__writeBRDFfile(brdfFile, brdfCol)

        # latitudeNodes = np.array([cart2sphere(node)[1] for node in node_coord])         # calculate nodes latitude
        # longitudeNodes = np.array([cart2sphere(node)[2] for node in node_coord])         # calculate nodes latitude
        # latitudeCells = latitudeNodes[cell_ids].mean(axis=-1)                           # calculate cell centers latitude
        # longitudeCells = longitudeNodes[cell_ids].mean(axis=-1)                           # calculate cell centers longitude

        #cellCenter = np.array([node_coord[ids].mean(axis=-1) for ids in
        #                       cell_ids])

        # nodeCoordSph = np.array([cart2sphere(node) for node in node_coord])
        # cellCenterSph = np.array([nodeCoordSph[ids].mean(axis=-1) for ids in
        #                        cell_ids])
        # cellCenter = np.array([sphere2cart(cell) for cell in cellCenterSph])

        x, y, z = node_coord.T
        latitudeCells = []
        longitudeCells = []
        for cell in cell_ids:
            i, j, k = cell
            newX = (x[i] + x[j] + x[k]) / 3
            newY = (y[i] + y[j] + y[k]) / 3
            newZ = (z[i] + z[j] + z[k]) / 3
            dump, lat, lon = cart2sphere(np.array([newX, newY, newZ]))
            latitudeCells.append(lat)
            longitudeCells.append(lon)
        latitudeCells = np.array(latitudeCells)
        longitudeCells = np.array(longitudeCells)


        # fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        # import matplotlib as mpl
        # X, Y, Z = node_coord.T
        # triangulation = mpl.tri.Triangulation(X, Y, triangles=cell_ids)
        # ax.plot_trisurf(triangulation, Z, alpha=0.5)
        # ax.scatter(*cellCenter.T, s=20, color='r')
        # set_axes_equal(ax)
        # plt.show()

        indicesLat = abs(self.latitudeGrd[None,:] - latitudeCells[:,None]).argmin(axis=1)  # find the indices corresponding
        indicesLon = abs(self.longitudeGrd[None,:] - longitudeCells[:,None]).argmin(axis=1)  # find the indices corresponding

        brdfIndices = indLatLon[indicesLat,indicesLon]
        Temperature = SurfaceTemperature[indicesLat,indicesLon]   # asigning temperature

        self.ground = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": Temperature,
            "brdf indices": brdfIndices

        }
        return

    def makeAtmosphereFrom1D_PP(self, data):
        '''
        Generate a plan parallel atmosphere from single column data.
        Here, the haze and gas data are mixed in a single array.
        # Input
        - data (dict): Dictionnary with the following items: 
            - "nLevel" (integer): number of levels (not layers),
            - "nCoeff" (integer): number of quadrature points for the k-coeff,
            - "nWavelengths" (integer): number of wavelengths,
            - "nAngle" (optional, default=None, integer): number of angles in the phase functions (not required if using the builtin phase function),
            - "weights" (list or 1-D array (shape=(nWavelengths, nCoeff), float [])): the weigths of the nCoeff quadrature points,
            - "altitude (m)" (1-D array (shape=(nLevel), float [m])): altitudes,
            - "scattering (m-1)": (1-D array (shape=(nWavelengths, nLevel, nCoeff), float [m-1])) scattering coefficients,
            - "absorption (m-1)": (1-D array (shape=(nWavelengths, nLevel, nCoeff), float [m-1])) absorption coefficients,
            - "angles (°)": (1-D array (shape=(nAngle), float [°])) angles for phase function,
            - "phaseFunc" or "assymetry": (1-D array (shape = (nLevel, nAngle) or (nLevel, nCoeff), float [])) phase functions or assymetry parameter,
            - "wavelength": (1-D array (shape = (nWavelengths), float [m]) wavelength,
            - "band low": (1-D array (shape = (nWavelengths), float [m]) lower boundary of wavelength band,
            - "band up": (1-D array (shape = (nWavelengths), float [m]) upper boundary of wavelength band
        '''

        ##############################################################
        # reading the input files and storing the data in dictionnary <data>
        altitude = data["altitude (m)"]
        nLevel = data["nLevel"]
        self.nLevel = nLevel
        self.nWavelength = data["nWavelengths"]
        self.wavelengths = data["wavelength"] / cst.nano

        ##############################################################
        # testing wether a temperature profile is given or a single value
        temperatures = data["temperature (K)"]
        self.temperatureCells = np.reshape(temperatures, (self.nLevel,1,1))   # shape=(nLevel, nLat, nPhi)

        if "pressure (Pa)" in data.keys(): self.pressure = np.tile(data["pressure (Pa)"][:,None,None], (1,self.nTheta,self.nPhi))   # shape=(nLevel, nLat, nPhi)    

        ##############################################################
        # writing the file containing the list of phase functions
        if "phaseFunc" in data.keys():
            angles = data["angles (°)"]
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(nLevel))
                wavelength = np.array([dt["wavelength"] for dt in data.values()]) / cst.nano
                for k in range(nLevel):
                    phaseFunctions = np.array([dt["phaseFunc"][k,:] for dt in data.values()]).T
                    arr = [angles, wavelength, phaseFunctions]
                    fileName = f"{self.inputPath}phase_function_alt{k}.dat"
                    write_phase_function_decrete_dat(fileName, arr)
                    f.write(f"\n{fileName}")
        elif "assymetry" in data.keys():
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(nLevel))
                for k in range(nLevel):
                    fileName = f"{self.inputPath}phase_function_alt{k}.dat"
                    self.__writeHGphaseFunction(fileName, data["assymetry"][:,k,0])
                    f.write(f"\n{fileName}")
        else: raise KeyError("phase function or assymetry parameter not found in the data dictionnary")

        ##############################################################
        # generating the mesh
        node_coord,cell_ids = plan_atm_mesh(altitude, self.radius, self.radius)
        self.nNodes = len(node_coord)

        ##############################################################
        # binding the data to the nodes

        print("Assigning data to nodes ...")
        alt = node_coord[:,0]                               # calculate corresponding altitude
        diffs = np.abs(altitude[None, :] - alt[:, None])       # find the indices corresponding
        indices = np.argmin(diffs, axis=1)                  # to nodes altitudes altitude
        temperatureNodes = temperatures[indices]             # asigning temperature
        phaseFunctionsIndices = np.copy(indices)            # asigning phase function

        scatt = np.array(data["scattering (m-1)"])                          # retrieving scattering coefficients
        abso = np.array(data["absorption (m-1)"] )                          # retrieving absorption coefficients
        absorption = abso[:,indices,:]                                      # asigning absorption coefficients
        scattering = (data["weights"][:,None,:] * scatt[:,indices,:]).sum(axis=2)   # asigning scattering coefficients

        ##############################################################
        # generating the atmosphere dictionnary used by self.prepareInput()
        self.atmosphere = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": temperatureNodes,                    # shape = (nNodes)
            "bands low": np.array(data["band low"]) / cst.nano, # shape = (nWavelength)
            "bands up": np.array(data["band up"]) / cst.nano,   # shape = (nWavelength)
            "weights": data["weights"],                         # shape = (nWavelength, nCoeff)
            "absorption (gas)": absorption,                     # shape = (nWavelength, nNodes, nCoeff)
            "absorption (haze)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (gas)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (haze)": scattering,                    # shape = (nWavelength, nNodes)
            "phase func indices": phaseFunctionsIndices         # shape = (nNodes)
        }
        return

    def makeAtmosphereFrom1Danalytic_PP(self, extinction, singleScatteringAlbedo, assymetry, args, band, altitudes, temperature=0, nAngle=0, phaseFunc=lambda g,theta: 1 + 3*g * np.cos(theta)):
        ''' 
        Generate an homogeneous sphere from single column data.
        Here, the haze and gas data are mixed in a single array.
        # Input
        - temperature (optional, default = 0 (for short wave calculations, i.e. no thermal emission accounted), float [k] or 1_D array (shape=(nLevel), float [k])): \
            homogeneous temperature or temperature profile 
        '''

        nLevel = len(altitudes)
        radii = altitudes+self.radius
        self.nWavelength = 1
        self.wavelengths = np.array([np.mean(band)]) / cst.nano

        ##############################################################
        # testing wether a temperature profile is given or a single value
        try:
            if len(temperature) != nLevel:
                raise IndexError("error in temperature profile: size mismatch")
        except TypeError:
            temperature = np.ones(nLevel) * temperature

        ##############################################################
        # testing wether a temperature profile is given or a single value
        try:
            if len(singleScatteringAlbedo) != nLevel:
                raise IndexError("error in temperature profile: size mismatch")
        except TypeError:
            singleScatteringAlbedo = np.ones(nLevel) * singleScatteringAlbedo

        ##############################################################
        # generating the mesh
        node_coord,cell_ids = plan_atm_mesh(radii, self.radius, self.radius)
        self.nNodes = len(node_coord)

        ##############################################################
        # binding the data to the nodes

        print("Assigning data to nodes ...")
        alt = node_coord[:,0]                               # calculate corresponding altitude
        diffs = np.abs(radii[None, :] - alt[:, None])       # find the indices corresponding
        indices = np.argmin(diffs, axis=1)                  # to nodes altitudes altitude
        temperatureNodes = temperature[indices]             # asigning temperature
        phaseFunctionsIndices = np.copy(indices)            # asigning phase function


        ext = extinction(altitudes, *args)
        abso = (1 - singleScatteringAlbedo) * ext
        scatt = singleScatteringAlbedo * ext

        abso = abso.reshape((self.nWavelength, nLevel, 1))
        scatt = scatt.reshape((self.nWavelength, nLevel))
        assymetry = assymetry.reshape((self.nWavelength, nLevel))


        absorption = abso[:,indices,:]  # asigning absorption coefficients
        scattering = scatt[:,indices]   # asigning scattering coefficients


        ##############################################################
        # writing the file containing the list of phase functions
        if nAngle==0:
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(nLevel))
                for k in range(nLevel):
                    fileName = f"{self.inputPath}phase_function_alt{k}.dat"
                    self.__writeHGphaseFunction(fileName, assymetry[:,k])
                    f.write(f"\n{fileName}")
        else:
            angles = np.linspace(0, 180, nAngle)
            phaseFunctions = phaseFunc(assymetry[:,:,None], angles[None,:]*cst.degree)
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(nLevel))
                for k in tqdm.tqdm(range(nLevel)):
                    ##############################################################
                    # writing the file containing the list of phase functions
                    phase = phaseFunctions[:,k,:].T  # shape = (nAngle, nWavelength)
                    arr = [angles, self.wavelengths, phase]
                    fileName = f"{self.inputPath}phase_function_node_{k}.dat"
                    write_phase_function_decrete_dat(fileName, arr)
                    f.write(f"\n{fileName}")

        ##############################################################
        # generating the atmosphere dictionnary used by self.prepareInput()
        self.atmosphere = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": temperatureNodes,                # shape = (nNodes)
            "bands low": np.array([band[0]]) / cst.nano,    # shape = (nWavelength)
            "bands up": np.array([band[1]]) / cst.nano,     # shape = (nWavelength)
            "weights": np.ones((self.nWavelength, 1)),      # shape = (nWavelength, nCoeff)
            "absorption (gas)": absorption,                 # shape = (nWavelength, nNodes, nCoeff)
            "absorption (haze)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (gas)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (haze)": scattering,                # shape = (nWavelength, nNodes)
            "phase func indices": phaseFunctionsIndices     # shape = (nNodes)
        }
        return

    def __makeAtmosphereFrom1D(self, readingRoutine, files, temperature=0):
        ''' 
        Generate an homogeneous sphere from single column data.
        Here, the haze and gas data are mixed in a single array.
        # Input
        - readingRoutine (func): the routine adapted for reading the file. It must produce a dictionnary with the following items: 
            - "nLevel" (integer): number of levels (not layers),
            - "nCoeff" (integer): number of quadrature points for the k-coeff,
            - "nAngle" (integer): number of angles in the phase functions,
            - "weights" (list or 1-D array (shape=(nCoeff), float [])): the weigths of the nCoeff quadrature points,
            - "altitude (m)" (1-D array (shape=(nLevel), float [m])): altitudes,
            - "scattering (m-1)": (1-D array (shape=(nLevel, nCoeff), float [m-1])) scattering coefficients,
            - "absorption (m-1)": (1-D array (shape=(nLevel, nCoeff), float [m-1])) absorption coefficients,
            - "angles (°)": (1-D array (shape=(nAngle), float [°])) angles for phase function,
            - "phaseFunc": (1-D array (shape = (nLevel, nAngle), float [])) phase functions,
            - "wavelength": (float [m]) wavelength,
            - "band low": (float [m]) lower boundary of wavelength band,
            - "band up": (float [m]) upper boundary of wavelength band
        - files (list, str): is the file list to be read, one for every wavelength
        - temperature (optional, default = 0 (for short wave calculations, i.e. no thermal emission accounted), float [k] or 1_D array (shape=(nLevel), float [k])): \
            homogeneous temperature or temperature profile 
        '''

        ##############################################################
        # reading the input files and storing the data in dictionnary <data>
        self.nWavelength = len(files)
        data = {}
        for i,file in enumerate(files):
            dt = readingRoutine(file)
            dt['altitude (m)'] += self.radius 
            data[i] = dt
            altitude = dt["altitude (m)"]
            nLevel = dt["nLevel"]
            angles = dt["angles (°)"]

        bandsLow = np.array([dt["band low"] for dt in data.values()]) / cst.nano
        bandsUp = np.array([dt["band up"] for dt in data.values()]) / cst.nano
        weights = np.array([dt["weights"] for dt in data.values()])

        ##############################################################
        # testing wether a temperature profile is given or a single value
        try:
            if len(temperature) != nLevel:
                raise IndexError("error in temperature profile: size mismatch")
        except TypeError:
            temperature = np.ones(nLevel) * temperature

        ##############################################################
        # writing the file containing the list of phase functions
        with open(self.phaseFunctionList, 'w') as f:
            f.write(str(nLevel))
            wavelength = np.array([dt["wavelength"] for dt in data.values()]) / cst.nano
            for k in range(nLevel):
                phaseFunctions = np.array([dt["phaseFunc"][k,:] for dt in data.values()]).T
                arr = [angles, wavelength, phaseFunctions]
                fileName = f"{self.inputPath}phase_function_alt{k}.dat"
                write_phase_function_decrete_dat(fileName, arr)
                f.write(f"\n{fileName}")

        ##############################################################
        # generating the mesh
        node_coord,cell_ids = spherical_mesh_control_cell(self.nTheta, self.nPhi, altitude)
        self.nNodes = len(node_coord)

        ##############################################################
        # binding the data to the nodes

        print("Assigning data to nodes ...")
        alt = np.linalg.norm(node_coord, axis=1)                            # calculate corresponding altitude
        diffs = np.abs(altitude[None, :] - alt[:, None])                    # find the indices corresponding
        indices = np.argmin(diffs, axis=1)                                  # to nodes altitudes altitude
        temperatureNodes = temperature[indices]                             # asigning temperature
        phaseFunctionsIndices = np.copy(indices)                            # asigning phase function
        scatt = np.array([dt["scattering (m-1)"] for dt in data.values()])  # retrieving scattering coefficients
        abso = np.array([dt["absorption (m-1)"] for dt in data.values()])   # retrieving absorption coefficients
        absorption = abso[:,indices,:]                                      # asigning absorption coefficients
        scattering = (weights[:,None,:] * scatt[:,indices,:]).sum(axis=2)   # asigning scattering coefficients

        ##############################################################
        # generating the atmosphere dictionnary used by self.prepareInput()
        self.atmosphere = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": temperatureNodes,    # shape = (nNodes)
            "bands low": bandsLow,              # shape = (nWavelength)
            "bands up": bandsUp,                # shape = (nWavelength)
            "weights": weights,                 # shape = (nWavelength, nCoeff)
            "absorption (gas)": absorption,     # shape = (nWavelength, nNodes, nCoeff)
            "absorption (haze)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (gas)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (haze)": scattering,            # shape = (nWavelength, nNodes)
            "phase func indices": phaseFunctionsIndices # shape = (nNodes)
        }   
        return

    def makeAtmosphereFrom1D(self, data):
        ''' 
        Generate an homogeneous sphere from single column data.
        Here, the haze and gas data are mixed in a single array.
        # Input
        - data (dict): Dictionnary with the following items: 
            - "nLevel" (integer): number of levels (not layers),
            - "nCoeff" (integer): number of quadrature points for the k-coeff,
            - "nWavelengths" (integer): number of wavelengths,
            - "nAngle" (optional, default=None, integer): number of angles in the phase functions (not required if using the builtin phase function),
            - "weights" (list or 1-D array (shape=(nWavelengths, nCoeff), float [])): the weigths of the nCoeff quadrature points,
            - "altitude (m)" (1-D array (shape=(nLevel), float [m])): altitudes,
            - "scattering (m-1)": (1-D array (shape=(nWavelengths, nLevel, nCoeff), float [m-1])) scattering coefficients,
            - "absorption (m-1)": (1-D array (shape=(nWavelengths, nLevel, nCoeff), float [m-1])) absorption coefficients,
            - "angles (°)": (1-D array (shape=(nAngle), float [°])) angles for phase function,
            - "phaseFunc" or "assymetry": (1-D array (shape = (nLevel, nAngle) or (nLevel, nCoeff), float [])) phase functions or assymetry parameter,
            - "wavelength": (1-D array (shape = (nWavelengths), float [m]) wavelength,
            - "band low": (1-D array (shape = (nWavelengths), float [m]) lower boundary of wavelength band,
            - "band up": (1-D array (shape = (nWavelengths), float [m]) upper boundary of wavelength band
        '''

        # warnings.warn("This routine has not been tested yet. Please use with caution.")

        ##############################################################
        # reading the input files and storing the data in dictionnary <data>
        # data = readingRoutine(*args)
        self.altitudes = data["altitude (m)"] + self.radius 
        self.latitudes = np.linspace(-90, 90, self.nTheta, endpoint=False)
        self.longitudes = np.linspace(0, 360, self.nPhi, endpoint=False)
        nLevel = data["nLevel"]
        self.nLevel = nLevel
        self.nWavelength = data["nWavelengths"]
        self.wavelengths = data["wavelength"] / cst.nano

        ##############################################################
        # testing wether a temperature profile is given or a single value
        temperatures = data["temperature (K)"]
        self.temperatureCells = np.tile(temperatures[:,None,None], (1,self.nTheta,self.nPhi))   # shape=(nLevel, nLat, nPhi)

        if "pressure (Pa)" in data.keys(): self.pressure = np.tile(data["pressure (Pa)"][:,None,None], (1,self.nTheta,self.nPhi))   # shape=(nLevel, nLat, nPhi)    

        ##############################################################
        # writing the file containing the list of phase functions
        if "phaseFunc" in data.keys():
            angles = data["angles (°)"]
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(nLevel))
                wavelength = np.array([dt["wavelength"] for dt in data.values()]) / cst.nano
                for k in range(nLevel):
                    phaseFunctions = np.array([dt["phaseFunc"][k,:] for dt in data.values()]).T
                    arr = [angles, wavelength, phaseFunctions]
                    fileName = f"{self.inputPath}phase_function_alt{k}.dat"
                    write_phase_function_decrete_dat(fileName, arr)
                    f.write(f"\n{fileName}")
        elif "assymetry" in data.keys():
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(nLevel))
                for k in range(nLevel):
                    fileName = f"{self.inputPath}phase_function_alt{k}.dat"
                    self.__writeHGphaseFunction(fileName, data["assymetry"][:,k,0])
                    f.write(f"\n{fileName}")
        else: raise KeyError("phase function or assymetry parameter not found in the data dictionnary")

        ##############################################################
        # generating the mesh
        node_coord,cell_ids = spherical_mesh_control_cell(self.nTheta,
                                                          self.nPhi,
                                                          self.altitudes)
        self.nNodes = len(node_coord)

        ##############################################################
        # binding the data to the nodes

        print("Assigning data to nodes ...")
        alt = np.linalg.norm(node_coord, axis=1)                            # calculate corresponding altitude
        diffs = np.abs(altitude[None, :] - alt[:, None])                    # find the indices corresponding
        indices = np.argmin(diffs, axis=1)                                  # to nodes altitudes altitude
        temperatureNodes = temperatures[indices]                                # asigning temperature
        phaseFunctionsIndices = np.copy(indices)                            # asigning phase function
        scatt = np.array(data["scattering (m-1)"])                          # retrieving scattering coefficients
        abso = np.array(data["absorption (m-1)"] )                          # retrieving absorption coefficients
        absorption = abso[:,indices,:]                                      # asigning absorption coefficients
        scattering = (data["weights"][:,None,:] * scatt[:,indices,:]).sum(axis=2)   # asigning scattering coefficients

        ##############################################################
        # generating the atmosphere dictionnary used by self.prepareInput()
        self.atmosphere = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": temperatureNodes,                    # shape = (nNodes)
            "bands low": np.array(data["band low"]) / cst.nano, # shape = (nWavelength)
            "bands up": np.array(data["band up"]) / cst.nano,   # shape = (nWavelength)
            "weights": data["weights"],                         # shape = (nWavelength, nCoeff)
            "absorption (gas)": absorption,                     # shape = (nWavelength, nNodes, nCoeff)
            "absorption (haze)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (gas)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (haze)": scattering,                    # shape = (nWavelength, nNodes)
            "phase func indices": phaseFunctionsIndices         # shape = (nNodes)
        }
        return

    def makeAtmosphereFrom1DhazeNgas(self, readingRoutine, files, temperature=0):
        ''' 
        Generate an homogeneous sphere from single column data.
        Here, the haze and gas data are given in independant arrays.
        # Input
        - readingRoutine (func): the routine adapted for reading the file. It must produce a dictionnary with the following items: 
            - "nLevel" (integer): number of levels (not layers),
            - "nCoeff" (integer): number of quadrature points for the k-coeff,
            - "nAngle" (integer): number of angles in the phase functions,
            - "weights" (list or 1-D array (shape=(nCoeff), float [])): the weigths of the nCoeff quadrature points,
            - "altitude (m)" (1-D array (shape=(nLevel), float [m])): altitudes,
            - "gas scattering (m-1)": (1-D array (shape=(nLevel, nCoeff), float [m-1])) scattering coefficients,
            - "haze scattering (m-1)": (1-D array (shape=(nLevel, nCoeff), float [m-1])) scattering coefficients,
            - "gas absorption (m-1)": (1-D array (shape=(nLevel, nCoeff), float [m-1])) absorption coefficients,
            - "haze absorption (m-1)": (1-D array (shape=(nLevel, nCoeff), float [m-1])) absorption coefficients,
            - "angles (°)": (1-D array (shape=(nAngle), float [°])) angles for phase function,
            - "phaseFunc": (1-D array (shape = (nLevel, nAngle), float [])) phase functions,
            - "wavelength": (float [m]) wavelength,
            - "band low": (float [m]) lower boundary of wavelength band,
            - "band up": (float [m]) upper boundary of wavelength band
        - files (list, str): is the file list to be read, one for every wavelength
        - temperature (optional, default = 0 (for short wave calculations, i.e. no thermal emission accounted), float [k] or 1_D array (shape=(nLevel), float [k])): \
            homogeneous temperature or temperature profile 
        '''

        ##############################################################
        # reading the input files and storing the data in dictionnary <data>
        self.nWavelength = len(files)
        data = {}
        for i,file in enumerate(files):
            dt = readingRoutine(file)
            dt['altitude (m)'] += self.radius 
            data[i] = dt
            altitude = dt["altitude (m)"]
            nLevel = dt["nLevel"]
            angles = dt["angles (°)"]

        bandsLow = np.array([dt["band low"] for dt in data.values()]) / cst.nano
        bandsUp = np.array([dt["band up"] for dt in data.values()]) / cst.nano
        weights = np.array([dt["weights"] for dt in data.values()])

        ##############################################################
        # testing wether a temperature profile is given or a single value
        try:
            if len(temperature) != nLevel:
                raise IndexError("error in temperature profile: size mismatch")
        except TypeError:
            temperature = np.ones(nLevel) * temperature

        ##############################################################
        # writing the file containing the list of phase functions
        with open(self.phaseFunctionList, 'w') as f:
            f.write(str(nLevel))
            wavelength = np.array([dt["wavelength"] for dt in data.values()]) / cst.nano
            for k in range(nLevel):
                phaseFunctions = np.array([dt["phaseFunc"][k,:] for dt in data.values()]).T
                arr = [angles, wavelength, phaseFunctions]
                fileName = f"{self.inputPath}phase_function_alt{k}.dat"
                write_phase_function_decrete_dat(fileName, arr)
                f.write(f"\n{fileName}")

        ##############################################################
        # generating the mesh
        node_coord,cell_ids = spherical_mesh_control_cell(self.nTheta, self.nPhi, altitude)
        self.nNodes = len(node_coord)

        ##############################################################
        # binding the data to the nodes

        print("Assigning data to nodes ...")
        alt = np.linalg.norm(node_coord, axis=1)                            # calculate corresponding altitude
        diffs = np.abs(altitude[None, :] - alt[:, None])                    # find the indices corresponding
        indices = np.argmin(diffs, axis=1)                                  # to nodes altitudes altitude
        temperatureNodes = temperature[indices]                             # asigning temperature
        phaseFunctionsIndices = np.copy(indices)                            # asigning phase function
        scattHaze = np.array([dt["haze scattering (m-1)"] for dt in data.values()]) # retrieving scattering coefficients
        absoHaze = np.array([dt["haze absorption (m-1)"] for dt in data.values()])  # retrieving absorption coefficients
        scattGas = np.array([dt["gas scattering (m-1)"] for dt in data.values()])   # retrieving scattering coefficients
        absoGas = np.array([dt["gas absorption (m-1)"] for dt in data.values()])    # retrieving absorption coefficients
        absorptionGas = absoGas[:,indices,:]                                        # asigning absorption coefficients
        scatteringHaze = (weights[:,None,:] * scattHaze[:,indices,:]).sum(axis=2)   # asigning scattering coefficients
        absorptioHaze = (weights[:,None,:] * absoHaze[:,indices,:]).sum(axis=2) # asigning scattering coefficients
        scatteringGas = (weights[:,None,:] * scattGas[:,indices,:]).sum(axis=2) # asigning scattering coefficients

        ##############################################################
        # generating the atmosphere dictionnary used by self.prepareInput()
        self.atmosphere = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": temperatureNodes,    # shape = (nNodes)
            "bands low": bandsLow,              # shape = (nWavelength)
            "bands up": bandsUp,                # shape = (nWavelength)
            "weights": weights,                 # shape = (nWavelength, nCoeff)
            "absorption (gas)": absorptionGas,  # shape = (nWavelength, nNodes, nCoeff)
            "absorption (haze)": absorptioHaze, # shape = (nWavelength, nNodes)
            "scattering (gas)": scatteringGas,  # shape = (nWavelength, nNodes)
            "scattering (haze)": scatteringHaze,# shape = (nWavelength, nNodes)
            "phase func indices": phaseFunctionsIndices # shape = (nNodes)
        }   
        return

    def makeAtmosphereFrom1Danalytic(self, extinction, singleScatteringAlbedo, assymetry, args, band, altitudes, temperature=0):
        ''' 
        Generate an homogeneous sphere from single column data.
        Here, the haze and gas data are mixed in a single array.
        # Input
        - temperature (optional, default = 0 (for short wave calculations, i.e. no thermal emission accounted), float [k] or 1_D array (shape=(nLevel), float [k])): \
            homogeneous temperature or temperature profile 
        '''

        nLevel = len(altitudes)
        radii = altitudes+self.radius
        self.nWavelength = 1
        self.wavelengths = np.array([np.mean(band)]) / cst.nano


        ##############################################################
        # testing wether a temperature profile is given or a single value
        try:
            if len(temperature) != nLevel:
                raise IndexError("error in temperature profile: size mismatch")
        except TypeError:
            temperature = np.ones(nLevel) * temperature


        ##############################################################
        # testing wether a single scattering albedo profile is given or a single value
        try:
            if len(singleScatteringAlbedo) != nLevel:
                raise IndexError("error in temperature profile: size mismatch")
        except TypeError:
            singleScatteringAlbedo = np.ones(nLevel) * singleScatteringAlbedo

        ##############################################################
        # generating the mesh
        node_coord,cell_ids = spherical_mesh_control_cell(self.nTheta, self.nPhi, radii)
        self.nNodes = len(node_coord)

        ##############################################################
        # binding the data to the nodes

        print("Assigning data to nodes ...")
        alt = np.linalg.norm(node_coord, axis=1)                            # calculate corresponding altitude
        diffs = np.abs(radii[None, :] - alt[:, None])                       # find the indices corresponding
        indices = np.argmin(diffs, axis=1)                                  # to nodes altitudes altitude
        temperatureNodes = temperature[indices]                             # asigning temperature
        phaseFunctionsIndices = np.copy(indices)                            # asigning phase function


        ext = extinction(altitudes, *args)
        abso = (1 - singleScatteringAlbedo) * ext
        scatt = singleScatteringAlbedo * ext

        abso = abso.reshape((self.nWavelength, nLevel, 1))
        scatt = scatt.reshape((self.nWavelength, nLevel))
        assymetry = assymetry.reshape((self.nWavelength, nLevel))


        absorption = abso[:,indices,:]  # asigning absorption coefficients
        scattering = scatt[:,indices]   # asigning scattering coefficients


        ##############################################################
        # writing the file containing the list of phase functions
        with open(self.phaseFunctionList, 'w') as f:
            f.write(str(nLevel))
            for k in range(nLevel):
                fileName = f"{self.inputPath}phase_function_alt{k}.dat"
                self.__writeHGphaseFunction(fileName, assymetry[:,k])
                f.write(f"\n{fileName}")

                
        ##############################################################
        # generating the atmosphere dictionnary used by self.prepareInput()
        self.atmosphere = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": temperatureNodes,                # shape = (nNodes)
            "bands low": np.array([band[0]]) / cst.nano,    # shape = (nWavelength)
            "bands up": np.array([band[1]]) / cst.nano,     # shape = (nWavelength)
            "weights": np.ones((self.nWavelength, 1)),      # shape = (nWavelength, nCoeff)
            "absorption (gas)": absorption,                 # shape = (nWavelength, nNodes, nCoeff)
            "absorption (haze)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (gas)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (haze)": scattering,                # shape = (nWavelength, nNodes)
            "phase func indices": phaseFunctionsIndices     # shape = (nNodes)
        }   
        return

    def makeAtmosphereFrom2D(self, data):
        ''' 
        Generate an heterogeneous sphere from a list of columns along a meridian.
        Here, the haze and gas data are mixed in a single array.
        # Input
        - data (dict): Dictionnary with the following items: 
            - "nLevel" (integer): number of levels (not layers),
            - "nLat" (integer): number of latitudes,
            - "nCoeff" (integer): number of quadrature points for the k-coeff,
            - "nWavelengths" (integer): number of wavelengths,
            - "nAngle" (optional, default=None, integer): number of angles in the phase functions (not required if using the builtin phase function),
            - "weights" (list or 2-D array (shape=(nWavelengths, nCoeff), float [])): the weigths of the nCoeff quadrature points,
            - "altitude (m)" (2-D array (shape=(nLevel, nLat), float [m])): altitudes,
            - "pressure (Pa)" (2-D array (shape=(nLevel, nLat), float [Pa])): pressures,
            - "latitude (°)" (1-D array (shape=(nLat), float [°])): latitudes,
            - "scattering (m-1)" (4-D array (shape=(nWavelengths, nLevel, nLat, nCoeff), float [m-1])): scattering coefficients,
            - "absorption (m-1)" (4-D array (shape=(nWavelengths, nLevel, nLat, nCoeff), float [m-1])): absorption coefficients,
            - "temperature (K)" (optional, 2-D array (shape=(nLevel, nLat), float [K])): temperatures,
            - "angles (°)": (optional, 1-D array (shape=(nAngle), float [°])) angles for phase function,
            - "phaseFunc" or "assymetry": (1-D array (shape = (nWavelength, nLevel, nLat, nAngle) or (nWavelength, nLevel, nLat, nCoeff), float [])) phase functions or assymetry parameter,
            - "wavelength": (1-D array (shape = (nWavelengths), float [m]) wavelength,
            - "band low": (1-D array (shape = (nWavelengths), float [m]) lower boundary of wavelength band,
            - "band up": (1-D array (shape = (nWavelengths), float [m]) upper boundary of wavelength band
        '''

        if not self.nPhi: raise ValueError("nPhi must be set before calling this function")
        ##############################################################
        # reading the input files and storing the data in dictionnary <data>
        # data = readingRoutine(*args)
        self.nTheta = data["nLat"]
        self.nLevel = data["nLevel"]
        self.nWavelength = data["nWavelengths"]
        self.nCoeff = data["nCoeff"]
        self.latitudes = data["latitude (°)"]
        self.longitudes = np.linspace(0, 360, self.nPhi, endpoint=False)
        self.altitudes = data["altitude (m)"] + self.radius                       # shape=(nLevel, nLat)
        self.wavelengths = data["wavelength"] / cst.nano
        if "pressure (Pa)" in data.keys(): self.pressure = np.tile(data["pressure (Pa)"][:,:,None], (1,1,self.nPhi))    # shape=(nLevel, nLat, nPhi)    

        coords = np.zeros((self.nLevel, self.nTheta, self.nPhi, 3))         # shape=(nLevel, nLat, nPhi, 3)
        for i,j,k in np.ndindex(self.nLevel,self.nTheta,self.nPhi):
            coords[i,j,k] = np.array([self.altitudes[i,j],
                                      self.latitudes[j],
                                      self.longitudes[k]])

        scattering = np.tile(data["scattering (m-1)"][:,:,:,None,:], (1,1,1,self.nPhi,1))   # shape=(nWavelengths, nLevel, nLat, nLon, nCoeff)
        absorption = np.tile(data["absorption (m-1)"][:,:,:,None,:], (1,1,1,self.nPhi,1))   # shape=(nWavelengths, nLevel, nLat, nLon, nCoeff)

        self.temperatureCells = data["temperature (K)"]
        self.temperatureCells = np.tile(self.temperatureCells[:,:,None], (1,1,self.nPhi))   # shape=(nLevel, nLat, nPhi)

        ##############################################################
        phaseFunctionsIndices = - np.ones((self.nLevel, self.nTheta, self.nPhi))
        # writing the file containing the list of phase functions
        if "phaseFunc" in data.keys():
            angles = data["angles (°)"]
            count = 0
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(self.nLevel*self.nTheta))
                wavelength = np.array(data["wavelength"]) / cst.nano
                for k,j in np.ndindex(self.nLevel,self.nTheta):
                    phaseFunctions = np.array(data["phaseFunc"][:,k,j,:]).T
                    arr = [angles, wavelength, phaseFunctions]
                    fileName = f"{self.inputPath}phase_function_alt{k}_{j}.dat"
                    write_phase_function_decrete_dat(fileName, arr)
                    f.write(f"\n{fileName}")
                    phaseFunctionsIndices[k,j,:] = count
                    count += 1
        elif "assymetry" in data.keys():
            count = 0
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(self.nLevel*self.nTheta))
                for k,j in np.ndindex(self.nLevel,self.nTheta):
                    fileName = f"{self.inputPath}phase_function_alt{k}_{j}.dat"
                    self.__writeHGphaseFunction(fileName, data["assymetry"][:,k,j,0])
                    f.write(f"\n{fileName}")
                    phaseFunctionsIndices[k,j,:] = count
                    count += 1
        else: raise KeyError("phase function or assymetry parameter not found in the data dictionnary")



        self.nNodes = self.nLevel * self.nTheta * self.nPhi
        coords = coords.reshape((self.nNodes,3))
        node_coord = np.array([sphere2cart(coords[i]) for i in range(self.nNodes)]) # shape=(nNodes, 3)
        scattering = scattering.reshape((self.nWavelength, self.nNodes, self.nCoeff))
        absorption = absorption.reshape((self.nWavelength, self.nNodes, self.nCoeff))
        scattering = (data["weights"][:,None,:] * scattering[:,:,:]).sum(axis=2)
        temperatureNodes = self.temperatureCells.reshape(self.nNodes)
        phaseFunctionsIndices = phaseFunctionsIndices.reshape(self.nNodes).astype(int)

        if any(phaseFunctionsIndices == -1): raise ValueError("Wrong index for phase function: -1")

        cell_ids = Delaunay(node_coord)

        ##############################################################
        # generating the atmosphere dictionnary used by self.prepareInput()
        self.atmosphere = {
            "nodes coordinates": node_coord,
            "cells ids": cell_ids.simplices,
            "temperature": temperatureNodes,                    # shape = (nNodes)
            "bands low": np.array(data["band low"]) / cst.nano, # shape = (nWavelength)
            "bands up": np.array(data["band up"]) / cst.nano,   # shape = (nWavelength)
            "weights": data["weights"],                         # shape = (nWavelength, nCoeff)
            "absorption (gas)": absorption,                     # shape = (nWavelength, nNodes, nCoeff)
            "absorption (haze)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (gas)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (haze)": scattering,                    # shape = (nWavelength, nNodes)
            "phase func indices": phaseFunctionsIndices         # shape = (nNodes)
        }
        return

    def makeAtmosphereFrom3D(self, data):
        ''' 
        Generate an heterogeneous sphere from a list of columns along a meridian.
        Here, the haze and gas data are mixed in a single array.
        # Input
        - data (dict): Dictionnary with the following items: 
            - "nLevel" (integer): number of levels (not layers),
            - "nLat" (integer): number of latitudes,
            - "nLon" (integer): number of longitudes,
            - "nCoeff" (integer): number of quadrature points for the k-coeff,
            - "nWavelengths" (integer): number of wavelengths,
            - "nAngle" (optional, default=None, integer): number of angles in the phase functions (not required if using the builtin phase function),
            - "weights" (list or 2-D array (shape=(nWavelengths, nCoeff), float [])): the weigths of the nCoeff quadrature points,
            - "altitude (m)" (3-D array (shape=(nLevel, nLat, nLon), float [m])): altitudes,
            - "pressure (Pa)" (optional, 3-D array (shape=(nLevel, nLat, nLon), float [Pa])): pressures,
            - "latitude (°)" (1-D array (shape=(nLat), float [°])): latitudes,
            - "longitude (°)" (1-D array (shape=(nLon), float [°])): longitudes,
            - "scattering (m-1)" (5-D array (shape=(nWavelengths, nLevel, nLat, nLon, nCoeff), float [m-1])): scattering coefficients,
            - "absorption (m-1)" (5-D array (shape=(nWavelengths, nLevel, nLat, nLon, nCoeff), float [m-1])): absorption coefficients,
            - "temperature (K)" (3-D array (shape=(nLevel, nLat, nLon), float [K])): temperatures,
            - "angles (°)": (optional, 1-D array (shape=(nAngle), float [°])) angles for phase function,
            - "phaseFunc" or "assymetry": (1-D array (shape = (nWavelength, nLevel, nLat, nLon, nAngle) or (nWavelength, nLevel, nLat, nCoeff), float [])) phase functions or assymetry parameter,
            - "wavelength": (1-D array (shape = (nWavelengths), float [m]) wavelength,
            - "band low": (1-D array (shape = (nWavelengths), float [m]) lower boundary of wavelength band,
            - "band up": (1-D array (shape = (nWavelengths), float [m]) upper boundary of wavelength band
        '''

        ##############################################################
        # reading the input files and storing the data in dictionnary <data>
        # data = readingRoutine(*args)
        self.nTheta = data["nLat"]
        self.nPhi = data["nLon"]
        self.nLevel = data["nLevel"]
        self.nWavelength = data["nWavelengths"]
        self.nCoeff = data["nCoeff"]
        self.latitudes = data["latitude (°)"]
        self.longitudes = data["longitude (°)"]
        self.altitudes = data["altitude (m)"] + self.radius  # shape=(nLevel, nLat, nLon)
        self.wavelengths = data["wavelength"] / cst.nano

        if "pressure (Pa)" in data.keys(): self.pressure = np.tile(data["pressure (Pa)"][:,:,None], (1,1,self.nPhi))    # shape=(nLevel, nLat, nPhi)    

        coords = np.zeros((self.nLevel, self.nTheta, self.nPhi, 3))         # shape=(nLevel, nLat, nPhi, 3)
        for i,j,k in np.ndindex(self.nLevel,self.nTheta,self.nPhi):
            coords[i,j,k] = np.array([self.altitudes[i,j,k],
                                      self.latitudes[j],
                                      self.longitudes[k]])

        scattering = data["scattering (m-1)"] # shape=(nWavelengths, nLevel, nLat, nLon, nCoeff)
        absorption = data["absorption (m-1)"] # shape=(nWavelengths, nLevel, nLat, nLon, nCoeff)

        self.temperatureCells = data["temperature (K)"]

        ##############################################################
        phaseFunctionsIndices = - np.ones((self.nLevel, self.nTheta, self.nPhi))
        # writing the file containing the list of phase functions
        if "phaseFunc" in data.keys():
            angles = data["angles (°)"]
            count = 0
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(self.nLevel*self.nTheta*self.nPhi))
                wavelength = np.array(data["wavelength"]) / cst.nano
                for k,j,l in np.ndindex(self.nLevel,self.nTheta,self.nPhi):
                    phaseFunctions = np.array(data["phaseFunc"][:,k,j,l,:]).T
                    arr = [angles, wavelength, phaseFunctions]
                    fileName = f"{self.inputPath}phase_function_alt{k}_{j}_{l}.dat"
                    write_phase_function_decrete_dat(fileName, arr)
                    f.write(f"\n{fileName}")
                    phaseFunctionsIndices[k,j,l] = count
                    count += 1
        elif "assymetry" in data.keys():
            count = 0
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(self.nLevel*self.nTheta*self.nPhi))
                for k,j,l in np.ndindex(self.nLevel,self.nTheta,self.nPhi):
                    fileName = f"{self.inputPath}phase_function_alt{k}_{j}_{l}.dat"
                    self.__writeHGphaseFunction(fileName, data["assymetry"][:,k,j,l,0])
                    f.write(f"\n{fileName}")
                    phaseFunctionsIndices[k,j,l] = count
                    count += 1
        else: raise KeyError("phase function or assymetry parameter not found in the data dictionnary")



        self.nNodes = self.nLevel * self.nTheta * self.nPhi
        coords = coords.reshape((self.nNodes,3))
        node_coord = np.array([sphere2cart(coords[i]) for i in range(self.nNodes)]) # shape=(nNodes, 3)
        scattering = scattering.reshape((self.nWavelength, self.nNodes, self.nCoeff))
        absorption = absorption.reshape((self.nWavelength, self.nNodes, self.nCoeff))
        scattering = (data["weights"][:,None,:] * scattering[:,:,:]).sum(axis=2)
        temperatureNodes = self.temperatureCells.reshape(self.nNodes)
        phaseFunctionsIndices = phaseFunctionsIndices.reshape(self.nNodes).astype(int)

        if any(phaseFunctionsIndices == -1): raise ValueError("Wrong index for phase function: -1")

        cell_ids = Delaunay(node_coord)

        ##############################################################
        # generating the atmosphere dictionnary used by self.prepareInput()
        self.atmosphere = {
            "nodes coordinates": node_coord,
            "cells ids": cell_ids.simplices,
            "temperature": temperatureNodes,                    # shape = (nNodes)
            "bands low": np.array(data["band low"]) / cst.nano, # shape = (nWavelength)
            "bands up": np.array(data["band up"]) / cst.nano,   # shape = (nWavelength)
            "weights": data["weights"],                         # shape = (nWavelength, nCoeff)
            "absorption (gas)": absorption,                     # shape = (nWavelength, nNodes, nCoeff)
            "absorption (haze)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (gas)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (haze)": scattering,                    # shape = (nWavelength, nNodes)
            "phase func indices": phaseFunctionsIndices         # shape = (nNodes)
        }
        return

    def makeFromLMDZ(self, LMDZinput, LMDZouput, weights=None, keys=keysLMDZtitan_vi, wavelength=None, time=-1, hg=False, nAngle=181, phaseFunc=lambda g,theta: 1 + 3*g * np.cos(theta)):
        ''' 
        Generate an heterogeneous sphere from LMDZ outputs and inputs.
        # Input
        - LMDZinput (str): path to the netCDF file containing surface information, to be read
        - LMDZouput (str): path to the netCDF file containing atmosphere information, to be read
        - weights (optional, 1-D array (shape=(nWeight), float []): weightd of the Gaussian quadrature points for correlated-k data. \
            If not provided, assumes no correlated-k are used. It is not required if wavelengths are separted (see wavelengths)
        - keys (optional, default=htrdr.keysLMDZtitan_vi, dictionnary): dictionnary containing the keys to use for reading the output file \
            It must contain the following keys:
            - 'tsurf': (default = 'tsurf'),                 -> keys for surface temperature
            - 'temp': (default = 'temp'),                   -> keys for temperature
            - 'wavelength': (default = 'wavelength_vi'),    -> keys for visible wavelengths
            - 'ssa': (default = 'wv'),                      -> keys for single scatering albedo
            - 'extinction': (default = 'kv'),               -> keys for extinction coefficeint
            - 'assym': (default = 'gv'),                    -> keys for assymetry factor
            - 'geopotential': (default = 'pphi'),           -> keys for geopotential
            - 'altitude': (default = 'altitude'),           -> keys for altitude
            - 'latitude': (default = 'lat'),                -> keys for latitude
            - 'longitude': (default = 'lon')                -> keys for longitude
            - 'pressure': (default = 'p'),                  -> pressure
        - wavelengths (optional, dictionnary): dictionnary containing the wavelength bands data with. It must be composed of 1 sub-dictionnary for every band.
                - 'index' (dictionnary): dictionnary containing the data for that specific band ('index' is the index refering to the band in the GCM output file, e.g. 'v_23' for the last visible band in Titan GCM)
                    - 'wavelength' (float): central wavelength of the band (in m)
                    - 'low' (float): lower bound of the band (in m)
                    - 'up' (float): upper bound of the band (in m)
                    - 'weights' (optional, 1-D array (shape=(nWeights), float [])): the weights associated to the different k-correlated coefficents (if no k-coeff, omit the key)
        - time (optional, dafault=-1, int): time index to use, default is last
        - hg (optional, default=False, bool): Whether to use the Henyey-Greenstein phase function built in htrdr
        - nAngle (optional, default=181, int, if hg=True nAngle is omitted): number of angles to use in the discrete phase functions
        - phaseFunc (optional, default = 1 + g cos(theta), func, if hg=True phaseFunc is omitted): function to use to calculate the discrete phase function. \
            The function must take in first argument the asymetry factor and in second argument the angle (in rad). 
        # Note:
        If the surface temperature is not provided in the output file, it will be read from the input file
        '''
        
        self.time = time
        self.hg = hg
        self.nAngle = nAngle
        self.weights = weights

        self.__readLMDZintput(LMDZinput)
        self.__calculateTopoFromLMDZinput()
        self.__readLMDZoutput(LMDZouput, keys, wavelength=wavelength)

        self.__makeAtmosphereFromLMDZ(phaseFunc)
        self.__makeGroundFromLMDZ()

        return

    def __readLMDZintput(self, file):
        '''
        Extract the necessary data from the LMDZ input file to generate the ground
        '''
        data = nc.Dataset(file)
        self.elevation = np.array(data['ZMEA'][:], dtype=float)             # list of elevation (nCell)
        self.lat = np.array(data['latitude'][:], dtype=float)/cst.degree    # list of latitudes (nCell)
        self.lon = np.array(data['longitude'][:], dtype=float)/cst.degree   # list of longitudes (nCell)

        # list of nodes coordinate to recreate the topographic map
        self.groundMesh = np.array([self.elevation, self.lat, self.lon]).T

        # list of nodes cartesian coordinate for the interpolation (initial grid)
        cell_sph = np.array([self.elevation+self.radius, self.lat, self.lon]).T
        self.groundCellCoordGCM = np.array([sphere2cart(cell_sph[i,:]) for i in range(cell_sph.shape[0])])

        self.surfTemperature = np.array(data['tsurf'][:], dtype=float)      # list of surface temperature (nCell)
        self.albedo = np.array(data['albedodat'][:], dtype=float)           # list of albedo (nCell)
        return

    def __readLMDZoutput(self, file, keys, wavelength=None):
        '''
        Extract the necessary data from the LMDZ output file to generate the atmosphere.
        Also attempt to extract the surface temperature
        '''
        data = nc.Dataset(file)

        # extracting the latitudes and longitudes grids
        self.latitudes = np.array(data[keys['latitude']][:], dtype=float)
        self.longitudes = np.array(data[keys['longitude']][:], dtype=float)

        try:
            self.pressure = np.array(data[keys['pressure']][self.time,:,:,:], dtype=float)
        except:
            warnings.warn("No pressure data is available")
            self.pressure = None
        
        try:
            # calculation of the altitude of each cell based on the geopotential
            geopotential = np.array(data[keys['geopotential']][self.time,:,:,:], dtype=float) # geopotential g*z
            geopotentialSurf = np.array(data[keys['geopotentialSurf']][self.time,:,:], dtype=float) # geopotential g*z
            alt = (geopotential + geopotentialSurf) / self.gravity + self.radius

            # we gather the cells spherical coordinates
            self.atmosphereCellCoord = np.zeros(np.append(np.array(alt.shape), 3))
            for (k,i,j), val in np.ndenumerate(alt):
                self.atmosphereCellCoord[k,i,j,:] = np.array([val, self.latitudes[i], self.longitudes[j]])

        except IndexError:
            altitudes = np.array(data[keys['altitude']][:], dtype=float) * cst.kilo + self.radius
            altitudesGCM = altitudes[:,None, None] + self.topoMap[None,::-1,:]

            self.atmosphereCellCoord = np.zeros((len(altitudes), len(self.latitudes), len(self.longitudes), 3))
            for (k,i,j),alt in np.ndenumerate(altitudesGCM):
                self.atmosphereCellCoord[k,i,j,:] = np.array([alt, self.latitudes[i], self.longitudes[j]])


        self.nCell = np.prod(self.atmosphereCellCoord.shape[:-1])

        self.temperatureCells = np.array(data[keys['temp']][self.time,:,:,:], dtype=float)

        print("Extracting spectral data ...")


        if wavelength:
        
            wavelength = []
            bandsLow = []
            bandsUp = []
            asymetries = []
            absorption = []
            scattering = []
            weights = []
            for ind,dataBand in wavelength.items():

                wavelength.append(dataBand['wavelength'])
                bandsLow.append(dataBand['low'])
                bandsUp.append(dataBand['up'])

                singleScatAlb = np.array(data[f'ww{ind}'][self.time,:,:,:], dtype=float)#.reshape(self.nCell)

                if 'weights' in dataBand.keys():
                    weight = np.array(dataBand['weights'], dtype=float)
                    ext = np.array(data[f'kk{ind}'][self.time,:,:,:,:], dtype=float)#.reshape((self.nCell,len(weight)))
                else:
                    weight = np.array([1.])
                    ext = np.array(data[f'kk{ind}'][self.time,:,:,:,None], dtype=float) #.reshape((self.nCell,len(weight)))

                abso = ext *  (1 - singleScatAlb[:,None])
                scatt= ext * singleScatAlb[:,None]
                absorption.append(abso)
                scattering.append(scatt)
                weights.append(weight)

                asymetry = np.array(data[f'gg{ind}'][self.time,:,:,:], dtype=float).reshape(self.nCell)
                asymetries.append(asymetry)


            self.wavelengths = np.array(wavelength, dtype=float)
            self.bandsLow = np.array(bandsLow, dtype=float)
            self.bandsUp = np.array(bandsUp, dtype=float)
            self.weights = np.array(weights, dtype=float)                   # shape = (nWvl, nWeight)
            self.asymetries = np.array(asymetries, dtype=float)             # shape = (nWvl, nAlt, nLat, nLon)
            self.absorption = np.array(absorption, dtype=float)             # shape = (nWvl, nAlt, nLat, nLon, nWeight)
            self.scattering = np.array(scattering, dtype=float)             # shape = (nWvl, nAlt, nLat, nLon, nWeight)
            self.scattering = (weights[:,None,:] * scattering).sum(axis=-1) # shape = (nWvl, nAlt, nLat, nLon)
            self.nWavelength = len(wavelength)


        elif self.weights is not None: # if weights are given

            self.nWeight = len(self.weights)

            self.wavelengths = np.array(data[keys['wavelength']][::-1], dtype=float) * cst.micron
            self.nWavelength = len(self.wavelengths)

            self.bandsLow = np.zeros_like(self.wavelengths)
            self.bandsUp = np.zeros_like(self.wavelengths)

            self.bandsLow[1:] = (self.wavelengths[1:] + self.wavelengths[:-1]) / 2
            self.bandsUp[:-1] = self.bandsLow[1:]

            self.bandsLow[0] = (3 * self.wavelengths[0] - self.wavelengths[1]) / 2
            self.bandsUp[-1] = (3 * self.wavelengths[-1] - self.wavelengths[-2]) / 2

            self.weights = np.tile(self.weights, (self.nWavelength, 1))


            self.absorption = np.zeros((self.nWavelength, *self.atmosphereCellCoord.shape[:-1], self.nWeight))
            self.scattering = np.zeros_like(self.absorption)
            self.asymetries = np.array(data[keys['assym']][self.time,::-1,:,:,:], dtype=float)#.reshape((self.nWavelength,self.nCell))

            for weight in range(self.nWeight):

                num = "%02i" % (weight+1)

                singleScatAlb = np.array(data[f"{keys['ssa']}_{num}"][self.time,::-1,:,:,:], dtype=float) #.reshape((self.nWavelength,self.nCell))
                extinction = np.array(data[f"{keys['extinction']}_{num}"][self.time,::-1,:,:,:], dtype=float)#.reshape((self.nWavelength,self.nCell))
                self.absorption[:,:,:,:,weight] = extinction * ( 1 - singleScatAlb )
                self.scattering[:,:,:,:,weight] = extinction * singleScatAlb

            self.scattering = (self.weights[:,None,None,None,:] * self.scattering[:,:,:,:,:]).sum(axis=-1)


        else:

            self.wavelengths = np.array(data[keys['wavelength']][::-1], dtype=float) * cst.micron
            self.nWavelength = len(self.wavelengths)

            self.bandsLow = np.zeros_like(self.wavelengths)
            self.bandsUp = np.zeros_like(self.wavelengths)

            self.bandsLow[1:] = (self.wavelengths[1:] + self.wavelengths[:-1]) / 2
            self.bandsUp[:-1] = self.bandsLow[1:]

            self.bandsLow[0] = (3 * self.wavelengths[0] - self.wavelengths[1]) / 2
            self.bandsUp[-1] = (3 * self.wavelengths[-1] - self.wavelengths[-2]) / 2

            singleScatAlb = np.array(data[keys['ssa']][self.time,::-1,:,:,:], dtype=float) #.reshape((self.nWavelength,self.nCell))
            extinction = np.array(data[keys['extinction']][self.time,::-1,:,:,:], dtype=float)#.reshape((self.nWavelength,self.nCell))
            self.absorption = extinction * ( 1 - singleScatAlb )
            self.scattering= extinction * singleScatAlb
            self.asymetries = np.array(data[keys['assym']][self.time,::-1,:,:,:], dtype=float)#.reshape((self.nWavelength,self.nCell))


            self.nWeight = 1
            self.weights = np.ones((self.nWavelength,self.nWeight))
            self.absorption = self.absorption.reshape(np.append(self.absorption.shape, self.nWeight))

        # htrdr expects wavelengths in nm
        self.wavelengths /= cst.nano
        self.bandsLow /= cst.nano
        self.bandsUp /= cst.nano

        try:
            self.surfTemperature = np.array(data[keys['tsurf']][self.time,::-1,:], dtype=float)
            latInd = np.argmin(np.abs(self.latitudesGroundGCM[:,None] - self.groundMesh[None,:,1]), axis=0)
            lonInd = np.argmin(np.abs(self.longitudesGroundGCM[:,None] - self.groundMesh[None,:,2]), axis=0)
            self.surfTemperature = self.surfTemperature[latInd,lonInd]
        except:
            pass
        return

    def __calculateTopoFromLMDZinput(self):
        '''
        Stores the topographical map in a 2-D array (nLat,nLon)
        '''
        # extracting the list of latitudes
        self.latitudesGroundGCM, latIndices = np.unique(self.groundMesh[:,1], return_inverse=True)

        # extracting the list of longitudes
        self.longitudesGroundGCM, lonIndices = np.unique(self.groundMesh[:,2], return_inverse=True)

        # creating a topographic map to generate the ground
        self.topoMap = np.zeros((self.latitudesGroundGCM.shape[0],self.longitudesGroundGCM.shape[0]))
        indices = np.array([latIndices, lonIndices]).T
        for k, (i,j) in enumerate(indices): 
            self.topoMap[i,j] = self.groundMesh[k,0]

        self.topoMap[0,:]  = max(self.topoMap[0,:])     # south pole identic at all longitudes
        self.topoMap[-1,:] = max(self.topoMap[-1,:])    # north pole identic at all longitudes
        return

    def __makeGroundFromLMDZ(self):
        '''
        Define the new ground mesh and write the albedo files
        '''
        # we move the east half of the topo map to the left so the longitude scale goes from 0 to 360 instead of -180 to 180
        nl = len(self.longitudesGroundGCM)
        newTopo = np.zeros_like(self.topoMap)
        newTopo[:,:nl//2], newTopo[:,nl//2:] = self.topoMap[:,nl//2:] , self.topoMap[:,:nl//2]
        node_coord, cell_ids = topo_ground_mesh(self.radius, newTopo)

        # calculating the coordinates of the new cells centers
        nodeCoordSph = np.array([cart2sphere(node) for node in node_coord])
        self.groundCellCoord = np.array([sphere2cart(cell) for cell in np.mean(nodeCoordSph[cell_ids,:], axis=1)])

        # interpolating the temperature and albedo data
        nCell = len(cell_ids)
        albedo = interpolate(self.groundCellCoordGCM, self.albedo, self.groundCellCoord)
        temperature = interpolate(self.groundCellCoordGCM, self.surfTemperature, self.groundCellCoord)

        # writing the BRDF files
        wavelengthBound = np.array( [self.atmosphere['bands low'].min(), self.atmosphere['bands up'].max()] )
        with open(self.groundMaterialList, 'w') as f:
            f.write(f"\t {nCell} ")
            for k in range(nCell):
                brdfFile = f"{self.inputPath}material_{k}.dat"
                brdf = {
                    "kind": 'lambertian',
                    "albedo": np.array([albedo[k]]),
                    "bands": np.array([wavelengthBound]) / cst.nano
                }
                self.__writeBRDFfile(brdfFile, brdf)
                f.write(f"\n{brdfFile}")
        brdfIndices = np.arange(nCell)

        self.ground = {
            "nodes coordinates":node_coord,
            "cells ids":cell_ids,
            "temperature": temperature,
            "brdf indices": brdfIndices
        }
        return

    def __cells2nodes(self, cellCoord):
        '''
        Calculate the nodes coordinates from the cells coordinates
        # Input
        - cellCoord (3-D array (shape=(nAlt, nLat, nLon, 3), float [])): cells spherical coordinates

        # Output
        - nodeCoord (2-D array (shape=(nNodes, 3), float [])): nodes cartesian coordinates
        - cellIds (2-D array (shape=(nCell, ?), int [])): ids of the tetrahedrons forming each PCM cell
        - tetraIds (2-D array (shape=(nTetra, 4), int [])): ids of the nodes of each tetrahedron
        - cellIndexALL (2-D array (shape=(nCell, 3), int [])): Altitude, Latitude and Longitude indices of each cell
        '''
        altitudesLay = cellCoord[:,:,:,0]

        altSup = np.zeros_like(altitudesLay)
        altInf = np.zeros_like(altitudesLay)
        altSup[:-1,:,:] = altInf[1:,:,:] = 0.5 * (altitudesLay[1:,:,:] + altitudesLay[:-1,:,:])
        altSup[-1,:,:] = 2 * altitudesLay[-1,:,:] - altitudesLay[-2,:,:]
        altInf[0,:,:] = self.topoMap[::-1,:] + self.radius

        latN = np.zeros_like(self.latitudes)
        latS = np.zeros_like(self.latitudes)
        latN[1:] = latS[:-1] = 0.5 * (self.latitudes[1:] + self.latitudes[:-1])
        latN[0] = latN[1]
        latS[-1] = latS[-2]

        lonE = np.zeros_like(self.longitudes)
        lonW = np.zeros_like(self.longitudes)
        lonW[1:] = lonE[:-1] = 0.5 * (self.longitudes[1:] + self.longitudes[:-1])
        lonW[0] = lonE[-1] = 0.5 * (self.longitudes[-1] - self.longitudes[0])

        nodeCoord = []      # contains nodes cartesian coordinates
        tetraIds = []       # contains the ids of the nodes of each tetrahedron
        cellIds = []        # contains the ids of the tetrahedrons forming each PCM cell
        cellIndexALL = []   # contains the Altitude, Latitude and Longitude indices of each cell
        tetraALL = []

        self.newAssymetries = []
        self.newAbsorptions = []
        self.newScatterings = []
        self.newTemperatures = []

        tetraInds = []
        tetraInds.append(np.array([0,1,2,5]))
        tetraInds.append(np.array([0,2,3,7]))
        tetraInds.append(np.array([0,4,5,7]))
        tetraInds.append(np.array([2,5,6,7]))
        tetraInds.append(np.array([0,2,5,7]))

        polarTobs = np.arange(0, self.longitudes.shape[0])
        tetraIndsPoles = []
        tetraIndsPoles.append(np.array([0,2,3,4]))
        tetraIndsPoles.append(np.array([1,3,4,5]))
        tetraIndsPoles.append(np.array([0,1,3,4]))

        for k in range(cellCoord.shape[0]):
            # north pole
            cellId = []
            for n in polarTobs:
                start = len(nodeCoord)
                nodeCoord.append(sphere2cart([altInf[k,0,n], 90, 0]))
                nodeCoord.append(sphere2cart([altSup[k,0,n], 90, 0]))
                nodeCoord.append(sphere2cart([altInf[k,0,n], latS[0], lonW[n]]))
                nodeCoord.append(sphere2cart([altSup[k,0,n], latS[0], lonW[n]]))
                nodeCoord.append(sphere2cart([altInf[k,0,n], latS[0], lonE[n]]))
                nodeCoord.append(sphere2cart([altSup[k,0,n], latS[0], lonE[n]]))
                for _ in range(6):
                    self.newAssymetries.append(self.asymetries[:,k,0,n])
                    self.newAbsorptions.append(self.absorption[:,k,0,n,:])
                    self.newScatterings.append(self.scattering[:,k,0,n])
                    self.newTemperatures.append(self.temperatureCells[k,0,n])

                for tetraIndsPole in tetraIndsPoles:
                    cellId.append(len(tetraIds))
                    tetraIds.append(start + tetraIndsPole)
                    tetraALL.append(np.array([k,0,0]))
            cellIds.append(np.array(cellId))
            cellIndexALL.append(np.array([k,0,0]))

            # south pole
            cellId = []
            for n in polarTobs:
                start = len(nodeCoord)
                nodeCoord.append(sphere2cart([altInf[k,-1,n], -90, 0]))
                nodeCoord.append(sphere2cart([altSup[k,-1,n], -90, 0]))
                nodeCoord.append(sphere2cart([altInf[k,-1,n], latN[-1], lonW[n]]))
                nodeCoord.append(sphere2cart([altSup[k,-1,n], latN[-1], lonW[n]]))
                nodeCoord.append(sphere2cart([altInf[k,-1,n], latN[-1], lonE[n]]))
                nodeCoord.append(sphere2cart([altSup[k,-1,n], latN[-1], lonE[n]]))
                for l in range(6):
                    self.newAssymetries.append(self.asymetries[:,k,-1,n])
                    self.newAbsorptions.append(self.absorption[:,k,-1,n,:])
                    self.newScatterings.append(self.scattering[:,k,-1,n])
                    self.newTemperatures.append(self.temperatureCells[k,-1,n])

                for tetraIndsPole in tetraIndsPoles:
                    cellId.append(len(tetraIds))
                    tetraIds.append(start + tetraIndsPole)
                    tetraALL.append(np.array([k,len(self.latitudes)-1,0]))
            cellIds.append(np.array(cellId))
            cellIndexALL.append(np.array([k,len(self.latitudes)-1,0]))

        for k,i,j in np.ndindex(cellCoord.shape[:-1]):
            start = len(nodeCoord)
            if i == 0: continue # north pole already done
            elif i == len(self.latitudes)-1: continue # south pole already done
            nodeCoord.append(sphere2cart([altInf[k,i,j], latN[i], lonW[j]]))
            nodeCoord.append(sphere2cart([altInf[k,i,j], latN[i], lonE[j]]))
            nodeCoord.append(sphere2cart([altInf[k,i,j], latS[i], lonE[j]]))
            nodeCoord.append(sphere2cart([altInf[k,i,j], latS[i], lonW[j]]))
            nodeCoord.append(sphere2cart([altSup[k,i,j], latN[i], lonW[j]]))
            nodeCoord.append(sphere2cart([altSup[k,i,j], latN[i], lonE[j]]))
            nodeCoord.append(sphere2cart([altSup[k,i,j], latS[i], lonE[j]]))
            nodeCoord.append(sphere2cart([altSup[k,i,j], latS[i], lonW[j]]))
            for l in range(8):
                self.newAssymetries.append(self.asymetries[:,k,i,j])
                self.newAbsorptions.append(self.absorption[:,k,i,j,:])
                self.newScatterings.append(self.scattering[:,k,i,j])
                self.newTemperatures.append(self.temperatureCells[k,i,j])

            cellId = []
            for tetraInd in tetraInds:
                cellId.append(len(tetraIds))
                tetraIds.append(start + tetraInd)
                tetraALL.append(np.array([k,i,j]))
            cellIds.append(np.array(cellId))
            cellIndexALL.append(np.array([k,i,j]))

        nodeCoord = np.array(nodeCoord)
        tetraIds = np.array(tetraIds, dtype=int)
        cellIndexALL = np.array(cellIndexALL, dtype=int)
        self.tetraALL = np.array(tetraALL)

        self.newAssymetries = np.array(self.newAssymetries).T
        self.newAbsorptions = np.moveaxis(np.array(self.newAbsorptions), 0, 1)
        self.newScatterings = np.array(self.newScatterings).T

        print(self.newAssymetries.shape)
        print(self.newAbsorptions.shape)
        print(self.newScatterings.shape)

        return nodeCoord, cellIds, tetraIds, cellIndexALL

    def __makeAtmosphereFromLMDZ(self, phaseFunc):
        '''
        Define the new atmosphere mesh and write the phase function files
        '''
        node_coord, self.cellIds, cell_ids, self.cellIndices = self.__cells2nodes(self.atmosphereCellCoord)
        self.nNodes = len(node_coord)


        print("Writing phase function files ...")
        assymetry = self.newAssymetries
        if self.hg:
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(self.nNodes))
                for k in tqdm.tqdm(range(self.nNodes)):
                    ##############################################################
                    # writing the file containing the list of phase functions
                    fileName = f"{self.inputPath}phase_function_node_{k}.dat"
                    self.__writeHGphaseFunction(fileName, assymetry[:,k])
                    f.write(f"\n{fileName}")
        else:
            angles = np.linspace(0, 180, self.nAngle)
            phaseFunctions = phaseFunc(assymetry[:,:,None], angles[None,:]*cst.degree)
            with open(self.phaseFunctionList, 'w') as f:
                f.write(str(self.nNodes))
                for k in tqdm.tqdm(range(self.nNodes)):
                    ##############################################################
                    # writing the file containing the list of phase functions
                    phase = phaseFunctions[:,k,:].T  # shape = (nAngle, nWavelength)
                    arr = [angles, self.wavelength, phase]
                    fileName = f"{self.inputPath}phase_function_node_{k}.dat"
                    write_phase_function_decrete_dat(fileName, arr)
                    f.write(f"\n{fileName}")

        phaseFunctionsIndices = np.arange(self.nNodes)

        ##############################################################
        # generating the atmosphere dictionnary used by self.writeInputs() and self.writeVTKfiles()
        self.atmosphere = {
            "nodes coordinates":node_coord,
            # "cells ids":cell_ids.simplices,
            "cells ids":cell_ids,
            # "temperature": self.temperatureCells.reshape(self.nCell),         # shape = (nNodes)
            "temperature": self.newTemperatures,            # shape = (nNodes)
            "bands low": self.bandsLow,                                         # shape = (nWavelength)
            "bands up": self.bandsUp,                                           # shape = (nWavelength)
            "weights": self.weights,                                            # shape = (nWavelength, nCoeff)
            "absorption (gas)": self.newAbsorptions,                            # shape = (nWavelength, nNodes, nCoeff)
            "absorption (haze)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (gas)": np.zeros((self.nWavelength, self.nNodes)),
            "scattering (haze)": self.newScatterings                ,           # shape = (nWavelength, nNodes)
            # "absorption (gas)": self.absorption.reshape((self.nWavelength,self.nNodes,self.nWeight)),# shape = (nWavelength, nNodes, nCoeff)
            # "absorption (haze)": np.zeros((self.nWavelength, self.nNodes)),
            # "scattering (gas)": np.zeros((self.nWavelength, self.nNodes)),
            # "scattering (haze)": self.scattering.reshape((self.nWavelength,self.nNodes)),         # shape = (nWavelength, nNodes)
            "phase func indices": phaseFunctionsIndices                                             # shape = (nNodes)
        }
        return

    def writeInputs(self, octree_def="512", opthick="1", nthOctree=8, procOctree="master", octreeFile=""):
        '''
        Write the binary input files for htrdr-planets and precalculate octrees
        # Inputs:
        - octree_def (optional, default=512, int): maximal defintion of the octree grid
        - opthick (optional, default=1, float []): optical thickness threshold to assess the merge of cells
        - nthOctree (optional, default=8, int): number of threads to use for octree computation
        - procOctree (optional, default='master', str): which process must realize the octree calculation (useless if no storage). Put to 'all' if the processes does not share the disk space.
        - octreeFile (optional, dafault='', str): file name to store the octree. If left empty, octrees are not stored on disk
        '''
        self.writeInputGround()
        self.writeInputAtmosphere()

        self.octreeDef = octree_def
        self.opthick = opthick
        self.nthOctree = nthOctree
        self.procOctree = procOctree

        # if the octrees are stored in memory, there is no need for precalculing them...
        if octreeFile:
            self.octreeFile = f"{self.outputPath}{octreeFile}"
            self.__precalculateOctrees() 
        else: self.octreeFile = ""

        return

    def writeInputGround(self):
        '''Write the ground binary input files for htrdr-planets'''
        # write mesh
        
        print('generating surface mesh bin file...')
        write_binary_file_grid(self.groundGeometry,4096,self.ground["nodes coordinates"],self.ground["cells ids"])
        print('bin generation completed.')

        # write properties

        print('generating surface properties bin file...')
        write_binary_file_surface_properties(self.groundSurfaceProperties,4096,self.ground["cells ids"],self.ground["temperature"],self.ground["brdf indices"])
        print('bin generation completed.')
        return

    def writeInputAtmosphere(self):
        '''Write the atmosphere binary input files for htrdr-planets'''
        # write mesh
        
        print('generating atmosphere mesh bin file...')
        write_binary_file_grid(self.atmosphereGeometry,4096,self.atmosphere["nodes coordinates"],self.atmosphere["cells ids"])
        print('bin generation completed.')

        # write properties

        print('generating gas temperature bin file...')
        write_binary_file_T(self.gasTempearture,4096,self.atmosphere["temperature"])
        print('bin generation completed.')

        print('generating gas properties bin file...')
        write_binary_file_k(self.gasOpticalProperties,4096,self.atmosphere["bands low"],self.atmosphere["bands up"],self.atmosphere["weights"],self.atmosphere["absorption (gas)"], self.atmosphere["scattering (gas)"])
        print('bin generation completed.')

        print('generating haze properties bin file...')
        write_binary_file_k_haze(self.particleOpticalProperties,4096,self.atmosphere["bands low"],self.atmosphere["bands up"], self.atmosphere["absorption (haze)"], self.atmosphere["scattering (haze)"])
        print('bin generation completed.')

        print('generating haze phase function bin file...')
        write_binary_file_phase_function_het(self.phaseFunctionFile,4096,self.atmosphere["phase func indices"])
        print('bin generation completed.')
        return

    def writeInputsParallel(self):
        ''' doesn't work ! use writeInputs()'''
        threads = []
        threads.append(Thread(target=write_binary_file_grid, args=(self.groundGeometry,4096,self.ground["nodes coordinates"],self.ground["cells ids"])))
        threads.append(Thread(target=write_binary_file_grid , args=(self.atmosphereGeometry,4096,self.atmosphere["nodes coordinates"],self.atmosphere["cells ids"])))
        threads.append(Thread(target=write_binary_file_surface_properties , args=(self.groundSurfaceProperties,4096,self.ground["cells ids"],self.ground["temperature"],self.ground["brdf indices"])))
        threads.append(Thread(target=write_binary_file_T , args=(self.gasTempearture,4096,self.atmosphere["temperature"])))
        threads.append(Thread(target=write_binary_file_k , args=(self.gasOpticalProperties,4096,self.atmosphere["bands low"],self.atmosphere["bands up"],self.atmosphere["weights"],self.atmosphere["absorption"],np.zeros((self.nWavelength, self.nNodes)))))
        threads.append(Thread(target=write_binary_file_k_haze , args=(self.particleOpticalProperties,4096,self.atmosphere["bands low"],self.atmosphere["bands up"],np.zeros((self.nWavelength, self.nNodes)),self.atmosphere["scattering"])))
        threads.append(Thread(target=write_binary_file_phase_function_het , args=(self.phaseFunctionFile,4096,self.atmosphere["phase func indices"])))
        
        for th in threads:
            th.start()
        
        for th in threads:
            th.join()
        return

    def writeVTKfiles(self):
        '''Write the VTK files for view in paraview'''
        self.writeVTKfilesAtmosphere()
        self.writeVTKfilesGround()
        return

    def writeVTKfilesAtmosphere(self):
        '''
        Write the atmosphere VTK files for view in paraview
        '''
        self.atmosphereGeometryVTK = f'{self.vtkPath}atmosphereGeometry.vtk'
        self.atmosphereTemperatureVTK = f'{self.vtkPath}atmosphereTemperature.vtk'
        self.gasOpticalPropertiesVTK = [f'{self.vtkPath}absorptionCoefficients_{i}.vtk' for i in range(self.nWavelength)]
        self.particleOpticalPropertiesVTK = [f'{self.vtkPath}scatteringCoefficients_{i}.vtk' for i in range(self.nWavelength)]

        try:
            os.mkdir(self.vtkPath)
        except FileExistsError:
            pass

        print("generating Atmosphere geometry VTK file ...")
        write_vtk_tetr(self.atmosphere["nodes coordinates"],self.atmosphere["cells ids"], self.atmosphereGeometryVTK)
        print("VTK file written.")

        print("generating Temperature VTK file ...")
        attach_values_to_nodes(self.atmosphereGeometryVTK, self.atmosphere["temperature"], self.atmosphereTemperatureVTK)
        print("VTK file written.")

        print("generating Scattering and Absorption properties VTK file ...")
        for i in range(self.nWavelength):
            # print(len(self.atmosphere["scattering"][i,:]))
            attach_values_to_nodes(self.atmosphereGeometryVTK, self.atmosphere["scattering (haze)"][i,:], self.particleOpticalPropertiesVTK[i])
            # print((self.atmosphere["weights"][None,None,:] * self.atmosphere["absorption"][:,:,:]).sum(axis=2)[i,:].shape)
            attach_values_to_nodes(self.atmosphereGeometryVTK, (self.atmosphere["weights"][:,None,:] * self.atmosphere["absorption (gas)"][:,:,:]).sum(axis=2)[i,:], self.gasOpticalPropertiesVTK[i])
        print("VTK file written.")
        return

    def writeVTKfilesGround(self):
        '''
        Write the ground VTK files for view in paraview
        '''
        self.groundGeometryOBJ = f'{self.vtkPath}groundGeometry.obj'
        self.groundGeometryVTK = f'{self.vtkPath}groundGeometry.vtk'
        self.groundTemperatureVTK = f'{self.vtkPath}groundTemperature.vtk'

        try:
            os.mkdir(self.vtkPath)
        except FileExistsError:
            pass

        print("generating Ground geometry OBJ file ...")
        write_obj(self.ground["nodes coordinates"],self.ground["cells ids"], self.groundGeometryOBJ)
        print("OBJ file written.")

        print("generating Ground geometry VTK file ...")
        write_vtk(self.ground["nodes coordinates"],self.ground["cells ids"], self.groundGeometryVTK)
        print("VTK file written.")

        print("generating Surface Temperature VTK file ...")
        attach_values_to_cells(self.groundGeometryVTK, self.ground["temperature"], self.groundTemperatureVTK)
        print("VTK file written.")
        return

    def __writeBRDFfile(self, filename, brdf):
        '''
        Generate the brdf file from the albedo data.
        This function is called from the makeGround...() methods.
        # Input
        - filename (str): path to the file to be written
        - brdf (dictionnary): contains the surface reflectivity data with the following items:
            - "kind" (str = "lambertian" or "specular"): kind of brdf function to use
            - "albedo" (list or numpy 1-D array (shape=(nWavelength), float [])): wavelength dependent surface albedos (should match the size of "wavelengths" or "bands")
            - "wavelengths" or "bands":
                - if "wavelengths" (list or numpy 1-D array (shape=(nWavelength), float [m]) wavelengths where the albedo is defined
                - if "bands" (numpy 2-D array (shape=(nWavelength,2), float [m])) wavelengths bands where the albedo is defined, the values corresponds to the bands limits
        '''
        with open(filename, 'w') as f:
            if "wavelengths" in brdf.keys():
                keySpec = "wavelengths"
            elif "bands" in brdf.keys():
                keySpec = "bands"
            else:
                raise KeyError(f"error in brdf keys \
                                need to one of ('kind', 'albedo', 'wavelengths')")
            f.write(f"{keySpec} \t {len(brdf[keySpec])} \n")
            for wvl,alb in zip(brdf[keySpec], brdf["albedo"]):
                if keySpec == "wavelengths":
                    f.write(f"{wvl / cst.nano} \t {brdf['kind']} \t {alb} \n")
                else:
                    f.write(f"{wvl[0] / cst.nano} \t {wvl[1] / cst.nano} \t {brdf['kind']} \t {alb} \n")
        return

    def __writeHGphaseFunction(self, fileName, asymetries):
        '''
        Write the phase function file when using Henyey-Greenstein builtin phase function
        # Input
        - filename (str): path to the file to be written
        - asymetries (list or 1-D array (shape=(nWavelength), float [nm])) : assymetry factors
        '''
        with open(fileName, 'w') as f:
            f.write(f"wavelengths {self.nWavelength}\n")
            for i, wave in enumerate(self.wavelengths):
                f.write(f"{wave}  HG  {asymetries[i]}\n")

    def __precalculateOctrees(self):
        '''
        Generate the octree file for the whole calculation based on the loaded geometry.
        '''

        # Define string variables
        gas = f"mesh={self.atmosphereGeometry}"
        gas += f":ck={self.gasOpticalProperties}"
        gas += f":temp={self.gasTempearture}"
        
        haze = "name=haze"
        haze += f":mesh={self.atmosphereGeometry}"
        haze += f":radprop={self.particleOpticalProperties}"
        haze += f":phasefn={self.phaseFunctionList}"
        haze += f":phaseids={self.phaseFunctionFile}"
        
        ground = "name=surface"
        ground += f":mesh={self.groundGeometry}"
        ground += f":prop={self.groundSurfaceProperties}"
        ground += f":brdf={self.groundMaterialList}"

        ##############
        
        image = "def=1x1:spp=1"

        source = f"lon=0:lat=0:dst={1000*self.radius}:radius=1:temp=1"
        
        spectral = f"sw={self.atmosphere['bands low'].min()},{self.atmosphere['bands up'].max()}"

        octree = f"def={self.octreeDef}"
        octree += f":nthreads={self.nthOctree}"
        octree += f":tau={self.opthick}"
        if self.octreeFile:
            octree += f":storage={self.octreeFile}"
            octree += f":proc={self.procOctree}"

        command = f"htrdr-planets -v -N -f \
                -a {haze} \
                -G {ground} \
                -g {gas} \
                -s {spectral} \
                -S {source} \
                -b {octree} \
                -i {image}"

        try:
            subprocess.run(command, shell=True, check=True)
        except:
            os.remove(self.octreeFile)
            subprocess.run(command, shell=True, check=True)
        return

    def cleanInputs(self):
        command = f"rm -r -f {self.inputPath}"
        subprocess.run(command, shell=True, check=True)
        return


if __name__ == "__main__":
    data = Data(radius=2575 * cst.kilo, nPhi=32)
    nwvl = 20
    nlat = 40
    nlon = 50
    brdf = {
        "kind":"lambertian",
        "albedo": 0.7 * np.ones((nwvl,nlat,nlon)),
        "latitude": np.linspace(-90, 90, nlat),
        "longitude": np.linspace(-180, 180, nlon),
        "wavelengths": np.linspace(300, 40000, nwvl)*cst.nano,
    }
    tsurf = np.linspace(90, 95, nlat*nlon).reshape((nlon,nlat)).T
    data.makeGroundFrom3D(tsurf, brdf)

    data.writeVTKfilesGround()
    data.writeInputGround()
