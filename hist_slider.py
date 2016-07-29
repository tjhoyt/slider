import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons


#methods = ["Cepheids": "yellow", "TRGB": "orange", "RR Lyrae"]
#keys = ["exclusion code", "record index", "object index", "object name","dm",
#"dmerr","distance","method","refcode","SN ID","z","h0","LMCmod","date","notes"]


colors = ["red", "blue", "yellow"]
#colors2 = ["green", "yellow", "cyan"]
#alphas = [1.0, 0.60, 0.80]

infile = 'm031_ce_tr_rr.txt'
with open(infile) as json_data:
    d = json.load(json_data)
    json_data.close()

methods = list(set([x['method'] for x in d]))
print(methods)
#########################################################################
################################ FUNCTIONS ##############################
#########################################################################


def obj_filter(r, o):
    n = r['object name']
    if n == o or n == o.replace(" ","") or n == o.lower() or n == o.upper():
        return r 

def get_dm(r): # need separate get_dm function bc of the replacement 
    d = r['LMCmod']
    if d == "":
        return 18.5
    else: return d
    
def get_val(r, key):
    '''
    Check if user looking for the LMCmod value
    then branch from there
    
    '''
    val = r[key]
    if key == 'LMCmod':
        if val == "":
            return 18.5
        else:
            return val
    else:
        return val
    
def check_for(d, key, val):
    '''
    Simply returns True if the given value exists 
    under a certain key in the given dict. Do this
    instead of plain existence because each key 
    might not have mutually exclusive values!
    '''
    if d[key] == val or d[key] == val.replace(" ","") or d[key] == val.lower() or d[key] == val.upper():
        return True
    
def slice_intersect(sli1, sli2, sli3):
    sli = []
    for i, j, k in zip(sli1, sli2, sli3):
        if i and j and k:
            sli.append(True)
        else:
            sli.append(False)
    return sli

def slice(d, dLo, dHi):
    '''
    d: data to slice

    dLo: lower limit to place on d

    dHi: upper limit to place on d

    Returns:

    indices: list of indices corresponding to
    desired data
    '''
    bools = ((d >= dHi) & (d <= dLo))
    indices = np.arange(0, len(d), step = 1)[bools]
    return indices

def and_indices():
    y_sli = ((y >= y_min) & (y <= y_max))
    y_ind = np.arange(0, len(d), step = 1)[y_sli]
    l_sli = ((l >= l_min) & (l <= l_max))
    l_ind = np.arange(0, len(d), step = 1)[l_sli]
    ind = np.array(list(set.intersection(set(y_ind), set(l_ind), set(m_ind))))
def hist(d, err, b = 15):
    '''
    d: array of distance moduli
    
    b: number of bins for the histogram
    
    Returns:
    
    h: histogram values
    
    c: bin centers
    
    wid: width of bars
    '''
    # want to weight by err! #
    h, binedges = np.histogram(d, bins = b)
    c  = 0.5 * (binedges[1:] + binedges[:-1])
    wid = np.ptp(d)/15
    return h, c, wid      


# get list of indices corresponding to each desired measurement method  #

no = ['n', 'N', 'no', 'NO', 'No']
#dms = []
#dmerrs = []
#ceph_ind = []
#rrly_ind = []
#trgb_ind = []
# need to come up with alternative to individuall naming each method's list

#for r in objRows:
#    if check_for(r, 'method', m):
#        method.append(m)
#        t = True # t is an "any" true to avoid duplicate methods in the final list
#    if r['method'] == 'Cepheids' == m:
#        ceph_ind.append(objRows.index(r))
#    elif r['method'] == 'RR Lyrae' == m:
#        rrly_ind.append(objRows.index(r))
#    elif r['method'] == 'TRGB' == m:
#        trgb_ind.append(objRows.index(r))

#np.savetxt("{0}_{1}".format(obj_short, "_".join(methods_short)), np.transpose([dms, dmerrs, years, lmcs]), fmt='%0.2f')   
'''
# getting the needed data. Edit this as needed # 
dms = []
dmerrs = []
years = []
lmcs = []

for oRow in objRows:
    dms.append(float(get_val(oRow, 'dm')))
    dmerrs.append(float(get_val(oRow, 'dmerr')))
    years.append(float(get_val(oRow, 'date')))
    lmcs.append(float(get_val(oRow, 'LMCmod')))

dms = np.array(dms)
dmerrs = np.array(dmerrs)
years = np.array(years) + 1980
lmcs = np.array(lmcs)

print(dms)
print(dmerrs)
print(years)
print(lmcs)
obj_short = obj[0] + ''.join( [ x for x in obj.replace(" ", "") if not x.isalpha() ])
methods_short = [s.replace(" ", "").lower()[0:2] for s in methods]
print(obj_short)
print(methods_short)
print('Success!')
np.savetxt("{0}_{1}.txt".format(obj_short, methods_short), np.transpose([dms, dmerrs, years, lmcs]), fmt='%0.2f')
'''


# getting the needed data # 
#dms = []
#dmerrs = []
#years = []
#lmcs = []
#for oRow in objRows:
#    dms.append(float(get_val(oRow, 'dm')))
#    dmerrs.append(float(get_val(oRow, 'dmerr')))
#    years.append(float(get_val(oRow, 'date')))
#    lmcs.append(float(get_val(oRow, 'LMCmod')))

#dms = np.array(dms)
#dmerrs = np.array(dmerrs)
#years = np.array(years) + 1980
#lmcs = np.array(lmcs)


print("The methods {0} have been found in {1}".format(methods, infile))
#########################################################################
########################### SLIDERS AND AXES ############################
#########################################################################


fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.35)


# THESE are my "functions" to alter with sliders! then just plot them!! #

# want to weight counts by error

min_yr0 = 1985
max_yr0 = 2015
min_lmc0 = 18.40
max_lmc0 = 18.60
rects_list = [ ]
N_tots = [ ]
for m,c in zip(methods, colors):
#    for x in d:
#        if x['method'] == m:
#            dms.append(x['dm'])
#            dmerrs.append(x['dmerr'])
#            lmcs.append(x['LMCmod'])
#            years.append(x['date'])
    dms = np.array([float(x['dm']) for x in d if x['method'] == m])
    dmerrs = np.array([float(x['dmerr']) for x in d if x['method'] == m])
    lmcs = np.array([ 18.5 if not x['LMCmod'] else float(x['LMCmod']) for x in d if x['method'] == m])
    years = np.array([float(x['date']) for x in d if x['method'] == m]) + 1980
    N_tots.append(len(dms))
    y0 = [ x for x in years if x > min_yr0 and x < max_yr0 ]
    l0 = [ x for x in lmcs if x > min_lmc0 and x < max_lmc0 ]
    h0, centers0, w0 = hist(dms, dmerrs)
    rects_list.append(plt.bar(centers0, h0, width = w0, label = m, color = c))
print(rects_list)
#mdict = dict(zip(methods, N_tots))
#methods = [ mdict[x] for x in mdict.keys if x
# these if statements are to avoid sending empty lists to hist through  #
# the final ind parameter
'''                                             #
if 'Cepheids' in methods:
    h, centers, w = hist(dms, years, lmcs, min_yr0, max_yr0, min_lmc0, max_lmc0, ceph_ind)
    rects1 = plt.bar(centers, h, width = w, label = 'Cepheids', color = 'red')
if 'TRGB' in methods:
    h, centers, w = hist(dms, years, lmcs, min_yr0, max_yr0, min_lmc0, max_lmc0, ceph_ind)
    rects2 = plt.bar(centers, h, width = w, label = 'TRGB', color = 'red')
if 'RR Lyrae' in methods:
    h, centers, w = hist(dms, years, lmcs, min_yr0, max_yr0, min_lmc0, max_lmc0, ceph_ind)
    rects3 = plt.bar(centers, h, width = w, label = 'Cepheids', color = 'red')
'''
# add more distance methods later 
#if 'Tully-fisher' in methods:
#    ...

plt.legend()
#plt.axis([0, 1, -10, 10])

axcolor = 'lightgoldenrodyellow'

# [starting point from left to right, starting point bottom to top, ending point left to right, thickness]
axmin_yr = plt.axes([0.25, 0.15, 0.65, 0.03], axisbg=axcolor)
axmax_yr = plt.axes([0.25, 0.10, 0.65, 0.03], axisbg=axcolor)
axmin_lmc = plt.axes([0.25, 0.25, 0.65, 0.03], axisbg=axcolor)
axmax_lmc = plt.axes([0.25, 0.20, 0.65, 0.03], axisbg=axcolor)

smin_yr = Slider(axmin_yr, 'Minimum Year', 1975, max(years) , valinit=min_yr0)
smax_yr = Slider(axmax_yr, 'Maximum Year', 1975, max(years), valinit=max_yr0)
smin_lmc = Slider(axmin_lmc, "Minimum LMC m - M", 18.4, max(lmcs), valinit=min_lmc0)
smax_lmc = Slider(axmax_lmc, 'Maximum LMC m - M', 18.4, max(lmcs), valinit=max_lmc0)

# use numpy histogram option "weights" to deweight more erroneous and older values!
# just use TWO sliders to squeeze values!
def update(val):
    min_yr = smin_yr.val
    max_yr = smax_yr.val
    min_lmc = smin_lmc.val
    max_lmc = smax_lmc.val
    y = [ x for x in years if x > min_yr and x < max_yr ]
    print(y)
    l = [ x for x in lmcs if x > min_lmc and x < max_lmc ]
    print(l)
    for m, c, rects in zip(methods, colors, rects_list):
        heights, centers, widths = hist(dms, dmerrs)
        for r, h in zip(rects, heights):
            r.set_height(h)
#            r.set_width(w)
# don't want to keep remaking width

#if 'Cepheids' in methods:
#        heights1, bincenters1, width1 = hist(dms, years, lmcs, min_yr, max_yr, min_lmc, max_lmc, ceph_ind)
#        for r1, h1 in zip(rects1, heights1):
#            r1.set_height(h1)
#            r1.set_width(width1)
#    if 'TRGB' in methods:
#        heights2, bincenters2, width2  = hist(dms, years, lmcs, min_yr, max_yr, min_lmc, max_lmc, trgb_ind)
#        for r2, h2 in zip(rects2, heights2):
#            r2.set_height(h2)
#    if 'RR Lyrae' in methods:
#        heights3, bincenters3, width3  = hist(dms, years, lmcs, min_yr, max_yr, min_lmc, max_lmc, rrly_ind)
#        for r3, h3 in zip(rects3, heights3):
#            r3.set_height(h3)

#    for r1, r2, r3, h1, h2, h3 in zip(rects1, rects2, rects3, heights1, heights2, heights3):
#        r1.set_height(h1)
#        r2.set_height(h2)
#        r3.set_height(h3)
    fig.canvas.draw_idle()
smin_yr.on_changed(update)
smax_yr.on_changed(update)
smin_lmc.on_changed(update)
smax_lmc.on_changed(update)
                     
resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')


def reset(event):
    smin_yr.reset()
    smax_yr.reset()
    smin_lmc.reset()
    smax_lmc.reset()
button.on_clicked(reset)

cax = plt.axes([0.05, 0.4, 0.125, 0.15])
check = CheckButtons(cax, methods, (True, True, True))

def func(label): # remember to add or remove methods here
    if label == 'Cepheids' and label in methods:
        rects1.set_visible(not rects1.get_visible())
    elif label == 'TRGB' and label in methods:
        rects2.set_visible(not rects2.get_visible())
    elif label == 'RR Lyrae' and label in methods:
        rects3.set_visible(not rects3.get_visible())
    plt.draw()
check.on_clicked(func)

plt.show()

