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
    '''
    Return a row that matches the desired object. All strings are
    normalized to first letter of catalog, lowercase, with no space
    between it and the number of the object in the catalog.

    Args:
        r (dict): Row from NED to check for matching object name
        under key 'object name'

        o (string): Input object name user is searching for in NED
        
    Returns:
        r (dict): the same row that was input
    
    '''
    
    
    num_db = ''.join( [ x for x in r['object name'].replace(" ", "")if not x.isalpha()] ).lstrip("0")  # deletes all spaces, lower cases everything, and strips all leading 0's while getting only the string's numeric characters
    num_in = ''.join( [ x for x in o.replace(" ", "") if not x.isalpha()] ).lstrip("0") 
    if len(num_db) > 4:
        num_db = num_db[:5]
    n_db = r['object name'][0].lower() + num_db
#    print(n_db)
    if len(num_in) > 4:
        num_in = num_in[:5]
    n_in = o[0].lower() + num_in
#    print(n_in)
    if n_db == n_in: # compares the first letter of object name plus the first four numbers
        return r

def get_dm(r): # need separate get_dm function bc of the replacement of 18.5 for ""
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
            if drow['object name']: # check to make sure the 'object name' value is not empty
                r = obj_filter(drow, obj)
                if r != None and r['dmerr']: # excludes values with no error on dm measurement
                    objRows.append(r)
                    t = True
    if t:
        print("The query successfully returned {0} entries for {1}. \n".format(len(objRows),obj))
        break
    else:
        print("\n    Sorry! The object name {0} is either not present or \n"
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

              
num_obj = ''.join( [ x for x in obj.replace(" ", "") if not x.isalpha()] ).lstrip('0')
if len(num_obj) > 4:
        num_obj = num_obj[:5]
obj_short = obj[0] + num_obj
methods_short = [s.replace(" ", "").lower()[0:2] for s in methods]

import json
with open("{0}_{1}.txt".format(obj_short, "_".join(methods_short)), 'w') as fout: # limit obj name to 5 chars (cat + 4 nums)
    json.dump(finalRows, fout)



print('Success!')
