import pandas as pd
import numpy as np
import time
from scipy.interpolate import griddata
from multiprocessing.dummy import Pool

from Utils import extractheader, outfilename

"""
Time consumption for 64 threads and 1 repeattime: 12min
Time consumption for 64 threads and 2 repeattime: 24min
Time consumption for 32 threads and 2 repeattime: 23min
Time consumption for no thread  and 1 repeattime with landuse type considered: 4min!!!
"""
ISEMP = 1
REPEATNUM = 5
# INPUT="testmap2"
# OUTPUT="testmapout"

if ISEMP == 0:
    INPUT="./Data/costmap-pop.txt"
    OUTPUT="./Data/costmap-pop-interpolated.txt"
    CENTERLIST = "./Data/popcenterlist.txt"
    TRAVELCOSTPATH = "./Data/costmaps-pop"
    TRCOSTMAP = "./Data/costmap-pop.txt"
else:
    INPUT="./Data/costmap-emp.txt"
    OUTPUT="./Data/costmap-emp-interpolated.txt"
    CENTERLIST = "./Data/empcenterlist.txt"
    TRAVELCOSTPATH = "./Data/costmaps-emp"
    TRCOSTMAP = "./Data/costmap-emp.txt"
    

HEADER="./Data/arcGISheader.txt"
TRAVELCOSTMAP = "travelcostmap.txt"
WEIGHTMAP = "./Data/weightmap-travelcost.txt"
SPEEDMAP = "./Data/speedmap.txt"
CELLSIZE = 30
COSTMAX = 999
#THREADNUM = 32

def gettravelcostmap(nrows, ncols, header, CENTERLIST=CENTERLIST, COSTMAX=COSTMAX, 
                               TRAVELCOSTPATH=TRAVELCOSTPATH, TRAVELCOSTMAP=TRAVELCOSTMAP):
    """Generate travelcost map by overlapping the 100 pop/emp center travelcost maps
       and obtain the minimal value of each cell in these 100 maps.
       This process takes several minutes.
       @param: nrows is # rows and ncols is # columns of travelcostmaps.
       @output: the overlapped minimal value travelcostma
       Time consumption: 3.5min
    """
    with open(CENTERLIST, 'r') as p:
        centerlist = p.readlines()
     
    trcostdf = pd.DataFrame(index=xrange(nrows), columns=xrange(ncols)) #initialize costmap with nan
    trcostdf = trcostdf.fillna(COSTMAX)    #initialize costmap with 999

    for i in xrange(99):
        (disW, disN, weight) = centerlist[i].strip('\n').split(',')
        costmapfile = outfilename(disW, disN, TRAVELCOSTPATH, TRAVELCOSTMAP, "NW", 100)
        try:
            newtrcostdf = pd.read_csv(costmapfile, skiprows=6, header=None, sep=r"\s+" ) #skip the 6 header lines
            print disW, disN, weight
        except IOError:
            print "file not found: ", costmapfile
            continue
        trcostdf = np.minimum(trcostdf, newtrcostdf)
      
    # header = extractheader(HEADER)
    with open(TRCOSTMAP, 'w') as w:
        w.writelines(header)
    trcostdf.round() # round to integer
    trcostdf.to_csv(path_or_buf=TRCOSTMAP, sep=' ', index=False, header=False, mode = 'a') # append
    return trcostdf


class SmoothCost():
    """Time consumption: 9min
    """
    def __init__(self, matrix, weightarray, speed_df, costmax=COSTMAX, cellsize=CELLSIZE, repeattimes=REPEATNUM):
        start = time.time()
        self.weightarray = weightarray
        self.matrix = matrix
        (self.rows, self.cols) = matrix.shape
        self.maxrow = self.rows-2
        self.maxcol = self.cols-2
        self.cellsize = cellsize
        self.costmax = costmax
        self.speed_df = speed_df
        self.smoothedmap = np.zeros((self.rows, self.cols), dtype=np.int)
        self.smoothedmap.fill(999)
        self.smooth2min(repeattimes)

    def smoothrow(self, rowidx):
        """This function assigns the center of 5*5 cells a value that equals to the sum of all cells having larger values multiplying by
           a weight. The weight is read from the input weightmap and has a value propotional to the distance to the center cell. Repeat 
           the steps for all cells of the row with rowidx in the attrmap matrix.
           @param: rowidx is the row index of the attrmap matrix.
           @output: the smoothedmap filled with row index of rowidx.
        """
        if rowidx < 2 or rowidx >= self.maxrow:
            return
        #debug: print "rowidx: ", rowidx , "==========="
        for colidx in xrange(2, self.maxcol): # for each cell in a row
            #debug: print "colidx: ", colidx, "-----------"
            if self.matrix[rowidx][colidx] < self.costmax:
                continue
            matrix_arr = self.matrix[rowidx-2:rowidx+3, colidx-2:colidx+3].flatten()
            minindex   = np.argmin(matrix_arr)
            minval     = matrix_arr[minindex]
            # print "--------------"
            # print "cur val:", self.matrix[rowidx][colidx]
            # print "minindex", minindex
            # print "minval: ", minval
            # print "### len weightarray ", len(self.weightarray)
            weight     = self.weightarray[minindex]
            speed      = self.speed_df.ix[rowidx, colidx]
            # print "speed: ", speed
            # print "weight: ", weight 
            # print "final: ", minval + self.cellsize*weight/speed
            if weight == 0 or speed == 0:
                self.smoothedmap[rowidx][colidx] = self.matrix[rowidx][colidx]
            else:
                self.smoothedmap[rowidx][colidx] = minval + self.cellsize*weight/speed
        
    def smooth2min(self, repeattimes):
        """smooth2min creates THREADNUM number of threads to parallell smoothing each row of the attrmap matrix.
            As the two side columns and rows are not smoothed in the attrmap, overlay the original map and smoothedmap
            can obtain the original attrativenesss score for the side columns and rows. Also, cells that decreases its
            values due to rounding to int can have the original higher values back.
        """
        for i in xrange(repeattimes):
            #pool = Pool(THREADNUM)
            #pool.map(self.smoothrow, xrange(self.rows))
			
            #debug:
            for rowidx in xrange(self.rows):
               self.smoothrow(rowidx)
            self.matrix = np.minimum(self.smoothedmap, self.matrix)
        self.smoothedmap = self.matrix

def outputmap(attrmap, header, output):
    with open(output, 'w') as f:
        f.writelines(header)
        np.savetxt(f, attrmap, fmt='%d',delimiter=' ')

def main():
    
    header = extractheader(HEADER)
    speed_df = pd.read_csv(SPEEDMAP, sep=' ', skiprows=6, header=None, dtype=np.int)

    (nrows, ncols) = speed_df.shape
    travelcostmap  = gettravelcostmap(nrows, ncols, header)
    
    costmap_df = pd.read_csv(INPUT, sep=' ', skiprows=6, header=None, dtype=np.float)
    costmap = np.asarray(costmap_df).round()
    weightarray = np.fromfile(WEIGHTMAP, sep=' ', dtype=np.float)
    
    
    smoothcost = SmoothCost(costmap, weightarray, speed_df)
    costmap = smoothcost.smoothedmap

    
    outputmap(costmap, header, OUTPUT)

if __name__ == "__main__":
	main()