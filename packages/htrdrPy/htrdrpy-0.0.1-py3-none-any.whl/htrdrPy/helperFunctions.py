import numpy as np
import scipy.constants as cst
import scipy.interpolate as interp


keysLMDZtitan_vi = {
    'tsurf': 'tsurf',               # surface temperature
    'temp': 'temp',                 # temperature
    'wavelength': 'wavelength_vi',  # visible wavelengths
    'ssa': 'wv',                    # single scatering albedo
    'extinction': 'kv',             # extinction coefficeint
    'assym': 'gv',                  # assymetry factor
    'geopotential': 'pphi',         # geopotential
    'geopotentialSurf': 'pphis',    # surface geopotential
    'altitude': 'altitude',         # altitude
    'latitude': 'lat',              # latitude
    'longitude': 'lon',             # longitude
    'pressure': 'p',                # pressure
}

keysLMDZtitan_ir = {
    'tsurf': 'tsurf',               # surface temperature
    'temp': 'temp',                 # temperature
    'wavelength': 'wavelength_ir',  # visible wavelengths
    'ssa': 'wi',                    # single scatering albedo
    'extinction': 'ki',             # extinction coefficeint
    'assym': 'gi',                  # assymetry factor
    'geopotential': 'pphi',         # geopotential
    'geopotentialSurf': 'pphis',    # surface geopotential
    'altitude': 'altitude',         # altitude
    'latitude': 'lat',              # latitude
    'longitude': 'lon',             # longitude
    'pressure': 'p',                # pressure
}


def sphere2cart(vec):
    '''
    Convert spherical to cartesian coordinates.
    # Input:
    - vec (1-D array (shape=(3), float [m,°,°])): [altitude, latitude, longitude]
    # Output:
    - 1-D array (shape=(3), float [m,m,m]): [x, y, z]
    '''
    alt, lat, lon = vec[0], vec[1] * cst.degree, vec[2] * cst.degree
    return np.array([
        np.cos(lat) * np.cos(lon),
        np.cos(lat) * np.sin(lon),
        np.sin(lat)
    ]) * alt

def cart2sphere(vec):
    '''
    Convert cartesian to spherical coordinates.
    # Input:
    - vec (1-D array (shape=(3), float [m,m,m])): [x, y, z]
    # Output:
    - 1-D array (shape=(3), float [m,°,°]): [altitude, latitude, longitude]

    '''
    x,y,z = vec
    XsqPlusYsq = x**2 + y**2
    r = np.sqrt(XsqPlusYsq + z**2)            # alt
    elev = np.atan2(z,np.sqrt(XsqPlusYsq))     # lat
    az = np.atan2(y,x)                        # lon
    return np.array([r, elev/cst.degree, az/cst.degree])

def interpolate(dataPoints, dataValues, nodes, flagNearest=False):
    if flagNearest:
        return interp.griddata(dataPoints, dataValues, nodes, method='nearest', rescale=True)
    dataInterp = interp.griddata(dataPoints, dataValues, nodes, method='linear', rescale=True)
    dataInterpNearest = interp.griddata(dataPoints, dataValues, nodes, method='nearest', rescale=True)
    mask = np.isnan(dataInterp)
    dataInterp[mask] = dataInterpNearest[mask]
    return dataInterp 

def integral(X, Y, low, up):
    if len(Y.shape) == 1: Y = Y.reshape(np.append(Y.shape,1))

    mask = (X>=low) & (X<=up)
    Xm = X[mask]
    Ym = Y[mask,:]
    if len(Xm) == 0:
        w = 0.5 * (low+up)
        index = np.argmin(abs(X-low))
        Xm = np.array([X[index], X[index+1]])
        Ym = np.array([Y[index,:], Y[index+1,:]])

    ilow = np.argmin(abs(Xm[0]-X)) - 1
    iup = np.argmin(abs(Xm[-1]-X)) + 1

    sm = 0
    if Xm[0]!=low:
        x0, y0 = X[ilow], Y[ilow,:]
        x1, y1 = Xm[0], Ym[0,:]
        x = low

        a = (x - x0)/(x1 - x0)
        y = a*y1 + (1-a)*y0
        sm += 0.5*(y + y1)*(x1-x)

    dx = Xm[1:] - Xm[:-1]
    yy = 0.5 * (Ym[1:,:] + Ym[:-1,:])
    sm += (yy*dx[:,None]).sum(axis=0)

    if Xm[-1]!=up:
        x0, y0 = Xm[-1], Ym[-1,:]
        x1, y1 = X[iup], Y[iup,:]
        x = up

        a = (x - x0)/(x1 - x0)
        y = a*y1 + (1-a)*y0
        sm += 0.5*(y + y0)*(x-x0)

    return sm

def toSI(value, unit):
    '''
    Return the given metric in SI unit
    Input:
    - value: value of the metric in the original units
    - unit: original units of value. \
    Must follow the form: <unit>int.<unit>int....<unit>int/<unit>int.<unit>int....<unit>int \
    The unit are separated by a space. The exposant of the unit is given right after the unit and must be positive. \
    All units with positive exposant are proviede before "/" and all negatives after (omiting the "-") \
    The character "/" must not be repeated. \
    Angstrom is given as A°.
    Output:
    - value in SI units 
    '''

    def parser(u, SIkeys, nonSIkeys):
        u = np.array([u[i:i+1] for i in range(len(u))])
        mask = np.char.isdigit(u)
        if any(mask):
            power = int("".join(u[mask]))
        else:
            power = 1
        u = "".join(u[~mask])

        keys = [unit for unit in nonSIkeys if unit in u]
        if len(keys) == 1: return u.replace(keys[0], ""), keys[0], power
        elif len(keys) == 0: pass
        else: raise ValueError("too many non SI units")

        
        indices = [i for i,un in enumerate(u) if un=="m"]
        if len(indices) == 0: pass
        elif len(indices) == 1:
            rest = u.replace("m", "")
            if indices[0] == 0 and rest != "": return "m", rest, power
            else: return rest, "m", power
        elif len(indices) == 2: return "m", "m", power
        else: raise ValueError("too many 'm' in unit")


        keys = [unit for unit in SIkeys if unit in u]
        if len(keys) == 1: return u.replace(keys[0], ""), keys[0], power
        elif len(keys) == 0: raise ValueError("no units found")
        else: raise ValueError("too many SI units")


    siUnits = ['g', 'K', 'm', 'A', 's', 'cd', 'W', 'J', 'Pa', 'N', 'V']
    prefixes = {
        '': 1,
        'Z': cst.zetta,
        'E': cst.exa,
        'P': cst.peta,
        'T': cst.tera,
        'G': cst.giga,
        'M': cst.mega,
        'k': cst.kilo,
        'h': cst.hecto,
        'da': cst.deka,
        'd': cst.deci,
        'c': cst.centi,
        'm': cst.milli,
        'µ': cst.micro,
        'n': cst.nano,
        'p': cst.pico,
        'f': cst.femto,
        'a': cst.atto
    }
    otherUnits = {
        # distance
        'A°': cst.angstrom,
        'au': cst.au,
        'pc': cst.parsec,
        'ly': cst.light_year,
        # mass
        'T': cst.metric_ton,
        'amu': cst.atomic_mass,
        # pressure
        'bar': cst.bar,
        'atm': cst.atm,
        'psi': cst.psi,
        'mmHg': cst.mmHg,
        # volume
        'L': cst.liter,
        # energy
        'eV': cst.electron_volt,
        'cal': cst.calorie,
        'erg': cst.erg,
        # force
        'dyn': cst.dyne
    }

    try:
        unitsUp, unitsLow = unit.split("/")
        unitsUp, unitsLow = unitsUp.split(), unitsLow.split()
    except ValueError:
        unitsUp = unit.split()
        unitsLow = []

    print(unitsUp, unitsLow)
    for u in unitsUp:
        prefix, un, power = parser(u, siUnits, otherUnits.keys())
        if un == "g":
            value *= (prefixes[prefix] / cst.kilo) ** power
        elif un in otherUnits:
            value *= (prefixes[prefix] * otherUnits[un]) ** power
        else:
            value *= (prefixes[prefix]) ** power

    for u in unitsLow:
        prefix, un, power = parser(u, siUnits, otherUnits.keys())
        if un == "g":
            value *= (prefixes[prefix] / cst.kilo) ** ( - power)
        elif un in otherUnits:
            value *= (prefixes[prefix] * otherUnits[un]) ** ( - power)
        else:
            value *= (prefixes[prefix]) ** ( - power)

    return value

def planck(T, wvl, r_d=False):
    '''
    Calculate planck emission in W/m2/sr/m for a surface T at wavelengths wvl
    # Input
    - T (float or N-D array of float [K]): temperature of the surface
    - wvl (float or 1-D array (shape=(nWavelength), float [m])): wavelengths
    - r_d (optional, 1-D array (shape=(2), float [m])): the source radius and distance, respectively. \
        If not given, returns the surface radiance, if given, returns the radiance received at that distance from the source
    # Output
    float of 1-D array (shape=(nWavelength), float [W/m2/sr/m])) according to the shape of wvl
    '''

    # if both T and wvl are arrays, we must add dimensions to both tables for
    # the following calculation to work
    if isinstance(T, np.ndarray) and isinstance(wvl, np.ndarray):
        shp = T.shape
        nWvl = wvl.shape[0]
        nDim = len(shp)

        # we add an axis at the end for the wavelength
        T = np.expand_dims(T, axis=-1)

        # we add as many axes as dimensions in T at the beginning of wvl
        axes = np.arange(0, nDim).astype(int)
        wvl = np.expand_dims(wvl, axis=tuple(axes))

    c1 = 2*cst.h*cst.c**2/(wvl**5)
    c2 = cst.h*cst.c/(wvl*cst.k*T)
    L = c1 / (np.exp(c2) - 1) # W/m2/sr/m

    if r_d:
        radius, distance = r_d
        return L * (radius/distance)**2
    else:
        return L

def dplanck_dT(T, wvl, r_d=False): 
    ''' Calculate derivative of the planck emission regarding the temperature in
    W/m2/sr/m/K for a surface T at wavelengths wvl
    # Input
    - T (float or N-D array of float [K]): temperature of the surface
    - wvl (float or 1-D array (shape=(nWavelength), float [m])): wavelengths
    - r_d (optional, 1-D array (shape=(2), float [m])): the source radius and
      distance, respectively. \n If not given, returns the surface radiance, if
      given, returns the radiance received at that distance from the source
    # Output
    float of 1-D array (shape=(nWavelength), float [W/m2/sr/m])) according to
    the shape of wvl '''

    # if both T and wvl are arrays, we must add dimensions to both tables for
    # the following calculation to work
    if isinstance(T, np.ndarray) and isinstance(wvl, np.ndarray):
        shp = T.shape
        nWvl = wvl.shape[0]
        nDim = len(shp)

        # we add an axis at the end for the wavelength
        T = np.expand_dims(T, axis=-1)

        # we add as many axes as dimensions in T at the beginning of wvl
        axes = np.arange(0, nDim).astype(int)
        wvl = np.expand_dims(wvl, axis=tuple(axes))

    c1 = 2*cst.h*cst.c**2/(wvl**5)
    c2 = cst.h*cst.c/(wvl*cst.k*T)
    L = ( (c1 * c2 ) / T ) / (np.exp(c2) - 1)**2 # W/m2/sr/m

    if r_d:
        radius, distance = r_d
        return L * (radius/distance)**2
    else:
        return L

def plotVector(ax, origin, vector, color='k', arrow_length_ratio=0.01, zorder=0):
    ax.quiver(origin[0], origin[1], origin[2], vector[0], vector[1], vector[2], arrow_length_ratio=arrow_length_ratio, color=color, zorder=zorder)

def set_axes_equal(ax):
    """
    Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc.

    Input
        ax: a matplotlib axis, e.g., as output from plt.gca().
    """

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5*max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])
    return

def readRadianceKurucz(file, radius):
    wavelength, spectrum = np.loadtxt(file, usecols=(0,1), unpack=True)
    spectrum *= cst.milli * (1/cst.nano)
    return wavelength, spectrum * ((cst.au/radius)**2)/np.pi

def combineEstimates(sumX, sumXsquare, numbers):
    '''
    Calculate the mean, the variance and the standard deviation of a set of values
    # Input:
    - sumX (1-D array, shape=(N), float): sum of the values
    - sumXsquare (1-D array, shape=(N), float): sum of the square of the values
    - numbers (int): number of realizations for each estimate
    # Output:
    - mean (float): mean of the values
    - variance (float): variance of the values
    - std (float): standard deviation of the values
    '''
    N = numbers.sum()
    mean = sumX.sum() / N
    variance = ((sumXsquare.sum() / N) - mean**2) / (N-1)
    deviation = np.sqrt(variance)
    return mean, variance, deviation

if __name__ == "__main__":
    T = np.linspace(200, 1000, 300)
    T = T.reshape((10,3,10))
    wvl = np.linspace(1e-7, 8e-7, 16)
    B = planck(T, wvl)
    print(B.shape)
