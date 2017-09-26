Required packages:
R

python 2.7
sys
StringIO
pandas
numpy
pprint
os
math
logging
time
multiprocessing
thread
scipy

Inputs and outpus data folder: ./Data
submission files to ROGER are stored in ./pbs 

the final speed map is saved in ./Data
the travel cost maps are saved in ./Data/costmaps

Input vector maps: ./Input/emp_centers5, ./Input/pop_center, ./Input/chicago_road2
Input raster map:  ./Input/landuse.gtif
Input speed chart: ./Input/speedlist.txt


Special thanks to ROGER Supercomputer.

############## Run program: #####################

python Utils.py
	#several functions easy to use for other program to call

python landcover2speedmap.py 
        #generate speedmap for each land_use class and probability map for SGA
 
        #input: 
	#DIRPROBCHART = "./Data/possibilitylist.txt"
	#SPEEDCHART="./Data/speedlist.txt"
	#ROADSPEEDCHART="./Data/roadspeedlist.txt"
	#LANDCOVER='./Data/landuse.txt'    #ascii landuse class type map
	#ROAD='./Data/chicago_road2.txt'   #ascii road speed (miles/hour) map

        #output: 
	#SPEEDMAP="./Data/speedmap.txt"
	#DIRPROBMAP="./Data/dirprobmap.txt"
	#LANDROADCLASSMAP = "./Data/landroadclassmap.txt"
	#HEADER = "./Data/arcGISheader.txt" 
        
        #Note that we need a default class -1 to have speed -1 in 
        #speedlist and possibilitylist for the speed 1 in roadspeedlist 
        #(a default useless speed that should get rid off).
        #Otherwise, there is an error message saying: some landuse type
        #missing in speedlist or possibility list.
        #This is due to the code design ==> take the
        #maximum of road matrix and landuse matrix.

python stocasticgreedy_randomwalk.py <vallessthan100> 
        #SGA algorithm; generate population or employment travel cost map based on 
        #population and employment centers list and output from landcover2speedmap.py 

        #argument: 
	#0 or 1 to stand for population and employment centers, respectively 

        #input:
	#SPEEDMAP = "./Data/speedmap.txt"
	#DIRPROBMAP = "./Data/dirprobmap.txt"
	#TRAVELCOSTMAP = "travelcostmap.txt"
	#HEADER = "./Input/arcGISheader.txt" 	
	#CENTERLIST="./Data/empcenterlist.txt"
	#CENTERLIST="./Data/popcenterlist.txt"

	#output:
	#TRAVELCOSTPATH = "./Data/costmaps-pop"
	#TRAVELCOSTPATH = "./Data/costmaps-emp"
	
	#submission file:
        #sh submitqsub to submit 10 jobs in queue to ROGER

python reducemaps.py
        #convert the 100 travelcost maps to attractive maps and
        #overlap the 100 maps using the weight of each attractive map.

        #argument: 
	#0 or 1 to stand for population and employment centers, respectively 
	
	#input:
	#SPEEDMAP = "./Data/speedmap.txt"
	#TRAVELCOSTMAP = "travelcostmap.txt"
	#HEADER = "./Input/arcGISheader.txt"
	#CENTERLIST = "./Data/empcenterlist.txt"
	#TRAVELCOSTPATH = "./Data/costmaps-emp"
	#CENTERLIST = "./Data/popcenterlist.txt"
	#TRAVELCOSTPATH = "./Data/costmaps-pop"

        #output:
	#ATTRACTIVEMAP = "./Data/attrmap-emp.txt"
	#ATTRACTIVEMAP = "./Data/attrmap-pop.txt"

python smoothcost.py
        #interpolate the attractive map attrmap-pop.txt to attrmap-pop-interpolated.txt
        #the interpolation is done for the center cell of each 5*5 cells except the side cells.
        #a distance to the center cell in the 5*5 cell is a weight parameter multilying to the
        #cell value and a penalty for each landuse type is exerted using the values in dirprobmap.txt

	#input:
	#CENTERLIST = "./Data/popcenterlist.txt"
	#TRAVELCOSTPATH = "./Data/costmaps-pop"
	#TRCOSTMAP = "./Data/costmap-pop.txt"
	#CENTERLIST = "./Data/empcenterlist.txt"
	#TRAVELCOSTPATH = "./Data/costmaps-emp"
	#TRCOSTMAP = "./Data/costmap-emp.txt"
	#HEADER="./Data/arcGISheader.txt"
	#TRAVELCOSTMAP = "travelcostmap.txt"
	#WEIGHTMAP = "./Data/weightmap-travelcost.txt"
	#SPEEDMAP = "./Data/speedmap.txt"

	#output:
	#Interpolated_POP="./Data/costmap-pop-interpolated.txt"
	#Interpolated_EMP="./Data/costmap-pop-interpolated.txt"
