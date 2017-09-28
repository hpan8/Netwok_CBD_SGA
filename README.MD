Required packages:

R

ggplot2

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

optparse 

matplotlib


Inputs and outpus data folder: ./Data

submission files to ROGER are stored in ./pbs 

the final speed map is saved in ./Data

the travel cost maps are saved in ./Data/costmaps

the graph drawing vectors are saved in "j_change" and "j_noch" for land-use change and existing land-use, respectively

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

#Interpolated_ATTRACTIVEMAP = "./Data/attrmap-emp.txt"

#Interpolated_ATTRACTIVEMAP = "./Data/attrmap-pop.txt"

python Data_Prepare.py

#read data from land_use maps (both change and existng)

#read data from attraction maps

#prepare the data in the format for curve fitting


#input:

LUDATA = "./Data/2011asc.txt"

LUCDATA = "./Data/2001_2011asc.txt"

POPDATA = "./Data/attrmap-pop.txt"

EMPDATA = "./Data/attrmap-emp.txt"

TRANSDATA = "./Data/attrmap-transport.txt"

BNDDATA = "./Data/chboundary.txt"

NOGODATA = "./Data/chnogrowth.txt"


#output:

RESOUT = "./Data/resout_0111.txt"

COMOUT = "./Data/comout_0111.txt"



#submission

#./pbs/rogersub


#argument: 

#-c 0 or 1 to stand for existing land-use map and land-use change map, respectively 


python Attach_rev_luc.py

# Attach luc and rev data to the current data_frame res_count.txt and com_count.txt


#input

LUDATA = "./LU_Maps/2011asc.txt"

LUCDATA = "./LU_Maps/2006_2011asc.txt"

OLD_LUCDATA = "./LU_Maps/2001_2006asc.txt"

REVDATA = "./Other_Maps/chi_rev.txt"

BNDDATA = "./Other_Maps/chboundary.txt"

NOGODATA = "./Other_Maps/chnogrowth.txt"

RESOUT = "./Output/resout_0111.txt"

COMOUT = "./Output/comout_0111.txt"


#output

RESOUT_R = "./Output/resout_rev_0111.txt"

COMOUT_R = "./Output/comout_rev_0111.txt"


#submission file

#./pbs/revsub


python Change_Graph.py

#use the lu and lu_change data matrix and matplotlib library to generate relational tables to prepare graph drawing in R


#input

RES_DATA = "./Data/resout_rev_0111.txt"

COM_DATA = "./Data/comout_rev_0111.txt"

#ouput

NO_CHANGE_DATA= "./j_noch/" + ["comemp", "compop", "comrev", "comtrans", "resemp", "respop",  "resrev", "restrans"] + ".csv"

CHANGE_DATA = "./j_change/" + ["comemp", "compop", "comrev", "comtrans", "resemp", "respop",  "resrev", "restrans"] + ".csv"


#argument 

#integer number for the numbers of quantile that the data are cut to (50 is used)

#-m type of attractors, can be "emp", "pop", "trans", "rev"


Rscript compare_loo.R

#compare leave_one_out errors of different types of functions to fit 

#attraction values and land-use class frequency


#input

NO_CHANGE_DATA= "./j_noch/" + ["comemp", "compop", "comrev", "comtrans", "resemp", "respop",  "resrev", "restrans"] + ".csv"

CHANGE_DATA = "./j_change/" + ["comemp", "compop", "comrev", "comtrans", "resemp", "respop",  "resrev", "restrans"] + ".csv"


#output are printed values of leave_one_out errors


Rscript Draw_freq_map.R

#Draw frequency maps based on smallest leave_one_out errors selected by compare_loo.R


#input

NO_CHANGE_DATA= "./j_noch/" + ["comemp", "compop", "comrev", "comtrans", "resemp", "respop",  "resrev", "restrans"] + ".csv"

CHANGE_DATA = "./j_change/" + ["comemp", "compop", "comrev", "comtrans", "resemp", "respop",  "resrev", "restrans"] + ".csv"


#output is figure 4 and figure 6 of the paper 