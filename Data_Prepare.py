"""
This script will do:
1. read data from land_use maps (both change and existng)
2. read data from attraction maps
3. prepare the data in the format for curve fitting
"""

import sys
import numpy as np
import pandas as pd
from optparse import OptionParser
import gc
import os

os.chdir("/home/hpan8/LEAM_Calibration/Data_Prepare/")

LUDATA = "./Data/2011asc.txt"
LUCDATA = "./Data/2006_2011asc.txt"

POPDATA = "./Data/attrmap-pop.txt"
EMPDATA = "./Data/attrmap-emp.txt"
TRANSDATA = "./Data/attrmap-transport.txt"
BNDDATA = "./Data/chboundary.txt"
NOGODATA = "./Data/chnogrowth.txt"

RESOUT = "./Data/resout_0611.txt"
COMOUT = "./Data/comout_0611.txt"


'''
Deciding change LU or exsting LU
'''
def opt_parser():

    parse = OptionParser()
    #attraction map option
    parse.add_option('-c', '--change', metavar='CENTERTYPE', default=False,
                    help='1 for change and 0 for no change') # change or existing option

    opts, args = parse.parse_args()
    ischg = 0
    opts, args = parse.parse_args()
    if not opts.change:
        ischg = 0
        print "No change or existing given. Default to be no change"
    elif opts.change == "0":
        ischg = 0
    elif opts.change == "1":
        ischg = 1
    else:
        parse.error("-c option needs to be either 1 or 0")

    return ischg

'''
Load Data
'''
def data_loader(ischg):
    if ischg == 0:
        lu_data = pd.read_csv(LUDATA, sep=r"\s+", skiprows=6, header=None)
    else:
        lu_data = pd.read_csv(LUCDATA, sep=r"\s+", skiprows=6, header=None)

    pop_data = pd.read_csv(POPDATA, sep=r"\s+", skiprows=6, header=None)
    emp_data = pd.read_csv(EMPDATA, sep=r"\s+", skiprows=6, header=None)
    trans_data = pd.read_csv(TRANSDATA, sep=r"\s+", skiprows=6, header=None)
    bnd_data = pd.read_csv(BNDDATA, sep=r"\s+", skiprows=6, header=None)
    nogo_data = pd.read_csv(NOGODATA, sep=r"\s+", skiprows=6, header=None)
    luo_data = pd.read_csv(LUDATA, sep=r"\s+", skiprows=6, header=None)
    lu_row = bnd_data.shape[0]
    lu_col = bnd_data.shape[1]

    with open(LUDATA) as myfile:
        head = [next(myfile) for x in xrange(6)]

    return {'lu': lu_data, 'pop': pop_data, 'emp': emp_data, 'trans': trans_data, 'luo': luo_data,
            'bnd': bnd_data, 'nogo': nogo_data, 'head': head,
            'row': lu_row, 'col': lu_col}

'''
create mask so that the model only cares about developable cells
'''
def mask_data(lu_data, ischng, bnd, no_growth, row, col):
    gc.collect()
    g_mask = np.zeros(row * col, dtype=int)
    #g_mask = pd.DataFrame(g_mask)
    if ischng == 0:
        urb_class = np.array([24, 11, 90, 95])  # non-developable water LU class
    else:
        urb_class = np.array([1, 2, 200, 723])

    '''
    a lot of nonsense are used to save memory
    '''
    lu = lu_data

    lu = lu.as_matrix()
    lu = lu.astype(int)
    print lu.itemsize
    lu = lu.ravel()

    u_mask = np.in1d(lu, urb_class)  # creating mask of exiting development
    #u_mask = u_mask.reshape((row, col))
    #g_mask.values.flatten()
    g_mask[u_mask] = 1

    gc.collect()
    boundary = bnd.as_matrix()
    boundary = boundary.astype(int)
    boundary = boundary.ravel()
    g_mask[boundary != 1] = 1

    gc.collect()
    no_go = no_growth.as_matrix()
    no_go = no_go.astype(int)
    no_go = no_go.ravel()
    g_mask[no_go == 1] = 1

    print g_mask.shape
    print boundary.shape
    print no_go.shape
    print u_mask.shape
    return g_mask

'''
throw away first and last 2% of the data unique values
'''
def head_cut(input_data):
    uni_data = np.unique(input_data)
    len_unique = len(uni_data)
    #num_cut = int(np.floor((len_unique-1)/50))
    #st_data = np.sort(uni_data)

    low_cut = max(1, uni_data[2])
    if len_unique > 6:
    	high_cut = uni_data[(len_unique-3)]
    else:
        high_cut = uni_data[-1]
    output_data = input_data
    print len(uni_data)
    print low_cut
    print high_cut
    gc.collect()
    output_data[np.where(output_data < low_cut)] = low_cut
    output_data[np.where(output_data > high_cut)] = high_cut

	
    return output_data


def all_neighbors(luo_data):
    aaa

def get_one_neighbor(dist):
    aaa

'''
prepare data into columns
'''
def data_prepare(lu_col):

    siz = len(lu_col)

    res_class = [21, 22] #creating responses. Change/existing res = 1, other = 0. Same for com
    res_mask = np.in1d(lu_col, res_class)
    response_col = np.zeros(siz)
    response_col[res_mask] = 1
    #response_col[np.logical_not(res_mask)] = 0


    com_class = [23, 101]
    com_mask = np.in1d(lu_col, com_class)
    componse_col = np.zeros(siz)
    componse_col[com_mask] = 1
    #componse_col[np.logical_not(com_mask)] = 0
     
    print "mask", np.array_equal(res_mask, com_mask)
    print "col", np.array_equal(response_col, componse_col)

    return {'response': response_col, 'componse': componse_col}

'''
Assemble vectors into Pandas DF
'''
def output_df(pop_col, emp_col, trans_col, slope_col, out_col):
    #comnames = np.array(["pop", "emp", "trans", "response_col"])
    #resnames = np.array(["pop", "emp", "trans", "componse_col"])
    #v_size = len(pop_col)
    #colnames = range(v_size)
    out_df = pd.DataFrame({"pop": pop_col, "emp": emp_col, "trans": trans_col,
                           "response": out_col})

    return out_df

'''
I write in this long way because windows pycharm sucks in memory!
'''
def main():
    ischg = opt_parser()


    dict = data_loader(ischg)
    [lu_data, pop_data, emp_data, trans_data, luo_data,  bnd_data, nogo_data, row, col] = \
        [dict.get(k) for k in ('lu', 'pop', 'emp', 'trans', 'luo', 'bnd', 'nogo', 'row', 'col')]

    g_mask = mask_data(lu_data, ischg, bnd_data, nogo_data, row, col)

    gc.collect()

    lu_data = lu_data.as_matrix()
    lu_data = lu_data.ravel()
    lu_data = lu_data[g_mask == 0]

    gc.collect()

    pop_data = pop_data.as_matrix()
    pop_data = pop_data.astype(int)
    pop_data = pop_data.ravel()
    pop_data = pop_data[g_mask == 0]
    pop_data = head_cut(pop_data)

    gc.collect()

    emp_data = emp_data.as_matrix()
    emp_data = emp_data.ravel()
    emp_data = emp_data[g_mask == 0]
    emp_data = head_cut(emp_data)

    gc.collect()

    trans_data = trans_data.as_matrix()
    trans_data = trans_data.ravel()
    trans_data = trans_data[g_mask == 0]
    trans_data = head_cut(trans_data)

    gc.collect()
    dict = data_prepare(lu_data)
    [response_col, componse_col] = [dict.get(k) for k in ('response', 'componse')]

    gc.collect()
    res_df = output_df(pop_data, emp_data, trans_data, response_col)
    res_df.to_csv(RESOUT)

    gc.collect()
    com_df = output_df(pop_data, emp_data, trans_data, componse_col)
    com_df.to_csv(COMOUT)


if __name__ == "__main__":
    main()
