#!/usr/bin/python
from xml.dom.minidom import parse
import re
import os.path
import struct
from numpy import *
from neicmap.distance import sdist
from neicio.grid import GridError
from neicutil.text import decToRoman,commify
from sets import Set

class PagerCityError(Exception):
    """Used to handle errors for PagerCity"""
    def __str__(self):
        return repr(self.args[0])

class PagerCity:
    """
    Handles loading and searching for cities.
    """
    cities = []
    def __init__(self,cityfile=None):
        """
        Instantiate PagerCity object.
        @keyword cityfile: cities1000.txt file from the GeoNames website. If no cities file is provided, 
                           each call to instance methods MUST provide a separate city list.
        """
        if cityfile is not None:
            self.loadCities(cityfile)

    def findCitiesByName(self,cityname):
        for city in self.cities:
            m1 = re.search(cityname,city['name'])
            m2 = re.search(city['name'],cityname)
            if m1 is not None or m2 is not None:
                return city.copy()
        return None
            
    def filterCitiesByGrid(self,xmin,xmax,ymin,ymax,xdim,ydim,ncities,citylist=None):
        if citylist == None:
            citylist = self.cities
        ncols = int((xmax - xmin)/xdim)
        nrows = int((ymax - ymin)/ydim)
        subcities = []
        for i in range(0,nrows):
            bymin = ymin + i*ydim
            bymax = bymin + ydim
            if i == nrows-1:
                bymax = max(bymax,ymax)
            for j in range(0,ncols):
                bxmin = xmin + j*xdim
                bxmax = bxmin + xdim
                if j == ncols-1:
                    bxmax = max(bxmax,xmax)
                tcities = self.findCitiesByRectangle([bxmin,bxmax,bymin,bymax],citylist)
                
                if len(tcities):
                    tcities = self.sortCities(tcities,method='capital')
                    n = min(len(tcities),ncities)
                    for k in range(0,n):
                        subcities.append(tcities[k])

        return subcities
            
            
    def findCitiesByRadius(self,lat,lon,radius,citylist=None):
        """
        Find cities inside a given search radius.
        @param lat:  Latitude of center of search radius.
        @param lon:  Longitude of center of search radius.
        @param radius: Radius (in km) within which search should be conducted.
        @keyword citylist: List of city dictionaries to search from:
                           - name   City name
                           - ccode  Two-letter country code.
                           - lat    Latitude of city center.
                           - lon    Longitude of city center.
                           - iscap  Boolean indicating if city is a capital of a region or country.
                           - pop    Population of city.
        @return: List of city dictionaries (same fields as input citylist).
        """
        subcities = []
        if citylist == None:
            citylist = self.cities
        for city in citylist:
            if sdist(lat,lon,city['lat'],city['lon']) <= radius*1000:
                subcities.append(city)

        return subcities

    def findCitiesByRectangle(self,bounds,citylist=None):
        """
        Find cities inside a given rectangle.
        @param bounds:  Sequence of [lonmin,lonmax,latmin,latmax].
        @keyword citylist: List of city dictionaries to search from:
                           - name   City name
                           - ccode  Two-letter country code.
                           - lat    Latitude of city center.
                           - lon    Longitude of city center.
                           - iscap  Boolean indicating if city is a capital of a region or country.
                           - pop    Population of city.
        @return: List of city dictionaries (same fields as input citylist).
        """
        xmin = bounds[0]
        xmax = bounds[1]
        ymin = bounds[2]
        ymax = bounds[3]
        subcities = []
        if citylist == None:
            citylist = self.cities
        for city in citylist:
            if city['lat'] >= ymin and city['lat'] <= ymax and city['lon'] >= xmin and city['lon'] <= xmax:
                subcities.append(city)

        return subcities
    
    def findCitiesByCountry(self,ccode,citylist=None):
        """
        Find cities within a particular country.
        @param ccode:  Two letter country code.
        @keyword citylist: List of city dictionaries to search from:
                           - name   City name
                           - ccode  Two-letter country code.
                           - lat    Latitude of city center.
                           - lon    Longitude of city center.
                           - iscap  Boolean indicating if city is a capital of a region or country.
                           - pop    Population of city.
        @return: List of city dictionaries (same fields as input citylist).
        """
        subcities = []
        if citylist == None:
            citylist = self.cities
        for city in citylist:
            if city['ccode'].lower() == ccode.lower():
                subcities.append(city)

        return subcities
        
    def findCitiesByCapital(self,citylist=None):
        """
        Find cities that are capitals of a region or country.
        @keyword citylist: List of city dictionaries to search from:
                           - name   City name
                           - ccode  Two-letter country code.
                           - lat    Latitude of city center.
                           - lon    Longitude of city center.
                           - iscap  Boolean indicating if city is a capital of a region or country.
                           - pop    Population of city.
        @return: List of city dictionaries (same fields as input citylist).
        """
        subcities = []
        if citylist == None:
            citylist = self.cities
        for city in citylist:
            if city['iscap']:
                subcities.append(city)

        return subcities

    def findCitiesByPopulation(self,pop1,pop2,citylist=None):
        """
        Find cities that have a population between two bracketing values.
        @param pop1: Minimum population threshold.
        @param pop2: Maximum population threshold.
        @keyword citylist: List of city dictionaries to search from:
                           - name   City name
                           - ccode  Two-letter country code.
                           - lat    Latitude of city center.
                           - lon    Longitude of city center.
                           - iscap  Boolean indicating if city is a capital of a region or country.
                           - pop    Population of city.
        @return: List of city dictionaries (same fields as input citylist).
        """
        subcities = []
        if citylist == None:
            citylist = self.cities
        for city in citylist:
            if city['pop'] >= pop1 and city['pop'] <= pop2:
                subcities.append(city)

        return subcities

    def getCityExposure(self,shakegrid,citylist=None):
        """
        Find cities that are within a given shakemap, add MMI to keys.
        @param shakegrid: ShakeGrid object.
        @keyword citylist: List of city dictionaries to search from:
                           - name   City name
                           - ccode  Two-letter country code.
                           - lat    Latitude of city center.
                           - lon    Longitude of city center.
                           - iscap  Boolean indicating if city is a capital of a region or country.
                           - pop    Population of city.
        @return: List of city dictionaries, having the same fields as input citylist, with the addition of:
                 - mmi    MMI value to which city was exposed.
        """
        subcities = []
        if citylist == None:
            citylist = self.cities

        for city in citylist:
            lat = city['lat']
            lon = city['lon']
            try:
                mmi = shakegrid.getValue(lat,lon)
                city['mmi'] = mmi
                subcities.append(city)
            except GridError: #lat,lon may be out of bounds...
                continue

        return subcities
        

    def getCityTable(self,citylist):
        """
        Return a list of cities suitable for the onePAGER table of cities.
        
        The PAGER city sorting algorithm can be defined as follows.
        1. Sort cities by inverse intensity.  Select N (up to 6) from beginning of list.  If N < 6, return.
        2. Sort cities by capital status, and select M (up to 5) from beginning of the list that are not in the first list.
           If N+M == 11, sort selected cities by MMI, return list
        3. If N+M < 11, sort cities by inverse population, then select (up to) P= 11 - (M+N) cities that are not already in the list.  Combine
           list of P cities with list of N and list of M.
        4. Sort combined list of cities by inverse MMI and return.
        
        @param citylist:  List of city dictionaries from which to search, with at least the following keys:
                         - name   City name
                         - ccode  Two-letter country code.
                         - lat    Latitude of city center.
                         - lon    Longitude of city center.
                         - iscap  Boolean indicating if city is a capital of a region or country.
                         - pop    Population of city.
        @return: List of city dictionaries, sorted by algorithm described above.
        """
        NMax = 6
        MMax = 5
        NTotal = 11
        #Step 1 - get at most 6 cities with highest MMI
        mmicities = self.sortCities(citylist,method='mmi')
        if len(mmicities) < NMax:
            return mmicities
        mmicities = citylist[0:NMax]
        #Step 2 - get at most 5 cities that are capitals
        capcities,citylist = self.removeDuplicateCities(citylist,mmicities,'capital',MMax)
        capcities2 = []
        for city in capcities:
            if city['iscap']:
                capcities2.append(city)
        combined_cities = mmicities + capcities2
        if len(combined_cities) == NTotal:
            return self.sortCities(combined_cities,method='mmi')
                
        #Step 3 - Fill out list with top cities by population
        ncities = len(combined_cities)
        popcities,citylist = self.removeDuplicateCities(citylist,combined_cities,'population',NTotal-ncities)
        combined_cities = combined_cities + popcities
        
        #Step 4 - Sort list by MMI, return
        return self.sortCities(combined_cities,method='mmi')
        
        
    def removeDuplicateCities(self,allcities,citylist1,method,maxlen):
        """
        Return a list (of maxlen or less) of sorted cities selected from allcities that does not intersect with citylist1.

        @param allcities:  Large list of cities from which to search and sort.
        @param citylist1:  List against which selected sorted cities should be compared for duplicates.
        @param method:   Method by which selected cities should be sorted.
        @param maxlen:   Maximum length of list of selected sorted cities.
        @return: Two element tuple of selected cities and modified list of allcities (with duplicates removed).
        """
        c1names = [city['name'] for city in citylist1]
        citylist2 = self.sortCities(allcities,method=method)
        allnames = [city['name'] for city in allcities]
        c2names = [city['name'] for city in citylist2]
        

        dupcities = list(Set(c1names).intersection(c2names))
        while len(dupcities) > 0:
            for dup in dupcities:
                dupidx = allnames.index(dup)
                allcities.pop(dupidx)
                allnames = [city['name'] for city in allcities]
            citylist2 = self.sortCities(allcities,method=method)
            allnames = [city['name'] for city in allcities]
            c2names = [city['name'] for city in citylist2]
            dupcities = list(Set(c1names).intersection(c2names))
        
        if len(citylist2) > maxlen:
            citylist2 = citylist2[0:maxlen]
        return (citylist2,allcities)

        
    def sortCities(self,citylist,method=None):
        """
        Given a list of cities, sort them by one of N methods.

        @param citylist: List of city dictionaries, with at least the following keys:
                         - name   City name
                         - ccode  Two-letter country code.
                         - lat    Latitude of city center.
                         - lon    Longitude of city center.
                         - iscap  Boolean indicating if city is a capital of a region or country.
                         - pop    Population of city.
        @keyword method: String indicating which sorting method to use:
                         - 'population' - Sort by inverse city population
                         - 'capital' - Sort by inverse capital status.
                         - 'mmi' - Sort by inverse MMI.
                         - 'pager' - Use PAGER algorithm to determine list of (at most) 11 cities.
        @return: List of city dictionaries (see input).
        """
        if len(citylist) == 0:
            return citylist
        if method==None:
            citylist.sort(self.sortCitiesByPopulation)
            return citylist
        method = method.lower()
        if method == 'mmi' and 'mmi' not in citylist[0].keys():
            raise PagerCityError, 'Key "mmi" not in city dictionary list'

        popmatch = re.compile('pop')
        capmatch = re.compile('cap')
        
        haspop = popmatch.search(method)
        hascap = capmatch.search(method)
        if hascap:
            citylist.sort(self.sortCitiesByCapital,reverse=True)
            return citylist
        elif haspop:
            citylist.sort(self.sortCitiesByPopulation,reverse=True)
            return citylist
        else:
            citylist.sort(self.sortCitiesByMMI,reverse=True)

        return citylist

    def formatCityList(self,citylist,ncities):
        if len(citylist) == 0:
            return 'No cities were exposed.'

        citylist = self.getCityTable(citylist)
        ncities = min(ncities,len(citylist))
        #citylist2 = self.sortCities(citylist,method)
        cwidth = 0
        for city in citylist:
            if len(city['name']) > cwidth:
                cwidth = len(city['name'])
        
        fmt1 = '%-4s %-' + str(cwidth) + 's %-10s\n'
        fmt2 = '%-' + str(cwidth) + 's %-10s\n'
        if 'mmi' in citylist[0].keys():
            citytext = fmt1 % ('MMI','City','Population')
        else:
            citytext = fmt2 % ('City','Population')

        for i in range(0,ncities):
            city = citylist[i]
            name = city['name']
            pop = commify(city['pop'])
            if 'mmi' in city.keys() and city['mmi'] >= 1:
                mmi = decToRoman(round(city['mmi']))
                citytext = citytext + fmt1 % (mmi,name,pop)
            else:
                citytext = citytext + fmt2 % (name,pop)
        return citytext

    def sortCitiesByMMI(self,city1,city2):
        """Given two City dictionaries, sort them by MMI.

        @param city1: city dictionary.
        @param city2: city dictionary.
        @return: 
          - 0 when city populations are identical
          - -1 when city1 has a smaller population than city2
          - 1 when city1 has a larger population than city2
        """
        mmi1 = city1['mmi']
        mmi2 = city2['mmi']
        return cmp(mmi1,mmi2)

    def sortCitiesByPopulation(self,city1,city2):
        """Given two City dictionaries, sort them by population.

        @param city1: city dictionary.
        @param city2: city dictionary.
        @return: 
          - 0 when city populations are identical
          - -1 when city1 has a smaller population than city2
          - 1 when city1 has a larger population than city2
        """
        pop1 = city1['pop']
        pop2 = city2['pop']
        return cmp(pop1,pop2)
    
    def sortCitiesByCapital(self,city1,city2):
        """Given two city dictionary objects, sort them by population and capital status.

        If neither city is a capital, the one with the greater population wins.
        A capital city trumps a non-capital city, regardless of population size.
        
        @param city1: City object.
        @param city2: City object.
        @return: 
          - 0 when city populations are identical and both are either capitals or not capitals.
          - -1 when city1 has a smaller population than city2 or if city1 is not a capital and city2 is.
          - 1 when city1 has a larger population than city2 or if city1 is a capital and city2 is not.
        """
        iscap1 = city1['iscap']
        iscap2 = city2['iscap']
        c = cmp(iscap1,iscap2) 
        if c != 0:
            return c
        else:
            return cmp(city1['pop'],city2['pop'])



    def loadCities(self,cityfile):
        #     1)geonameid         : integer id of record in geonames database
        #     2)name              : name of geographical point (utf8) varchar(200)
        #     3)asciiname         : name of geographical point in plain ascii characters, varchar(200)
        #     4)alternatenames    : alternatenames, comma separated varchar(4000)
        #     5)latitude          : latitude in decimal degrees (wgs84)
        #     6)longitude         : longitude in decimal degrees (wgs84)
        #     7)feature class     : see http://www.geonames.org/export/codes.html, char(1)
        #     8)feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
        #     9)country code      : ISO-3166 2-letter country code, 2 characters
        #     10)cc2              : alternate country codes, comma separated, ISO-3166 2-letter country code, 60 characters
        #     11)admin1 code      : fipscode (subject to change to iso
        #                           code), isocode for the us and ch, see file
        #                           admin1Codes.txt for display names of this code; varchar(20)
        #     12)admin2 code      : code for the second administrative
        #                           division, a county in the US, see file admin2Codes.txt;varchar(80)
        #     13)admin3 code      : code for third level administrative division, varchar(20)
        #     14)admin4 code      : code for fourth level administrative division, varchar(20)
        #     15)population       : integer 
        #     16)elevation        : in meters, integer
        #     17)gtopo30          : average elevation of 30'x30' (ca 900mx900m) area in meters, integer
        #     18)timezone         : the timezone id (see file timeZone.txt)
        #     19)modification date: date of last modification in yyyy-MM-dd format
        CAPFLAG1 = 'PPLC'
        CAPFLAG2 = 'PPLA'
        tmpcities = []
        self.cities = []
        if not os.path.isfile(cityfile):
            raise PagerCityError, 'Could not find specified city file %s.' % (cityfile)
        f = open(cityfile,'rt')
        for line in f.readlines():
            city = {}
            parts = line.split('\t')
            city['name'] = parts[2].strip()
            city['ccode'] = parts[8].strip()
            city['lat'] = float(parts[4].strip())
            city['lon'] = float(parts[5].strip())
            city['iscap'] = (parts[7].strip() == CAPFLAG1 or parts[7] == CAPFLAG2)
            city['pop'] = int(parts[14].strip())
            if not city['name']:
                #print 'Found a city with no name'
                continue
            myvals = array([ord(c) for c in city['name']])
            if len((myvals > 127).nonzero()[0]):
                #print '%s' % parts[0]
                continue
            self.cities.append(city)
        f.close()
