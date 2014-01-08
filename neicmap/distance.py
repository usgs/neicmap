#!/usr/bin/python
#from numpy import *
import numpy

def getCompassDir(lat1,lon1,lat2,lon2,format='short'):
    """
    Get the nearest string compass direction between two points.
    @param lat1: Latitude of first point.
    @param lon1: Longitude of first point.
    @param lat2: Latitude of second point.
    @param lon2: Longitude of second point.
    @keyword format: String used to determine the type of output. ('short','long').
    @return: String compass direction, in the form of 'North','Northeast',... if format is 'long', 
             or 'N','NE',... if format is 'short'.
    """
    if format != 'short':
        points = ['North','Northeast','East','Southeast','South','Southwest','West','Northwest']
    else:
        points = ['N','NE','E','SE','S','SW','W','NW']
    az = getAzimuth(lat1,lon1,lat2,lon2)
    angles = numpy.arange(0,360,45)
    adiff = abs(az - angles)
    i = adiff.argmin()
    return points[i]

def getAzimuth(lat1,lon1,lat2,lon2):
    """
    Get the numerical compass direction between two points.
    @param lat1: Latitude of first point.
    @param lon1: Longitude of first point.
    @param lat2: Latitude of second point.
    @param lon2: Longitude of second point.
    @return: Numerical compass direction between two input points.
    """
    DE2RA = 0.01745329252 
    RA2DE = 57.2957795129
    lat1 = lat1 * DE2RA
    lat2 = lat2 * DE2RA
    lon1 = lon1 * DE2RA
    lon2 = lon2 * DE2RA
    
    ilat1 = numpy.floor(0.50 + lat1 * 360000.0)
    ilat2 = numpy.floor(0.50 + lat2 * 360000.0)
    ilon1 = numpy.floor(0.50 + lon1 * 360000.0)
    ilon2 = numpy.floor(0.50 + lon2 * 360000.0)
    
    result = 0
    
    if ((ilat1 == ilat2) and (ilon1 == ilon2)):
        return result
    elif (ilon1 == ilon2):
         if (ilat1 > ilat2):
             result = 180.0

    else:
       c = numpy.arccos(numpy.sin(lat2)*numpy.sin(lat1) + numpy.cos(lat2)*numpy.cos(lat1)*numpy.cos((lon2-lon1)))
       A = numpy.arcsin(numpy.cos(lat2)*numpy.sin((lon2-lon1))/numpy.sin(c))
       result = (A * RA2DE)

       if (ilat2 > ilat1) and (ilon2 > ilon1):
          pass
       elif ((ilat2 < ilat1) and (ilon2 < ilon1)):
         result = 180.0 - result
       elif ((ilat2 < ilat1) and (ilon2 > ilon1)):
         result = 180.0 - result
       elif ((ilat2 > ilat1) and (ilon2 < ilon1)):
         result = result + 360.0

    if result < 0:
       result = result + 360

    return result

def distance(x1, y1, x2, y2):
    """Vincenty Inverse Solution of Geodesics on the Ellipsoid (c)
       Adapted from Chris Veness Javascript implementation:
            http://www.movable-type.co.uk/scripts/latlong-vincenty.html
                     
       Originally from: Vincenty inverse formula - T Vincenty, "Direct and Inverse Solutions of Geodesics on the 
            Ellipsoid with application of nested equations", Survey Review, vol XXII no 176, 1975   
            http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf                                             
    """
    #WGS-84 ellipsoid params
    a = 6378137.0
    b = 6356752.314245
    f = 1/298.257223563 

    L = radians(y2-y1);
    U1 = numpy.arctan((1-f) * numpy.tan(radians(x1)))
    U2 = numpy.arctan((1-f) * numpy.tan(radians(x2)))
    sinU1 = numpy.sin(U1)
    cosU1 = numpy.cos(U1)
    sinU2 = numpy.sin(U2)
    cosU2 = numpy.cos(U2)
    cosSqAlpha = sinSigma = cosSigma = cos2SigmaM = sigma = 0.0
    lmbd = L
    lambdaP = iterLimit = 100.0

    while abs(lmbd-lambdaP) > 1e-12 and iterLimit > 0:
        iterLimit -= 1
        sinLambda = numpy.sin(lmbd)
        cosLambda = numpy.cos(lmbd);
        sinSigma = (numpy.sqrt((cosU2*sinLambda) * (cosU2*sinLambda) + 
            (cosU1*sinU2-sinU1*cosU2*cosLambda) * (cosU1*sinU2-sinU1*cosU2*cosLambda)))

        if sinSigma==0: 
            return 0   #co-incident points
        cosSigma = sinU1*sinU2 + cosU1*cosU2*cosLambda
        sigma = atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
        cosSqAlpha = 1 - sinAlpha*sinAlpha
        cos2SigmaM = cosSigma - 2*sinU1*sinU2/cosSqAlpha
        try: #fail equatorial on python <2.6
            if isnan(cos2SigmaM):
                cos2SigmaM = 0 # equatorial line: cosSqAlpha=0 (6)
        except: 
            pass
        C = f/16*cosSqAlpha*(4+f*(4-3*cosSqAlpha))
        lambdaP = lmbd
        lmbd = (L + (1-C) * f * sinAlpha *
            (sigma + C*sinSigma*(cos2SigmaM+C*cosSigma*(-1+2*cos2SigmaM*cos2SigmaM))))

    if iterLimit==0:
        return -1 #formula failed to converge

    uSq = cosSqAlpha * (a*a - b*b) / (b*b)
    A = 1 + uSq/16384*(4096+uSq*(-768+uSq*(320-175*uSq)))
    B = uSq/1024 * (256+uSq*(-128+uSq*(74-47*uSq)))
    deltaSigma = B*sinSigma*(cos2SigmaM+B/4*(cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)-
            B/6*cos2SigmaM*(-3+4*sinSigma*sinSigma)*(-3+4*cos2SigmaM*cos2SigmaM)))
    s = b*A*(sigma-deltaSigma)
    return s
    
def sdist(lat1,lon1,lat2,lon2):
    """
    Approximate great circle distance (meters) assuming spherical Earth (6367 km radius).
    @param lat1: Latitude(s) of first point(s).
    @param lon1: Longitude(s) of first point(s).
    @param lat2: Latitude(s) of second point(s).
    @param lon2: Longitude(s) of second point(s).
    @return: Vector of great circle distances, same length as longer of two input arrays of points.
    """		
    R = 6367*1e3 #radius of the earth in meters, assuming spheroid
    dlon = lon1-lon2;
    t1 = pow((cosd(lat2)*sind(dlon)),2);
    t2 = pow((cosd(lat1)*sind(lat2) - sind(lat1)*cosd(lat2)*cosd(dlon)),2);
    t3 = sind(lat1)*sind(lat2) + cosd(lat1)*cosd(lat2)*cosd(dlon);
    
    dsig = numpy.arctan2(numpy.sqrt(t1+t2),t3);
    
    gcdist = R*dsig;
    return gcdist

def edist(lat1,lon1,lat2,lon2):
    """
    Euclidean distance (meters) between two (or more) latitude/longitude points.
    Warning: This distance is not as accurate as great circle distance, but faster.
    @param lat1: Latitude(s) of first point(s).
    @param lon1: Longitude(s) of first point(s).
    @param lat2: Latitude(s) of second point(s).
    @param lon2: Longitude(s) of second point(s).
    @return: Vector of great circle distances, same length as longer of two input arrays of points.
    """
    D2M = 111191  #meters in a decimal degree
    dlat = (lat2 - lat1)*D2M #y distance in kilometers
    dlon = (lon2 - lon1)*D2M*cosd(lat2) #x distance in kilometers
    d = numpy.sqrt(pow(dlat,2) + pow(dlon,2))
    return d

def cosd(input):
    """
    Returns cosine of angle given in degrees.
    """
    return numpy.cos(input * numpy.pi/180)

def sind(input):
    """
    Returns sine of angle given in degrees.
    """
    return numpy.sin(input * numpy.pi/180) 

def getLatLonToECEF(lat,lon,h=0):
    a = 6378137.0 #meters
    esq = 6.69437999014e-3
    N = a/(numpy.sqrt((1-esq)*sind(lat)**2))
    X = (N + h) * cosd(lat) * cosd(lon)
    Y = (N + h) * cosd(lat) * sind(lon)
    Z = (N * (1-esq) + h)*sind(lat)
    return (X,Y,Z)

def getHypoCentralDistance(lat1,lon1,h1,lat2,lon2,h2):
    x1,y1,z1 = getLatLonToECEF(lat1,lon1,h1)
    x2,y2,z2 = getLatLonToECEF(lat2,lon2,h2)
    distance = numpy.sqrt((x2-x1)**2 + (y2-y1)*2 + (z2-z1)**2)
    return distance
