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
import scipy.constants as sc
#######
#DEBUG
#import matplotlib.pyplot as plt
#######

'''
Interpolations
'''

def find_closest_index(array, value1):
    """
    Find the index of the closest value to value1 in array.
    
    Parameters:
    array (list or numpy array): The array in which to search.
    value1 (float): The value to find the closest to.
    
    Returns:
    int: The index of the closest value.
    """
    array = np.array(array)
    absolute_difference_array = np.abs(array - value1)
    closest_index = np.argmin(absolute_difference_array)
    return closest_index

def interpolate_c_array(prop,P_layer,T_layer):

    N_lambda = np.shape(prop[3])[0]
    N_qt = np.shape(prop[3])[3]
    N_layer = len(P_layer)
    c_arr = -1*np.ones((N_lambda,N_layer,N_qt))

    # initialize
    P_close = -1*np.ones((4)) 
    T_close = -1*np.ones((4)) 
    c_close = -1*np.ones((4,16))

    for i in range(N_lambda):
        for j in range(N_layer):
            # find 4 clostest points 
            Pid,Tid = find_nearest(P_layer[j],T_layer[j],prop)
            P_close = prop[1][Pid]
            T_close[0] = prop[2][Pid[0],Tid[0]]
            T_close[1] = prop[2][Pid[1],Tid[1]]
            T_close[2] = prop[2][Pid[2],Tid[2]]
            T_close[3] = prop[2][Pid[3],Tid[3]]

            # find c
            c_close[0,:] = np.copy(prop[3][i,Pid[0],Tid[0],:])
            c_close[1,:] = np.copy(prop[3][i,Pid[1],Tid[1],:])
            c_close[2,:] = np.copy(prop[3][i,Pid[2],Tid[2],:])
            c_close[3,:] = np.copy(prop[3][i,Pid[3],Tid[3],:])
            # linear interpolation of [ln(P) T]
            for k in range(16):
                stat_pt = np.array([math.log(P_layer[j]),T_layer[j]])
                ref_pt = np.array([[math.log(P_close[0]),T_close[0]],[math.log(P_close[1]),T_close[1]],[math.log(P_close[2]),T_close[2]],[math.log(P_close[3]),T_close[3]]])
                c_arr[i,j,k] = interpolate_c_point(stat_pt,ref_pt,c_close[:,k])
    return c_arr

def get_pdf_cdf_from_data(input_data,input_bins):
    #pdf,bins = np.histogram(input_data,density=True,bins=input_bins)
    pdf,bins = np.histogram(input_data,bins=input_bins)
    cdf = np.cumsum(pdf)*(bins[1]-bins[0])
    return pdf,cdf

def interpolate_gaska(ka1,ka2,weights):
    '''
    ka, ka have same dimension and same weights
    '''
    N_lambda = len(ka1[:,0,0])
    N_layer = len(ka1[0,:,0])
    N_q = len(weights)
    g = np.cumsum(weights)

    ka_gas_ori = -1*np.ones((N_lambda,N_layer,N_q*N_q))
    ka_gas_inter = -1*np.ones((N_lambda,N_layer,N_q))

    weights_gas = np.ones(N_q*N_q) * -1
    idx = 0
    for i in range(N_q):
        for j in range(N_q):
            weights_gas[idx] = weights[i]*weights[j]
            idx += 1


    for i in range(N_lambda):
        for j in range(N_layer):
            idx = 0
            tmp_ka_gas = -1*np.ones(N_q*N_q)
            # calculate combined ka, N = N_q*N_q
            for k1 in range(N_q):
                for k2 in range(N_q):
                    tmp_ka_gas[idx] = ka1[i,j,k1] + ka2[i,j,k2]
                    idx += 1
            # ka with Nq*Nq quadrature points
            ka_gas_ori[i,j,:] = np.copy(tmp_ka_gas)

            # interpolate Nq*Nq quadrature points to Nq quadrature points 
            idx = np.argsort(tmp_ka_gas)
            sorted_ka = tmp_ka_gas[idx]
            sorted_weights = weights_gas[idx]
            sorted_g = np.cumsum(sorted_weights)
            ka_gas_inter[i,j,:] = np.copy(np.interp(g,sorted_g,sorted_ka))

    #########
    #Debug interpolation
    #N1 = 5
    #N2 = 30
    #idx = np.argsort(ka_gas_ori[N1,N2,:])
    #sorted_ka = ka_gas_ori[N1,N2,idx]
    #sorted_weights = weights_gas[idx]
    #sorted_g = np.cumsum(sorted_weights)

    #plt.figure()
    #plt.plot(ka_gas_ori[N1,N2,:],weights_gas,'b.')
    #plt.plot(sorted_ka,sorted_weights,'r.')
    #plt.xscale('log') 
    #plt.figure()
    #plt.plot(sorted_g,sorted_ka,'b.')
    #plt.plot(g,ka_gas_inter[N1,N2,:],'r.')
    #plt.yscale('log') 
    #plt.show()
    #########
    return ka_gas_inter

def calculate_Alt_from_P_T(P_top,P_bottom,N_level,P,T,P_ch4,xch4):

    N_layer = N_level - 1
    P_level = np.exp(np.linspace(math.log(P_bottom),math.log(P_top),N_level))
    P_layer = np.exp(np.log(P_level)[:-1]+np.diff(np.log(P_level))/2)

    # interpolate x_ch4
    xch4_layer = np.interp(np.log(P_layer),np.log(np.sort(P_ch4)),np.sort(xch4))

    #########
    ##Debug interpolation
    #plt.figure()
    #plt.plot(xch4,P_ch4,'b.')
    #plt.plot(xch4_level,P_level,'r.')
    #plt.yscale('log')
    #plt.show()
    #########

    # interpolate T_level
    T_layer = np.interp(np.log(P_layer),np.log(P[::-1]),T[::-1])

    # interpolate ml_level
    # NOTE xN2, xH2, xAr are constant
    xn2 = 0.9425
    xh2 = 0.001
    xar = 0
    ml_layer = 16.043 * xch4_layer + (28.0134 * xn2 + 2.0158 * xh2 + 35.9675 * xar) * (1-xch4_layer)/(1-xch4_layer[0])

    # some constants
    R_titan = 2.575E6 
    R = 8.3144598
    ml = 28
    g0 = 1.354

    # first layter, use g0 -> H
    Alt_level = np.ones(N_level)*-1
    Alt_level[0] = 0

    # calculate Alt_level
    g_level = g0
    for i in range(N_layer):
        H = 1000 * R * T_layer[i]/(ml_layer[i] * g_level)
        Alt_level[i+1] = Alt_level[i] - H * math.log(P_level[i+1]/P_level[i])
        g_layer = g0 * (R_titan * R_titan)/((R_titan+(Alt_level[i+1]+Alt_level[i])/2) * (R_titan+(Alt_level[i+1]+Alt_level[i])/2))
        H = 1000 * R * T_layer[i]/(ml_layer[i] * g_layer)
        Alt_level[i+1] = Alt_level[i] - H * math.log(P_level[i+1]/P_level[i])
        g_level = g0 * (R_titan * R_titan)/((R_titan+Alt_level[i+1]) * (R_titan+Alt_level[i+1]))
    return Alt_level, P_layer, T_layer

def calculate_Alt_PTlevel_from_P_T(P_top,P_bottom,N_level,P,T,P_ch4,xch4):
    '''
    This function calculate P_level, Alt_level, T_level from 
    user defined P_top,P_bottom, N_level, P,T, P_ch4, xch4
    '''

    N_layer = N_level - 1
    P_level = np.exp(np.linspace(math.log(P_bottom),math.log(P_top),N_level))
    P_layer = np.exp(np.log(P_level)[:-1]+np.diff(np.log(P_level))/2)

    # interpolate x_ch4
    xch4_layer = np.interp(np.log(P_layer),np.log(np.sort(P_ch4)),np.sort(xch4))

    #########
    ##Debug interpolation
    #plt.figure()
    #plt.plot(xch4,P_ch4,'b.')
    #plt.plot(xch4_level,P_level,'r.')
    #plt.yscale('log')
    #plt.show()
    #########

    # interpolate T_level
    T_layer = np.interp(np.log(P_layer),np.log(P[::-1]),T[::-1])
    T_level = np.interp(np.log(P_level),np.log(P[::-1]),T[::-1])

    # interpolate ml_level
    # NOTE xN2, xH2, xAr are constant
    xn2 = 0.9425
    xh2 = 0.001
    xar = 0
    ml_layer = 16.043 * xch4_layer + (28.0134 * xn2 + 2.0158 * xh2 + 35.9675 * xar) * (1-xch4_layer)/(1-xch4_layer[0])

    # some constants
    R_titan = 2.575E6 
    R = 8.3144598
    ml = 28
    g0 = 1.354

    # first layter, use g0 -> H
    Alt_level = np.ones(N_level)*-1
    Alt_level[0] = 0

    # calculate Alt_level
    g_level = g0
    for i in range(N_layer):
        H = 1000 * R * T_layer[i]/(ml_layer[i] * g_level)
        Alt_level[i+1] = Alt_level[i] - H * math.log(P_level[i+1]/P_level[i])
        g_layer = g0 * (R_titan * R_titan)/((R_titan+(Alt_level[i+1]+Alt_level[i])/2) * (R_titan+(Alt_level[i+1]+Alt_level[i])/2))
        H = 1000 * R * T_layer[i]/(ml_layer[i] * g_layer)
        Alt_level[i+1] = Alt_level[i] - H * math.log(P_level[i+1]/P_level[i])
        g_level = g0 * (R_titan * R_titan)/((R_titan+Alt_level[i+1]) * (R_titan+Alt_level[i+1]))
    return Alt_level, P_level, T_level
           
def select_albedo_from_Alt_lambda(alt,lamb,ALBEDO):
    # work in nm for lamb and km for alt
    id1 = find_closest_index(ALBEDO[1],lamb)
    id2 = find_closest_index(ALBEDO[0],alt)
    return(ALBEDO[2][id1,id2])

def find_nearest(P,T,data):
    # find Pmin Pmax
    idx_p = np.sort(np.abs(P - data[1]).argpartition(2)[:2])
    # find Tmin Tmax |Pmin
    idx_t1 = np.sort(np.abs(T - data[2][idx_p[0],:]).argpartition(2)[:2])
    # find Tmin Tmax |Pmax
    idx_t2 = np.sort(np.abs(T - data[2][idx_p[1],:]).argpartition(2)[:2])

    return [idx_p[0],idx_p[0],idx_p[1],idx_p[1]],[idx_t1[0],idx_t1[1],idx_t2[0],idx_t2[1]]

def get_distance(pt1, pt2):
    """
    Calculate the Euclidean distance between two points in 2D (P,T) space.
    """
    return np.sqrt(np.sum((pt1 - pt2)**2))

def interpolate_c_point(status_point, reference_points, c_values):
    """
    Perform a linear interpolation of c value based on the status point.

    Args:
        status_point (numpy array): The (P, T) values of the status point.
        reference_points (numpy array): The (P, T) values of the reference points.
        c_values (numpy array): The c values corresponding to the reference points.

    Returns:
        The interpolated c value for the status point.
    """

    distances = np.apply_along_axis(get_distance, 1, reference_points, status_point)
    weights = 1 / distances
    # Handle the case where the status point equals a reference point, resulting in a distance of 0
    weights[np.isnan(weights)] = 1

    # Normalize the weights so they sum to 1
    weights = weights / np.sum(weights)

    # Calculate the weighted average of the c values
    c_avg = np.dot(weights, c_values)

    return c_avg

def calc_absorption_coefficient(P_mbar, T, sigma, Vratio):
    """
    Calculate the absorption coefficient.

    Parameters:
    P_mbar (float): Pressure of the gas in millibar.
    T (float): Temperature of the gas in Kelvin.
    sigma (float): Cross section of the gas in cm^2.
    Vratio (float): CH4 Volume mixing ratio.

    Returns:
    float: Absorption coefficient of the gas.
    """

    # Convert sigma from cm^2 to m^2
    sigma = sigma * 1E-4

    # Convert pressure from millibar to Pascals
    P = P_mbar * 100

    # Number density n = P / (k * T)
    n = P / (sc.k * T)

    # Absorption coefficient κ = σ * n * Vratio
    kappa = sigma * n * Vratio 

    return kappa

def calc_rayleigh_cross_section_n2(wavelength):
    """
    wavelength: mu
    """
    #alpha = 6.8552e-5 * 3.243157e-2/(144-np.power(wavelength,-2))
    alpha = 6.8552e-5 + 3.243157e-2/143
    c = 4.58156e-21/np.power(wavelength,4) * alpha * alpha
    return c

def calc_rayleigh_cross_section_ch4(wavelength):
    """
    wavelength: mu
    """
    alpha = 4.2607e-4 + 6.1396687e-6/np.power(wavelength,2)
    c = 4.58156e-21/np.power(wavelength,4) * alpha * alpha
    return c

def calc_rayleigh_ks(P_mbar, T, sigma, Vratio):
    """
    Calculate the scattering coefficient.

    Parameters:
    P_mbar (float): Pressure of the gas in millibar.
    T (float): Temperature of the gas in Kelvin.
    sigma (float): Cross section of the gas in cm^2.
    Vratio (float): CH4 Volume mixing ratio.

    Returns:
    float: Absorption coefficient of the gas.
    """

    # Convert sigma from cm^2 to m^2
    sigma = sigma * 1E-4

    # Convert pressure from millibar to Pascals
    P = P_mbar * 100

    # Number density n = P / (k * T)
    n = P / (sc.k * T)

    # Absorption coefficient κ = σ * n * Vratio
    kappa = sigma * n * Vratio 

    return kappa


def add_Alt(Alt,P,T,Alt_max):
    Alt = np.append(Alt,Alt_max)
    P = np.append(P,P[-1])
    T = np.append(T,T[-1])
    return Alt,P,T


