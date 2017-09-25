#!/usr/bin/env python
import sys
from StringIO import StringIO
import numpy as np
import pandas as pd
from numpy import maximum
from pandas import (Series,DataFrame, Panel,)
from pprint import pprint
from Utils import extractheader, outputmap

"""
This script does:
0. Convert road speed(miles/hour) map to road class types according to the roadspeedlist.txt mapping. A speed of 1 is given a class 0. 
1. Convert landuse class type map to landuse speed map according to the speedlist.txt mapping.
2. Convert road class type map to road speed map according to the speedlist.txt mapping.
3. Overlap the two maps by choosing the larger value to get the final speed map.
   Note the road class of 0 is assigned a speed of 1, and will be overwritten by landuse speed.
4. Convert landuse class type map to landuse dirprobmap according to the possibility.txt mapping.
5. Convert road class type map to road dirprobmap according to the possibility.txt mapping.
6. Overlap the two maps by choosing the larger value to get the final dirprob map.
   Note the road class of 0 is assigned a dirprob of 1, and will be overwritten by landuse dirprob.
"""

# input files
LANDCOVER='./Data/landuse.txt'    #ascii landuse class type map
ROAD='./Data/chicago_road2.txt'   #ascii road speed (miles/hour) map

# output files
SPEEDMAP="./Output/speedmap.txt"
DIRPROBMAP="./Output/dirprobmap.txt"
LANDROADCLASSMAP = "./Output/landroadclassmap.txt"

# mapping files
DIRPROBCHART = "./Data/possibilitylist.txt"
SPEEDCHART="./Data/speedlist.txt"
ROADSPEEDCHART="./Data/roadspeedlist.txt"

# export road speed class

HEADER = "./Output/arcGISheader.txt" 


def asciiMap2DataFrame(file):
    df = pd.read_csv(file, skiprows=6, header=None, sep=r"\s+")
    #return df.ix[0:10, 0:10]
    return df
    #if VERSION == "debug1":
    #    return df.ix[0:100, 50:88]
    #else:
    #    return df
def roadspeed2class(roadspeedmap, roadspeedchart, roadclassmap, headermap):
    """Replace values in original list not in the matrix to be None, and then replace
       all the catgory values with their corresponding speed value according to the
       provided speedchart. If the catgory is None, replace the speed with 0.
       @param: roadspeedmap has a default speed of 1.
               roadspeedchart is a file that has speed, class mapping pairs with one line header.
               roadclassmap is the file that road class map is exported to.
               It converts speed 1 to class 0.
       @output: road class type map with default class 0.
    """ 
    # speedchart2dict
    speedlist=[]
    classlist=[]
    with open(roadspeedchart, 'r') as f:
        next(f) #skip the header row
        for line in f:
            (speed, cat) = line.rstrip().split(',')
            speedlist.append(int(speed))
            classlist.append(int(cat))
    print speedlist
    print classlist
    matrix = asciiMap2DataFrame(roadspeedmap)
    matrix = matrix.where(matrix.isin(speedlist) == True, None)
    matrix = matrix.replace(to_replace=speedlist, value=classlist)

    with open(headermap, 'r') as h:
        header = h.read()
    with open(roadclassmap, 'w') as w:
        w.writelines(header)
    matrix.to_csv(path_or_buf=roadclassmap, sep=' ', index=False, header=False, mode = 'a') # append
    return matrix

def genlandroadclassmap(roadclassmap, landclassmap, header):
    # make the default class value to be a large number and then take
    # the minimum value of the maps.
    roadclassmap = roadclassmap.replace(to_replace=-1, value=999) 
    landroadclassmap = np.minimum(roadclassmap, landclassmap)
    
    outputmap(landroadclassmap, header, LANDROADCLASSMAP)

class SpeedMap:
    def __init__(self, landcover_matrix, road_matrix, speedchart, speedmap, header):
        self.cat_list = []
        self.speed_list = []
        self.projectioninfo_list = []
        # read the speedchart to be a speed dictionary
        self.speedchart2dict(speedchart)
        # replace the landcover catogory values with speed values
        self.landcoverspeed_matrix = self.cat2speedmap(landcover_matrix)
        self.roadspeed_matrix = self.cat2speedmap(road_matrix)
        self.finalspeed_matrix = self.overlapspeedmap(self.landcoverspeed_matrix, self.roadspeed_matrix)
        
        #self.landcoverspeed_matrix = self.landcoverspeed_matrix.apply(np.sqrt)
        outputmap(self.landcoverspeed_matrix, header, "./Data/landcoverspeedmap.txt")
    
    def speedchart2dict(self, speedchart):
    	"""Read the speedchart text file and convert it to be a catogory list and its corresponding
    	   speed list.
    	   @param: speedchart txt file with one header row, two columns: catgory values and speed values
    	"""
        with open(speedchart, 'r') as f:
            next(f) #skip the header row
            for line in f:
                (cat, speed) = line.split(',')
                #get rid of the \r\n appended to each speed
                speed = speed.split('\r\n')[0] 
                self.cat_list.append(int(cat))
                self.speed_list.append(int(speed))
    
    def cat2speedmap(self, matrix):
    	"""Replace the catgory values not in the matrix to be None, and then replace
    	   all the catgory values with their corresponding speed value according to the
    	   provided speedchart. If the catgory is None, replace the speed with 0.
    	   @param: matrix is the input map with all catgory values
    	   @output: matrix that has speed values corresponding to the input catgory values.
    	"""
        # if the catogory is not in the list, define the catgory to be np.nan.
        # print standard error and exit.
        checknull = matrix.where(matrix.isin(self.cat_list), np.nan)

        if (not pd.notnull(checknull).values.all()):
            sys.stderr.write("Error: At least one type has no corresponding speed or direction probability assigned.")
            wrong = matrix.where(matrix.isin(self.cat_list) == False, 0)
            self.outputspeedmap(wrong, LANDCOVER, "./Data/cat2speed_debug_" +str(ISEMP)+".txt" )
            exit(1)
        return matrix.replace(to_replace=self.cat_list, value=self.speed_list)

    def overlapspeedmap(self, matrix1, matrix2):
    	"""Overlap two speed maps by selecting the max value in either of the map.
    	   @param: matrix1 and matrix2 are two maps to be overlapped.
    	   @output: the max values of two matrixes.
    	"""
    	return np.maximum(matrix1, matrix2)

    def printdict(self, dict):
		for key, value in dict.iteritems():
			print str(key) + ":"+ str(value)
        
        
def main():
    
    #convert road speed map to road class type matrix
    roadclass_matrix = roadspeed2class(ROAD, ROADSPEEDCHART, ROADCLASSMAP, HEADER)
    landcover_matrix = asciiMap2DataFrame(LANDCOVER)

    # generate landroadclassmap
    header= extractheader(HEADER)
    genlandroadclassmap(roadclass_matrix, landcover_matrix, header)

    # generate speedmap and dirprobmap
    speedmap = SpeedMap(landcover_matrix, roadclass_matrix, SPEEDCHART, SPEEDMAP, header)
    dirprobmap = SpeedMap(landcover_matrix, roadclass_matrix, DIRPROBCHART, DIRPROBMAP, header)


if __name__ == "__main__":
	main()