import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons

colors = ["red", "blue", "yellow"]
no = ['n', 'N', 'no', 'NO', 'No']

# maybe a user input for below values *and* their names as well to    #
# totally generalize                                                  #    
min_yr0 = 1985
max_yr0 = 2015
min_lmc0 = 18.40
max_lmc0 = 18.60


# read in the desired file #
infile = input("\nEnter the name of the txt file produced by ned_get "
               " (include file extension) \n\nInput file: ")
with open(infile) as json_data:
    d = json.load(json_data)
    json_data.close()

methods = list(set([x['method'] for x in d]))
print(methods)
#########################################################################
################################ FUNCTIONS ##############################
#########################################################################



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
    try:
        wid = np.ptp(d)/15
    except:
        wid = 0.0
        print("\nNo distance moduli found in this  \n"
              "range of years and LMC zero point     " )
        pass
    return h, c, wid      


#########################################################################
########################### SLIDERS AND AXES ############################
#########################################################################


fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.35)

lmcs_list = [ ]
years_list = [ ]
dms_list = [ ]
dmerrs_list = [ ]
rects_list = [ ]
N_tots = [ ]
for m,c in zip(methods, colors):
    dms = np.array([float(x['dm']) for x in d if x['method'] == m])
    dmerrs = np.array([float(x['dmerr']) for x in d if x['method'] == m])
    lmcs = np.array([ 18.5 if not x['LMCmod'] else float(x['LMCmod']) for x in d if x['method'] == m])
    years = np.array([float(x['date']) for x in d if x['method'] == m]) + 1980
    dms_list.append(dms)
    dmerrs_list.append(dmerrs)
    lmcs_list.append(lmcs)
    years_list.append(years)
    N_tots.append(len(dms))
    ind = np.where( (years >= min_yr0) & (years <= max_yr0) & (lmcs >= min_lmc0) & (lmcs <= max_lmc0) )[0]
    h0, centers0, w0 = hist(dms[ind], dmerrs[ind])
    rects_list.append(plt.bar(centers0, h0, width = w0, label = m, color = c))
plt.legend()

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
    for m, c, dms, dmerrs, rects, years, lmcs in zip(methods, colors, dms_list, dmerrs_list, rects_list, years_list, lmcs_list):
#       np.where() gives you indices and just having the args of np.where() w/o the call
#       gives a boolean array!
        ind = np.where( (years >= min_yr) & (years <= max_yr) & (lmcs >= min_lmc) & (lmcs <= max_lmc) )[0]
        heights, centers, widths = hist(dms[ind], dmerrs[ind])
        for r, h in zip(rects, heights):
            r.set_height(h)
#           r.set_width(w)
# don't want to keep remaking width
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

