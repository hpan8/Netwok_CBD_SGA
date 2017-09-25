#!/usr/bin/env python
#from StringIO import StringIO
import numpy as np
import pandas as pd
import math
import os
import time
from numpy import maximum
from pandas import DataFrame
from pprint import pprint
import multiprocessing
import thread

from Utils import extractheader, outfilename, outputmap

"""
This script will do:
1) convert costmap for each pop/emp center into attractive map
2) overlap 100 attractive maps according to their weights
3) round all float values to integers
Time consumption: 4min
"""

ISEMP = 1

if ISEMP == 1:
    CENTERLIST = "./Data/empcenterlist.txt"
    TRAVELCOSTPATH = "./Data/costmaps-emp"
    ATTRACTIVEMAP = "./Data/attrmap-emp.txt"
else:
    CENTERLIST = "./Data/popcenterlist.txt"
    TRAVELCOSTPATH = "./Data/costmaps-pop"
    ATTRACTIVEMAP = "./Data/attrmap-pop.txt"

SPEEDMAP = "./Data/speedmap.txt"
TRAVELCOSTMAP = "travelcostmap.txt"
HEADER = "./Input/arcGISheader.txt"
ATTRBASE = 20

                        
def costmap2attrmap(costmap):
    try:
        costmatrix = pd.read_csv(costmap, skiprows=6, header=None, sep=r"\s+" ) #skip the 6 header lines
        #costmatrix.replace(to_replace=0.0, value=0.001)
    except IOError as e:
        raise e
        return costmatrix

    # add a base attractiveness to every cell to avoid the attractivenss
    # to go infinite when cost goes to zero
    attmatrix = 1/(costmatrix + ATTRBASE)
    #pprint(attmatrix)
    return attmatrix

def main():
    speedmap = pd.read_csv(SPEEDMAP, skiprows=6, header=None, sep=r"\s+")
    header = extractheader(HEADER)
    attinxcol = speedmap.shape
    indexlen = attinxcol[0]
    columnlen = attinxcol[1]
    attrmap = pd.DataFrame(index=range(indexlen), columns=range(columnlen)) #initialize costmap with nan
    attrmap = attrmap.fillna(0)    #initialize costmap with 0

    with open(CENTERLIST, 'r') as p:
        centerlist = p.readlines()

    for i in range(99):
        (disW, disN, weight) = centerlist[i].strip('\n').split(',')
        costmapfile = outfilename(disW, disN, TRAVELCOSTPATH, TRAVELCOSTMAP, "NW", 100)
        try:
           newattrmap = costmap2attrmap(costmapfile)
        except IOError:
            print "file not found: ", outfilename
            continue
        print "\nstart adding...\n"
        start = time.time()
        attrmap = attrmap + (int)(weight)*newattrmap
        end = time.time()
        print "done map using time: "
        print (end-start)

    #normalizer = np.matrix(attrmap).max()
    #attrmap /= normalizer
    attrmap.round() # round to integer
    outputmap(attrmap, header, ATTRACTIVEMAP)

if __name__ == "__main__":
    main()
    