#!/usr/bin/python
from types import IntType,StringType
import sys
import re
import csv
import os.path

def getCountryCode(value):
    """
    Return dictionary of information about country from input.

    The lists of country codes can be obtained from Wikipedia:
    http://en.wikipedia.org/wiki/ISO_3166-1

    Note: Three PAGER specific US earthquake regions have been added:
    'U.S. Earthquake Region California','XF','XFA','902'
    'U.S. Earthquake Region Western United States','XG','XGA','901'
    'U.S. Earthquake Region Central/Eastern United States','XH','XHA','903'

    @param value: Any of the following:
      - Two letter ISO country code (i.e., 'US' for United States)
      - Three letter ISO country code (i.e., 'USA' for United States)
      - Numeric ISO country code (i.e. 840 for United States)
      - String (preferably short) containing the name of the country.  Regular expressions will be used to attempt a match.
        NB:  The first potential match will be returned!
    @return: Dictionary containing the following values:
      - 'name' Full country name.
      - 'alpha2' Two letter ISO country code.
      - 'alpha3' Three letter ISO country code.
      - 'number' Numeric ISO country code.
    """
    doRegMatch = False
    doNumberMatch = False
    if type(value) is StringType:
        if len(value) != 2 and len(value) != 3:
            doRegMatch = True
    elif type(value) is IntType:
        doNumberMatch = True
    else:
        msg = 'Unsupported country search key %s with type %s' % (str(value),type(value))
        raise TypeError, msg
    clist = getCountryList()
    cdict = {'name':'','alpha2':'','alpha3':'','number':0,'shortname':''}
    for country in clist:
        if doRegMatch:
            s1 = re.search(value.lower(),country[0].lower())
            s2 = re.search(country[0].lower(),value.lower())
            if s1 is not None or s2 is not None:
                cdict['name'] = country[0]
                cdict['alpha2'] = country[1]
                cdict['alpha3'] = country[2]
                cdict['number'] = int(country[3])
                if len(country) == 5:
                    cdict['shortname'] = country[4]
                else:
                    cdict['shortname'] = country[0]
                break
        if doNumberMatch:
            if value in country:
                cdict['name'] = country[0]
                cdict['alpha2'] = country[1]
                cdict['alpha3'] = country[2]
                cdict['number'] = int(country[3])
                if len(country) == 5:
                    cdict['shortname'] = country[4]
                else:
                    cdict['shortname'] = country[0]
                break
            else:
                continue
        if value in country or value.upper() in country:
            cdict['name'] = country[0]
            cdict['alpha2'] = country[1]
            cdict['alpha3'] = country[2]
            cdict['number'] = int(country[3])
            if len(country) == 5:
                cdict['shortname'] = country[4]
            else:
                cdict['shortname'] = country[0]
            break
    return cdict
        
def getCountryList():
    """
    Return list of country information.
    
    Each entry in the list looks like this:
    ['Afghanistan','AF','AFG','4']

    @return: List of country lists, where each country list contains the following information:
      - Country name (i.e., 'Afghanistan')
      - Two letter ISO code (i.e., 'AF')
      - Three letter ISO code (i.e., 'AFG')
      - Numeric ISO code (i.e., '4')
      - (optional) Short country name
    """
    country = []
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    countryfile = os.path.join(homedir,'countries.csv')
    reader = csv.reader(open(countryfile,'rt'))
    for row in reader:
        row[3] = int(row[3])
        country.append(row)
    return country

def getLongestCountryName(useshort=False):
    clist = getCountryList()
    maxlen = 0
    for country in clist:
        if len(country) == 5 and useshort:
            name = country[4]
        else:
            name = country[0]
        if name > maxlen:
            maxlen = len(name)
    return maxlen

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:\n %s [key]\n, where key is either a 2 character or 3 character ISO code, or numeric ISO code' % sys.argv[0]
        sys.exit(1)
    key = sys.argv[1]
    try:
        cdict = getCountryCode(key)
        print 'Name: %s\nAlpha2: %s\nAlpha3: %s\nNumeric: %i\nShort: %s' % (cdict['name'],cdict['alpha2'],cdict['alpha3'],cdict['number'],cdict['shortname'])
    except TypeError,msg:
        print 'Command failed: %s' % (msg)
        sys.exit(1)
    sys.exit(0)
    
