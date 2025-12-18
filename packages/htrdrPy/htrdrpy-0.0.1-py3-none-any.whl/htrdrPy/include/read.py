#####################################################################
# Copyright (C) Observatoire de Paris - PSL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>. 
#####################################################################

import numpy as np 
import math

'''
Read brut data 
'''
def read_haze_albedo_file(file_path):
    Altitude = []
    Wavelength = []
    albedo = []

    with open(file_path, 'r', encoding='latin-1') as file:
        print(f'Reading file: {file_path}')
        lines = file.readlines()
        # read the first line
        line = lines[0]
        line = line.strip()
        values = line.split()
        entry = {
            Altitude.append(float(values[1])),
            Altitude.append(float(values[2])),
            Altitude.append(float(values[3])),
            Altitude.append(float(values[4])),
                }

        # read the rests
        for line in lines[1:]:
            line = line.strip()
            values = line.split()
            entry = {
                Wavelength.append(float(values[0])),
                albedo.append([float(values[1]),float(values[2]),float(values[3]),float(values[4])]),
            }
    return np.array(Altitude),np.array(Wavelength),np.array(albedo)
 
def read_huygens_file(file_path):
    Altitude = []
    Pressure = []
    Temperature = []
    
    with open(file_path, 'r', encoding='latin-1') as file:
        print(f'Reading file: {file_path}')
        lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#'):
                continue
            
            values = line.split()
            if len(values) == 3:
                entry = {
                    Altitude.append(float(values[0])),
                    Pressure.append(float(values[1])),
                    Temperature.append(float(values[2])),
                }
            
    
    return Altitude,Pressure,Temperature

def read_huygens_file(file_path):
    Altitude = []
    Pressure = []
    Temperature = []
    
    with open(file_path, 'r', encoding='latin-1') as file:
        print(f'Reading file: {file_path}')
        lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#'):
                continue
            
            values = line.split()
            if len(values) == 3:
                entry = {
                    Altitude.append(float(values[0])),
                    Pressure.append(float(values[1])),
                    Temperature.append(float(values[2])),
                }
            
    
    return Altitude,Pressure,Temperature

def read_temp_profile(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        print(f'Reading file: {file_path}')
        lines = file.readlines()
        Pressure = []
        Temperature = []
        for line in lines:
            line = line.strip()
            
            if line.startswith('P'):
                continue
            
            values = line.split()
            entry = {
                Pressure.append(float(values[0])),
                Temperature.append(float(values[1])),
                }

    return np.array(Pressure),np.array(Temperature)

def read_abondance_file(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        print(f'Reading file: {file_path}')
        lines = file.readlines()
        Pressure = []
        Vratio = []
        for line in lines:
            line = line.strip()
            
            if line.startswith('P'):
                continue
            
            values = line.split()
            entry = {
                Pressure.append(float(values[0])),
                Vratio.append(float(values[1])),
                }

    return Pressure,Vratio

def read_haze_q_file(file_path):
    Altitude = []
    Pressure = []
    q = []
    Temperature = []
    
    with open(file_path, 'r', encoding='latin-1') as file:
        print(f'Reading file: {file_path}')
        lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#'):
                continue
            
            values = line.split()
            if len(values) == 7:
                entry = {
                    Altitude.append(float(values[0])),
                    Pressure.append(float(values[1])),
                    q.append(float(values[2])),
                    Temperature.append(float(values[-1])),
                }
            
    
    return Altitude,Pressure,q,Temperature


def read_haze_kext_file(file_path):
    Altitude = []
    Kext = []
    
    with open(file_path, 'r', encoding='latin-1') as file:
        print(f'Reading file: {file_path}')
        next(file)  # Skip the first row
        lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            
            values = line.split()
            entry = {
                Altitude.append(float(values[0])),
                Kext.append(float(values[1])),
            }
    
    return np.array(Altitude)*1000,np.array(Kext)/1E3 # originaly km, 1/km

def read_temperature_file(file_path):
    Altitude = []
    Pressure = []
    Temperature = []
    
    with open(file_path, 'r', encoding='latin-1') as file:
        print(f'Reading file: {file_path}')
        lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#'):
                continue
            
            values = line.split()
            if len(values) == 6:
                entry = {
                    Altitude.append(float(values[0])),
                    Pressure.append(float(values[1])),
                    Temperature.append(float(values[2])),
                }
            
    
    return Altitude,Pressure,Temperature


def read_properties_file(kfile):
    with open(kfile, 'r') as f:
        print(f'Reading file: {kfile}')

        # Metadata
        NP, NT_perP, Nlambda, Nq = map(int, f.readline().split())

        # get pressure and temperatures
        Ncol = 5

        #initial P
        P = -1*np.ones(NP)
        #read P
        for i in range(math.ceil(NP/Ncol)):
            value = f.readline().split()
            for j in range(len(value)):
                P[j+i*Ncol] = float(value[j])

        #initial T
        T = -1*np.ones((NP,NT_perP))
        #read T
        for i in range(math.ceil(NT_perP*NP/Ncol)):
            value = f.readline().split()
            values = []
            for j in range(len(value)):
                values.append(float(value[j]))
            T[i,:] = np.array(values)

        # Reading quadrature abscissas
        g = np.array([float(val) for _ in range(math.ceil(Nq/5)) for val in f.readline().split()[:2]])

        # Reading quadrature weights
        w = np.array([float(val) for _ in range(math.ceil(Nq/5)) for val in f.readline().split()[:5]])
       
        # Normalization
        sum_w = np.sum(w)
        if np.abs(sum_w - 1.0) >= 1e-2:
            raise ValueError('Sum of weights is too different from 1.')
        w = w / sum_w

        # Read values of the wavelength
        Lambda = []
        idx_temp = -1
        c = -1*np.ones((Nlambda,NP,NT_perP,Nq)) 
        for i in range(Nlambda):
            for j in range(NP):
                for k in range(NT_perP):
                    # read lambda
                    value = f.readline().split()
                    if (idx_temp != i):
                        Lambda.append(float(value[0]))
                        idx_temp = i
                    # read c
                    values = []
                    for ii in range(math.ceil(Nq/Ncol)):
                        value = f.readline().split()
                        for jj in range(len(value)):
                            values.append(value[jj])
                    c[i,j,k,:] = np.array(values)

    return np.array(Lambda),np.array(P),np.array(T),np.array(c),np.array(w)

def read_haze_phase_function_file(file_path):
    angle = []
    Wavelength = []
    phi = []

    with open(file_path, 'r', encoding='latin-1') as file:
        print(f'Reading file: {file_path}')
        lines = file.readlines()
        # read the first line -> wavelength
        line = lines[0]
        line = line.strip()
        values = line.split()
        for i in range(len(values)):
            Wavelength.append(float(values[i])),

        # read the rests
        for line in lines[1:]:
            line = line.strip()
            values = line.split()
            angle.append(float(values[0])),
            temp = []
            for i in range(1,len(values)):
                temp.append(float(values[i]))
            phi.append(temp)

    return np.array(angle),np.array(Wavelength),np.array(phi)

def read_haze_albedo_file(file_path):
    Altitude = []
    Wavelength = []
    albedo = []

    with open(file_path, 'r', encoding='latin-1') as file:
        print(f'Reading file: {file_path}')
        lines = file.readlines()
        # read the first line
        line = lines[0]
        line = line.strip()
        values = line.split()
        entry = {
            Altitude.append(float(values[1])),
            Altitude.append(float(values[2])),
            Altitude.append(float(values[3])),
            Altitude.append(float(values[4])),
                }

        # read the rests
        for line in lines[1:]:
            line = line.strip()
            values = line.split()
            entry = {
                Wavelength.append(float(values[0])),
                albedo.append([float(values[1]),float(values[2]),float(values[3]),float(values[4])]),
            }
    return np.array(Altitude),np.array(Wavelength),np.array(albedo)
 
