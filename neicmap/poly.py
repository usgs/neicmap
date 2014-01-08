#!/usr/bin/python

import matplotlib.path as path
import numpy as np
from pylab import *

class PagerPolygon(object):
    """
    Class to encapsulate polygon objects which we wish to query about points they contain.
    """
    verts = []
    isComplex = False
    nparts = 0
    xmin = None
    xmax = None
    ymin = None
    ymax = None
    bounds = None
    def __init__(self,inxp,inyp):
        """
        Construct a PagerPolygon object.
        @param xp: Numpy array of x vertices, with parts separated by NaN.
        @param yp: Numpy array of y vertices, with parts separated by NaN.
        """
        xp = np.array(inxp)
        yp = np.array(inyp)
        
        self.verts = []
        self.xmin = xp[xp.argmin()]
        self.xmax = xp[xp.argmax()]
        self.ymin = yp[yp.argmin()]
        self.ymax = yp[yp.argmax()]
        self.bounds = (self.xmin,self.xmax,self.ymin,self.ymax)
        if len(find(isnan(xp))):
            self.isComplex = True
            #if we have NaN values, then the bounds will be NaN
            #search through each segment to find valid bounds
            self.xmin = 99999999
            self.xmax = -99999999
            self.ymin = 99999999
            self.ymax = -99999999
            inan = find(isnan(xp))
            self.nparts = len(inan)+1
            pstart = 0
            for i in range(0,len(inan)+1):
                if i == len(inan):
                    pnan = len(xp)
                else:
                    pnan = inan[i]

                #check the ranges of this segment against bounding box
                if xp[pstart:pnan].min() < self.xmin:
                    self.xmin = xp[pstart:pnan].min()
                if xp[pstart:pnan].max() > self.xmax:
                    self.xmax = xp[pstart:pnan].max()
                if yp[pstart:pnan].min() < self.ymin:
                    self.ymin = yp[pstart:pnan].min()
                if yp[pstart:pnan].max() > self.ymax:
                    self.ymax = yp[pstart:pnan].max()
                    
                self.verts.append(zip(xp[pstart:pnan],yp[pstart:pnan]))
                pstart = pnan+1
        else:
            self.nparts = 1
            self.verts = zip(xp,yp)
        
    def containsPoint(self,x,y):
        """
        Check to see if PagerPolygon contains input point.
        @param x: X coordinate of point.
        @param y: Y coordinate of point.
        @return: True if point is inside of polygon, False if outside.
        """
        #do a quick check with the bounding box
        if not (x > self.xmin and x < self.xmax and y > self.ymin and y < self.ymax):
            return False

        if not self.isComplex:
            xvert,yvert = zip(*self.verts)
            points = np.ones((len(yvert),2))
            points[:,0] = xvert
            points[:,1] = yvert
            p = path.Path(points)
            if p.contains_point((x,y)):
                return True
            else:
                return False
        else:
            for i in range(0,self.nparts):
                vertp = self.verts[i]
                xvert,yvert = zip(*vertp)
                points = np.ones((len(yvert),2))
                points[:,0] = xvert
                points[:,1] = yvert
                p = path.Path(points)
                if p.contains_point((x,y)):
                    return True
            return False

    def boundingBoxContainsPoint(self,x,y):
        #do a quick check with the bounding box
        if not (x > self.xmin and x < self.xmax and y > self.ymin and y < self.ymax):
            return False
        return True

    def containsPoints(self,x,y):
        """
        Check to see which input points are contained by a PagerPolygon.
        @param x: X coordinates of points.
        @param y: Y coordinates of points.
        @return: Numpy array of same length as X and Y, True where inside, False where outside.
        """
        if not self.isComplex:
            points = zip(x,y)
            xvert,yvert = zip(*self.verts)
            verts = np.ones((len(yvert),2))
            verts[:,0] = xvert
            verts[:,1] = yvert
            poly = path.Path(verts)
            return poly.contains_points(points)
        else:
            psum = zeros(x.shape)
            for i in range(0,self.verts):
                vertp = self.verts[i]
                xvert,yvert = zip(*vertp)
                points = np.ones((len(yvert),2))
                points[:,0] = xvert
                points[:,1] = yvert
                p = path.Path(points)
                psum = psum | p.contains_points(points)

            return psum

    def __repr__(self):
        """
        String representation of PagerPolygon.
        """
        fmt = '<PagerPolygon (xmin=%g,xmax=%g,ymin=%g,ymax=%g)>'
        return fmt % (self.xmin,self.xmax,self.ymin,self.ymax)

def inmultipoly(x,y,verts):
    """
    Convenience function for calculating point-in-polygon for 2D x,y arrays.
    @param x: 2D array of x values.
    @param y: 2D array of y values.
    @param verts: sequence of (x,y) tuples.
    @return: Numpy 2D array of boolean values indicating which x,y values are inside vertices.
    """
    m,n = x.shape
    x = x.reshape(m*n,1)
    y = y.reshape(m*n,1)
    points = squeeze(np.array(zip(x,y)))
    xvert,yvert = zip(*verts)
    points = np.ones((len(yvert),2))
    points[:,0] = xvert
    points[:,1] = yvert
    p = path.Path(points)
    inside = p.contains_points(points)
    inside = inside.reshape(m,n)
    return inside

