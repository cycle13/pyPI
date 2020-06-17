# This module stores functions used throughout pyPI
# Last updated 4/16/2020
#

# import numpy to use in functions
import numpy as np
import constants

# ---------------------- Longitude conversion ---------------------- %

# define function to convert longitudes from 0-360E to 180W-180E, and vice-versa
def convert_lon_to180(lon360):
    lon180 = (lon360-1e-6 + 180) % 360 - 180
    return(lon180)

def convert_lon_to360(lon180):
    lon360 = lon180 % 360
    return(lon360)


# ---------------------- Thermodynamic Calculations ---------------------- %

# Saturated water vapor pressure
# from Clausius-Clapeyron relation/August-Roche-Magnus formula
# Input temperature (TC) in Celsius
# Output saturation vapor pressure in hPa
def es_cc(TC):
    return 6.112*np.exp(17.67*TC/(243.5+TC))

# Latent heat of vaporization, as a function of temperature
# Input temperature (TC) in Celsius
# Output Latent heat of vaporization in J/kg
def Lv(TC):
    return constants.ALV0+constants.CPVMCL*TC

# Parcel vapor pressure (hPa)
# Input mixing ratio (R) in gram/gram
# Input pressure (P) in hPA
def ev(R,P):
    return R*P/(constants.EPS+R)

# Parcel mixing ratio (gram/gram)
# Input vapor pressure (E) in hPa
# Input pressure (P) in hPA
def rv(E,P):
    return EPS*E/(P-E)

# Total specific Entropy per unit mass of dry air (E94, EQN. 4.5.9)
# Input temperature (T) in kelvin
# Input mixing ratio (R) in gram/gram
# Input pressure (P) in hPA
def entropy_S(T,R,P):
    EV=ev(R,P)
    ES=es_cc(T-273.15)
    RH=min([EV/ES,1.0])
    ALV=Lv(T-273.15)
    S=(constants.CPD+R*constants.CL)*np.log(T)-constants.RD*np.log(P-EV)+ALV*R/T-R*constants.RV*np.log(RH)
    return(S)

# Saturated total specific Entropy per unit mass of dry air (E94, EQN. 4.5.9)
# Input temperature (T) in kelvin
# Input mixing ratio (R) in gram/gram
# Input pressure (P) in hPA
def entropy_Sstar(T,R,P):
    EV=ev(R,P)
    ALV=Lv(T-273.15)
    S=(constants.CPD+R*constants.CL)*np.log(T)-constants.RD*np.log(P-EV)+ALV*R/T
    return(S)

# Density temperature in K
# Input temperature (T) in kelvin
# Input mixing ratio (R) in gram/gram
def Trho(T,R):
    return T*(1.+R/constants.EPS)/(1.+R)

# Empirical pLCL
# Input parcel pressure (PP), temperature (TP), and relative humidity
# Output lifting condensation level pressure
def e_pLCL(TP,RH,PP):
    return PP*(RH**(TP/(constants.A-constants.B*RH-TP)))

# ---------------------- Analyses ---------------------- %

# define function to calculate TC efficiency
def pi_effiency(sstk,t0):
    # calculate efficiency with SST (K) and Outflow temperature (K)
    efficiency=(sstk-t0)/t0
    return(efficiency)

# define function to calculate TC air-sea thermodynamic disequilibrium
# as a residual from Bister and Emanuel (1998; BE98) EQN. 21
def pi_diseq_resid(pi,sstk,t0,CKCD=0.9):
    # calculate efficiency with SST (K) and Outflow temperature (K)
    efficiency=(sstk-t0)/t0
    # calculate disequilibrium with the BE98 equality
    diseq=pi**2/(CKCD*efficiency)
    return(diseq)

# define function to perform decomposition of TC PI terms
# from Wing et al. (2015), EQN. 2
def decompose_pi(pi,sstk,t0,CKCD=0.9):
    # the natural log of Ck/CD is a constant
    lnCKCD=np.log(CKCD)
    # calculate efficiency with SST (K) and Outflow temperature (K)
    efficiency=(sstk-t0)/t0
    # Is efficiency greater than 0? If not, return missing
    if (efficiency>0):
        # calculate disequilibrium with the BE98 equality
        diseq=pi**2/(CKCD*efficiency)
        lneff=np.log(efficiency)
        # Is potential intensity greater than 0? If not, return missing
        if pi>0:
            lnpi=2*np.log(pi)
            # the log of disequilibrium is calculated as a residual
            lndiseq=lnpi-lneff-lnCKCD
            return(lnpi,lneff,lndiseq,lnCKCD)
        else:
            return(np.nan,lneff,np.nan,lnCKCD)
    else:
        return(np.nan,np.nan,np.nan,lnCKCD)