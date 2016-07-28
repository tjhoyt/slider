
# coding: utf-8

# In[ ]:

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons


'''
1.) Main goal: to make a GUI functionality to toggle options on distance measurements
    a.) 2 way sliding bar to choose a date range @@@ Done! @@@
    b.) 2 way sliding bar to choose a lmc mod range @@@ Done! @@@
    c.) check boxes to choose objects -- no! Just one object at a time; makes more sense
    d.) check boxes select measurement methods

2.) Find a way to weight the histogram counts by the (inverse) error on the
measurement.

3.) Find a prettier way to handle when min goes higher than max


Additional:
    a.) Radio button(s) for weighted by error, by recentness, or both
    b.) Add object radio buttons and a while loop similar to the methods
    loop to grab mutliple objects from NED
    c.) Stop the rebinning with each new slide so a change in counts can be seen better
    d.) Fix the transparency issues (again)
    
    '''

'''
assumptions: Distances without tabulated errors are excluded! 
'''


# In[1]:

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons

#methods = ["Cepheids": "yellow", "TRGB": "orange", "RR Lyrae"]
keys = ["exclusion code", "record index", "object index", "object name","dm",
        "dmerr","distance","method","refcode","SN ID","z","h0","LMCmod","date","notes"]
obj = input("Enter the name of the object for which you want to retrieve "
              "distances: ")

#colors1 = ["red", "blue", "yellow"]
#colors2 = ["green", "yellow", "cyan"]
#alphas = [1.0, 0.60, 0.80]



#########################################################################
######################## DATABASE SEARCH FUNCTIONS ######################
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

def hist(d, y, l, y_min, y_max, l_min, l_max, m_ind, b = 15):
    '''
    d: array of distance moduli
    
    y: array of years
    
    m_ind: method indices for the first 3 arrays
    
    b: number of bins for the histogram
    
    Returns:
    
    h: histogram values
    
    c: bin centers
    
    wid: width of bars
    '''
    y_sli = ((y >= y_min) & (y <= y_max))
    y_ind = np.arange(0, len(d), step = 1)[y_sli]
    l_sli = ((l >= l_min) & (l <= l_max))
    l_ind = np.arange(0, len(d), step = 1)[l_sli]
    ind = np.array(list(set.intersection(set(y_ind), set(l_ind), set(m_ind))))
    h, binedges = np.histogram(d[ind], bins = b)
    c  = 0.5 * (binedges[1:] + binedges[:-1])
    wid = np.ptp(d[ind])/15
    return h, c, wid      

#########################################################################
######################### Filtering NED database ########################
#########################################################################


# pull rows corresponding to specified object. Exclude dm's w/ no error #

objRows = []
with open("NED26.05.1-D-12.1.0-20160501.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        drow = dict(zip(keys, row))
        r = obj_filter(drow, obj)
        if r != None and r['dmerr']: # python empty strings are 'falsy'
            objRows.append(r)

if any(x == None for x in objRows):
    print("The object name {0} is either not present or the naming"
      " format is not correct. Try looking at a few rows"
      " in the database to find the right convention.".format(obj))
else:
    print("The query returned {0} entries for the specified object.".format(len(objRows)))

    

# get list of indices corresponding to each desired measurement method  #

methods = [] # the overall methods list to get a list of methods to plot
no = ['n', 'N', 'no', 'NO', 'No']
dms = []
dmerrs = []
ceph_ind = []
rrly_ind = []
trgb_ind = []
# need to come up with alternative to individuall naming each method's list
while True:
    t = False
    method = []
    m = input("Enter a method, like 'Cepheids' or 'TRGB', you "
            "would like to search for in the new shortened  "
            "object database. If you do not wish to search "
            "for more methods hit enter or type no: ")
    for r in objRows:
        if check_for(r, 'method', m):
            method.append(m)
            t = True # t is an "any" true to avoid duplicate methods in the final list
        if r['method'] == 'Cepheids' == m:
            ceph_ind.append(objRows.index(r))
        elif r['method'] == 'RR Lyrae' == m:
            rrly_ind.append(objRows.index(r))
        elif r['method'] == 'TRGB' == m:
            trgb_ind.append(objRows.index(r))
    if t:
        methods.append(m)
        print("{0} of the {1} total {2} results used the {3} method.".format(len(method),
                                                                        len(objRows), obj, m))   
    elif m in no or m == '':
        print("broken")
        break
    else:
        print("The method {0} is either not present or the input"
              "format is not correct. Try looking at a few rows"
              "in the database to find the right convention.".format(m))
        

# getting the needed data # 
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

# these if statements are to avoid sending empty lists to hist through  #
# the final ind parameter                                               #
if 'Cepheids' in methods:
    h1, bincenters1, w1 = hist(dms, years, lmcs, min_yr0, max_yr0, min_lmc0, max_lmc0, ceph_ind)
    rects1 = plt.bar(bincenters1, h1, width = w1, label = 'Cepheids', color = 'red')
if 'RR Lyrae' in methods:
    h2, bincenters2, w2 = hist(dms, years, lmcs, min_yr0, max_yr0, min_lmc0, max_lmc0, rrly_ind)
    rects2 = plt.bar(bincenters2, h2, width = w2, label = 'RR Lyrae', color = 'blue')
if 'TRGB' in methods:
    h3, bincenters3, w3 = hist(dms, years, lmcs, min_yr0, max_yr0, min_lmc0, max_lmc0, trgb_ind)
    rects3 = plt.bar(bincenters3, h3, width = w3, label = 'TRGB', color = 'yellow')
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
    if 'Cepheids' in methods:
        heights1, bincenters1, width1 = hist(dms, years, lmcs, min_yr, max_yr, min_lmc, max_lmc, ceph_ind)
        for r1, h1 in zip(rects1, heights1):
            r1.set_height(h1)
    if 'RR Lyrae' in methods:
        heights2, bincenters2, width2 = hist(dms, years, lmcs, min_yr, max_yr, min_lmc, max_lmc, rrly_ind)
        for r2, h2 in zip(rects2, heights2):
            r2.set_height(h2)
    if 'TRGB' in methods:
        heights3, bincenters3, width3 = hist(dms, years, lmcs, min_yr, max_yr, min_lmc, max_lmc, trgb_ind)
        for r3, h3 in zip(rects3, heights3):
            r3.set_height(h3)
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
    elif label == 'RR Lyrae' and label in methods:
        rects2.set_visible(not rects2.get_visible())
    elif label == 'TRGB' and label in methods:
        rects3.set_visible(not rects3.get_visible())
    plt.draw()
check.on_clicked(func)

plt.show()

