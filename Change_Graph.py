"""
This script will do:
1. use the lu_change data matrix and matplotlib library and ggplot2 to generate relational graphs

"""

# from ggplot import * #ggplot is best to be used with pandas DataFrames
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from optparse import OptionParser
import time
import os
import math


os.chdir("/home/hpan8/LEAM_Calibration/Data_Prepare/") #this is for run on ROGER

# if (len(sys.argv) < 3):
#    print "Error: You need to specify at least two arguments: #attrmap baskets and #costmap baskets."
#    exit(1)

# option parsers to decide which column to read from data
RES_DATA = "./Output/resout_rev_0611.txt"
COM_DATA = "./Output/comout_rev_0611.txt"


def opt_parser():
    parse = OptionParser()
    parse.add_option('-m', '--maptype', metavar='MAPTYPE', default=False,
                     help='the map type can be "emp", "pop", "slope", "trans", "rev" ')

    isemp = 0
    opts, args = parse.parse_args()
    opts_c = opts.maptype
    if not opts.maptype:
        opts_c = 'emp'
        print "No centertype given. Default to be emp"
    elif opts.maptype == 'emp':
        opts_c = 'emp'
        isemp = 0
    elif opts.maptype == 'pop':
        opts_c = 'pop'
        isemp = 1
    elif opts.maptype == 'slope':
        opts_c = 'slope'
        isemp = 2
    elif opts.maptype == 'trans':
        opts_c = 'trans'
        isemp = 3
    elif opts.maptype == 'rev':
        opts_c = 'rev'
        isemp = 4
    else:
        parse.error("-c option needs to be  'emp', 'pop', 'slope'', 'trans', 'rev' ")

    attrbasketnum = int(sys.argv[1])  # number of tick bins

    return {'bnum': attrbasketnum, 'maptype': opts_c}


# Data loader
def data_loader(maptype):
    res_data = pd.read_csv(RES_DATA)
    com_data = pd.read_csv(COM_DATA)
    
    res_data = res_data.drop(0, axis = 1)
    res_data = res_data.drop(0, axis = 1) # drop redundent indexes
    res_data = res_data.drop(res_data[res_data.chg == -1].index)

    com_data = com_data.drop(0, axis = 1)
    com_data = com_data.drop(0, axis = 1) # drop redundent indexes
    com_data = com_data.drop(com_data[com_data.chg == -1].index)

    res_x = res_data[maptype] #read specific columns from input data
    res_y = res_data['chg']

    com_x = com_data[maptype]  # read specific columns from input data
    com_y = com_data['chg']

    res_x = res_x[~np.isnan(res_x)]
    res_y = res_y[~np.isnan(res_y)]
    com_x = com_x[~np.isnan(com_x)]
    com_y = com_y[~np.isnan(com_y)]
    
    print 'res_x', res_x.shape
    print 'res_y', res_y.shape
    print 'com_x', com_x.shape
    print 'com_y', com_y.shape



    # sort the arrays (ascending)

    arrinds = np.argsort(res_x)
    res_x = res_x[arrinds]
    res_y = res_y[arrinds]

    arrinds = np.argsort(com_x)
    com_x = com_x[arrinds]
    com_y = com_y[arrinds]


    return {'res_x': res_x, 'res_y': res_y, 'com_x': com_x, 'com_y': com_y}


# naming graphs
def graph_names(luname, maptype):
    outmapename = "./Output_Change_0611/" + luname + maptype + ".png"
    outdataname = "./Output_Change_0611/" + luname + maptype + ".csv"

    return {'outmapename': outmapename, 'outdataname': outdataname}


# change y label to percent
def to_percent(y, position):
    """[reference:http://matplotlib.org/examples/pylab_examples/histogram_percent_demo.html]
    """
    s = str(100 * y)

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'


# plot graph
def plotgraph(x, y, outfile, luname, mapname):
    plt.close("all")
    plt.ioff()
    fig, ax = plt.subplots()
    # set the grids of the x axis
    # When data are highly skewed, the ticks value needs to be
    # set differently for different number of baskets.
    major_ticks = xrange(0, int(x[-1] + x[-1] - x[-2]), max(1, int((x[-1] + x[-1] - x[-2]) / 10)))
    minor_ticks = xrange(0, int(x[-1] + x[-1] - x[-2]), max(1, int((x[-1] + x[-1] - x[-2]) / 100)))

    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    # set the range of the y axis
    plt.ylim(0, 1)
    # set the title and labels
    plt.title(luname + ' ' + mapname + ' Frequency Distribution')
    plt.xlabel(mapname + ' Score')
    plt.ylabel('Fraction ' + luname + ' Over All Landuse Type ' + mapname + ' Frequency')
    # set the y axis values to be 100% times.
    formatter = FuncFormatter(to_percent)
    plt.gca().yaxis.set_major_formatter(formatter)

    # plot the graph and pinpoint the max y value point
    x = np.insert(x, 0, 0)  # if not this, x will be shorter than y
    plt.plot(x, y, 'ro--')
    ymax_index = np.argmax(y)
    ymax = y[ymax_index]
    ymax_xval = x[ymax_index]
    plt.scatter(ymax_xval, ymax * 100)
    plt.grid(True)

    # save the figure to file
    plt.savefig(outfile)  # cut 10 percentile tail and head values


# csv output
def write_data(x, y, outfile):
    x = np.insert(x, 0, 0)  # if not this, x will be shorter than y
    outdata_arr = np.asarray([x, y])
    outdata_arr = np.transpose(outdata_arr)
    np.savetxt(outfile, outdata_arr, fmt='%5.5f', delimiter=',',
               header="x,y", comments='')


# cut 5 percentile tail and head values, and mask the residential array
def x_ticks(res_x, bnum):
    # create unique arrays from the attribute array
    #res_x = res_x * 100000
    attr_uni = np.unique(res_x)
    attr_uni = attr_uni[~np.isnan(attr_uni)]
    print 'attr_uni', attr_uni

    # create x axis values
    attr_arr_len = len(attr_uni)
    attrbasketsize = attr_arr_len / bnum
    attr_arr_sort = np.sort(attr_uni)
    tick_x = attr_arr_sort[0:attr_arr_len - 1:attrbasketsize]  # the x axis tick values
    tick_x = tick_x[0:bnum + 1]  # merge the last basket to the previous one
    tick_x = np.unique(tick_x)
    print tick_x
    print tick_x.shape

    return tick_x


# analyze frequency at each quantile cutoff
def frequencyanalysis_attr(res_x, res_y, tick_x):
    xlen = len(tick_x)
    # attr_res_arr_nb         = attr_res_arr[attr_res_arr > ATTRBASE]
    print " CELLS CONSIDERED: ", sum(res_y)
    # attr_arr_sort     = np.sort(attr_res_arr)
    # attr_res_basketsize_1st = len(attr_res_arr[attr_res_arr == ATTRBASE])
    # attr_basketsize_1st      = len(attr_arr    [attr_arr     == ATTRBASE])
    attr_res_freq = []  # frequency array for residential cells
    attr_arr_freq = []  # frequency array for all cells
    cur1 = tick_x[0]  # initialize lower bound of the cutoff

    # calculate the first basket
    mask = (res_x >= 0) & (res_x <= cur1)  # residential cells with values within the cutoff
    attr_res_freq.append(sum(res_y[mask]))  # add new residential frequency to the frequency array
    attr_arr_freq.append(len(res_x[mask]))  # add all cells frequency to the frequency array

    for i in np.arange(1, xlen):  # i is for cur2. in total ATTRBASKETNUM baskets.
        cur2 = tick_x[i]  # upper boundary of the cutoff
        mask = (res_x >= cur1) & (res_x <= cur2)  # residential cells with values within the cutoff
        attr_res_freq.append(sum(res_y[mask]))  # add new residential frequency to the frequency array
        attr_arr_freq.append(len(res_x[mask]))  # add all cells frequency to the frequency array
        cur1 = cur2  # update lower bound of the cutoff

    attr_res_freq.append(sum(res_y[res_x >= cur1]))  # add final cuoff values
    attr_arr_freq.append(len(res_x[res_x >= cur1]))  # add final cutoff values

    print "---------------------attr_res_freq----------------\n", [int(i) for i in attr_res_freq]  # print res frequency
    print "---------------------attr_arr_freq----------------\n", [int(i) for i in
                                                                   attr_arr_freq]  # print total frequency
    attr_res_y = np.divide(attr_res_freq, attr_arr_freq, dtype=np.float)  # calculate y values on the axis
    attr_res_y = np.nan_to_num(attr_res_y)  # eliminate nan values
    print "---------------------attr_y----------------\n", attr_res_y  # print y values
    return {'attr_res_y': attr_res_y, 'xlen': xlen}


def main():
    dict = opt_parser()
    [m_bnum, m_maptype] = [dict.get(k) for k in ('bnum', 'maptype')]

    dict = data_loader(m_maptype)
    [m_res_x, m_res_y, m_com_x, m_com_y] = [dict.get(k) for k in ('res_x', 'res_y','com_x','com_y')]
    

    m_res_tick = x_ticks(m_res_x, m_bnum)
    m_com_tick = x_ticks(m_com_x, m_bnum)

    dict = frequencyanalysis_attr(m_res_x, m_res_y,m_res_tick)
    [m_attr_res_y, m_res_len] = [dict.get(k) for k in ('attr_res_y', 'xlen')]

    dict = frequencyanalysis_attr(m_com_x, m_com_y, m_com_tick)
    [m_attr_com_y, m_com_len] = [dict.get(k) for k in ('attr_res_y', 'xlen')]



    dict = graph_names('res', m_maptype)
    [m_gres, m_dres] = [dict.get(k) for k in ('outmapename', 'outdataname')]

    dict = graph_names('com', m_maptype)
    [m_gcom, m_dcom] = [dict.get(k) for k in ('outmapename', 'outdataname')]

    plotgraph(m_res_tick, m_attr_res_y, m_gres, 'res_chg', m_maptype)
    write_data(m_res_tick, m_attr_res_y, m_dres)

    plotgraph(m_com_tick, m_attr_com_y, m_gcom, 'com_chg', m_maptype)
    write_data(m_com_tick, m_attr_com_y, m_dcom)


if __name__ == "__main__":
    if (len(sys.argv) < 1):
        print "Required: Arg1 ATTRBASKETNUM"
        exit(1)
    main()

