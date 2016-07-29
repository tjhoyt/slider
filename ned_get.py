import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons

'''
Assumptions: Distances without tabulated errors are excluded! 
'''



keys = ["exclusion code", "record index", "object index", "object name","dm",
        "dmerr","distance","method","refcode","SN ID","z","h0","LMCmod","date","notes"]


#########################################################################
################################ FUNCTIONS ##############################
#########################################################################


def obj_filter(r, o):
    n = r['object name'].replace(" ","").lower()
    o = o.replace(" ","").lower()
    if n == o:
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
    if d[key].replace(" ","").lower() == val.replace(" ","").lower():
        return True

#########################################################################
######################### Filtering NED database ########################
#########################################################################


while True:
    t = False
    obj = input("\n    Enter the name of the object for\n"
            "    which you want to retrieve distances.\n\n"
            "Object name: ")
# pull rows corresponding to specified object. Exclude dm's w/ no error #
    objRows = []
    with open("NED26.05.1-D-12.1.0-20160501.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            drow = dict(zip(keys, row))
            r = obj_filter(drow, obj)
            if r != None and r['dmerr']: # python empty strings are 'falsy'
                objRows.append(r)
                t = True
    if t:
        print("The query successfully returned {0} entries for {1}. \n".format(len(objRows),obj))
        break
    else:
        print("\n    The object name {0} is either not present or \n"
          "    the naming format is not correct. Try looking at a \n"
          "    few rows in the database to find the right convention. \n".format(obj))

methods = [] # the overall methods list to get a list of methods to plot
no = ['n', 'N', 'no', 'NO', 'No']
finalRows = []
# need to come up with alternative to individuall naming each method's list
while True:
    t = False
    method = []
    m = input("    Enter a method, like 'Cepheids' or 'TRGB', you \n"
            "    would like to search for in the new shortened \n"
            "    object database. If you do not wish to search \n"
            "    for more methods hit enter or type no \n\n"
            "Method name: ")
    for r in objRows:
        if check_for(r, 'method', m):
            method.append(m)
            finalRows.append(r)
            t = True # t is an "any" true to avoid duplicate methods in the final list
    if t:
        methods.append(m)
        print("{0} of the {1} total {2} results used the {3} method.\n".format(len(method), len(objRows), obj, m))   
    elif m in no or m == '':
        print("broken")
        break
    else:
        print("    The method {0} is either not present or the input \n"
              "    format is not correct. Try looking at a few rows \n"
              "    in the database to find the right convention. \n".format(m))

              
obj_short = obj[0] + ''.join( [ x for x in obj.replace(" ", "") if not x.isalpha()] )
methods_short = [s.replace(" ", "").lower()[0:2] for s in methods]

import json
with open("{0}_{1}.txt".format(obj_short, "_".join(methods_short)), 'w') as fout:
    json.dump(finalRows, fout)



print('Success!')
