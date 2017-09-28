"""
This script will do:
1. Attach luc and rev data to the current data_frame res_count_new.txt and com_count_new.txt

"""

import sys
import numpy as np
import pandas as pd
import matplotlib
from optparse import OptionParser
import gc
import os

os.chdir("/home/hpan8/LEAM_Calibration/Data_Prepare/")


LUDATA = "./LU_Maps/2011asc.txt"
LUCDATA = "./LU_Maps/2006_2011asc.txt"
OLD_LUCDATA = "./LU_Maps/2001_2006asc.txt"

REVDATA = "./Other_Maps/chi_rev.txt"


BNDDATA = "./Other_Maps/chboundary.txt"
NOGODATA = "./Other_Maps/chnogrowth.txt"

RESOUT = "./Output/resout_0111.txt"
COMOUT = "./Output/comout_0111.txt"

RESOUT_R = "./Output/resout_rev_0111.txt"
COMOUT_R = "./Output/comout_rev_0111.txt"




'''
Load Data
'''
def data_loader():

    lu_data = pd.read_csv(LUDATA, sep=r"\s+", skiprows=6, header=None)
    bnd_data = pd.read_csv(BNDDATA, sep=r"\s+", skiprows=6, header=None)
    nogo_data = pd.read_csv(NOGODATA, sep=r"\s+", skiprows=6, header=None)
    luc_data = pd.read_csv(LUCDATA, sep=r"\s+", skiprows=6, header=None)
    old_luc_data =  pd.read_csv(OLD_LUCDATA, sep=r"\s+", skiprows=6, header=None)

    rev_data = pd.read_csv(REVDATA, sep=r"\s+", skiprows=6, header=None)

    res_or_data = pd.read_csv(RESOUT)
    com_or_data = pd.read_csv(COMOUT)

    lu_row = bnd_data.shape[0]
    lu_col = bnd_data.shape[1]

    with open(LUDATA) as myfile:
        head = [next(myfile) for x in xrange(6)]

    return {'lu': lu_data, 'luc': luc_data, 'res_or': res_or_data, 'com_or': com_or_data, 'rev': rev_data, 'oluc': old_luc_data, 
            'bnd': bnd_data, 'nogo': nogo_data, 'head': head,
            'row': lu_row, 'col': lu_col}

'''
create mask so that the model only cares about developable cells
'''
def mask_data(lu_data, bnd, no_growth, row, col):
    gc.collect()
    g_mask = np.zeros(row * col, dtype=int)
    #g_mask = pd.DataFrame(g_mask)
    urb_class = np.array([24, 11, 90, 95])  # non-developable water LU class


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
throw away first and last 5% of the data unique values
'''
def head_cut(input_data):
    uni_data = np.unique(input_data)
    len_unique = len(uni_data)
    num_cut = int(np.floor(len_unique/20))
    st_data = np.sort(input_data)

    low_cut = st_data[(num_cut-1)]
    high_cut = st_data[num_cut]
    output_data = input_data

    gc.collect()
    output_data[output_data < low_cut] = low_cut
    output_data[output_data > high_cut] = high_cut

    return output_data

'''
prepare data into columns
'''
def data_prepare(luc_col, old_data):
    
    siz = len(luc_col)

    res_c_class = [1021, 1022] #creating responses. Change res = 1, no change = 0, other = -1
    res_n_class = [1, 2, 200, 300] # other
    res_c_mask = np.in1d(luc_col, res_c_class)
    res_n_mask = np.in1d(old_data, res_n_class)
    old_res_mask = np.in1d(old_data, res_c_class)
    response_col = np.zeros(siz)
    response_col[res_c_mask] = 1
    response_col[old_res_mask] = 1
    response_col[res_n_mask] = -1
    #response_col[~(res_n_mask | res_c_mask)] = 0


    
    com_c_class = [1023]  # creating responses. Change com = 1, no change = 0, other = -1
    com_n_class = [1, 2, 200, 300]
    com_c_mask = np.in1d(luc_col, com_c_class)
    com_n_mask = np.in1d(old_data, com_n_class)
    old_com_mask = np.in1d(old_data, com_c_class)
    componse_col = np.zeros(siz)
    componse_col[com_c_mask] = 1
    componse_col[old_com_mask] = 1
    componse_col[com_n_mask] = -1
    #componse_col[~(com_n_mask | com_c_mask)] = 0

    return {'response': response_col, 'componse': componse_col}


'''
I write in this long way because windows pycharm sucks in memory!
'''
def main():

    dict = data_loader()
    [lu_data, luc_data, old_data, res_data, com_data, bnd_data, nogo_data, rev_data, row, col] = \
        [dict.get(k) for k in ('lu', 'luc', 'oluc', 'res_or', 'com_or', 'bnd', 'nogo', 'rev', 'row', 'col')]

    g_mask = mask_data(lu_data, bnd_data, nogo_data, row, col)

    gc.collect()

    luc_data = luc_data.as_matrix()
    luc_data = luc_data.astype(int)
    luc_data = luc_data.ravel()
    luc_data = luc_data[g_mask == 0]

    old_data = old_data.as_matrix()
    old_data = old_data.astype(int)
    old_data = old_data.ravel()
    old_data = old_data[g_mask == 0]
    
    rev_data.to_csv(path_or_buf="./Output/revtest.txt")
    rev_data = rev_data.astype(np.float)
    rev_data.to_csv(path_or_buf="./Output/revtest5.txt")
    rev_data = rev_data * 100000
    rev_data = rev_data.as_matrix()
    np.savetxt("./Output/revtest3.txt", rev_data, delimiter=",")
    rev_data = rev_data.flatten()
    np.savetxt("./Output/revtest2.txt", rev_data, delimiter=",")
    rev_data = rev_data[g_mask == 0]


    gc.collect()
    dict = data_prepare(luc_data, old_data)
    [response_col, componse_col] = \
    [dict.get(k) for k in ('response', 'componse')]



    gc.collect()

    res_data['chg'] = response_col
    res_data['rev'] = rev_data
    com_data['chg'] = componse_col
    com_data['rev'] = rev_data

    res_data.to_csv(path_or_buf=RESOUT_R)
    com_data.to_csv(path_or_buf=COMOUT_R)

if __name__ == "__main__":
    main()