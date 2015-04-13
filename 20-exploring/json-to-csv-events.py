from glob import glob
from utilities import flatten_col
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
from pandas.io.json import json_normalize
import csv


data_dir = "../10-data"

outfile = open("%s/events.csv" % data_dir ,"wb")
types = []
lens = []

firstfile = True
for filename in glob("%s/events_updated/*.json" % data_dir):
    df = pd.read_json(filename)
    if len(df) == 0:
        continue
        # ignore empty json
    print "+ %d" % len(df),
    df[u'filename'] = filename.replace(".json","").replace(data_dir+"/events_updated/","")
    df = flatten_col(df, "group")
    df = flatten_col(df, "rating")
    df = flatten_col(df, "fee")
    df.rename(columns = {'id_main': 'id'}, inplace=True)
    if firstfile:
      headers = list(df.columns)
      types = list(df.dtypes)
      df.to_csv( outfile, header = True, encoding='utf-8' )
      for i,c in enumerate(headers):
        if types[i] == np.dtype('O'):
          lens.append(  df[c].str.len().max() )
        else:
          lens.append( 0)
      firstfile = False
    else:
      if headers ==       list(df.columns):
        df.to_csv( outfile, header = False, encoding='utf-8' )
        for i,c in enumerate(headers):
          if types[i] == dtype('O'):
            lens[i] = max( lens[i], df[c].str.len().max() )
      else:
        print "There is a problem writing file %s:" %filename
        print "  Header here are ",  list(df.columns)
        print "  Headers should be",  headers


print "CREATE TABLE events ("
for i,c in enumerate(headers):
  if types[i] == np.dtype('O'):
    print "%s VARCHAR(%d) NULL,  // column nr. %d" % (headers[i], lens[i], i)
  elif types[i] == np.dtype('int64'):
    print "%s INTEGER NULL,  // column nr. %d" % (headers[i],  i)
  elif types[i] == np.dtype('float64'):
    print "%s FLOAT NULL,  // column nr. %d" % (headers[i], i)
  else:
    print "%s %s NULL,  // column nr. %d" % (headers[i], types[i], i)

print " PRIMARY KEY id"
print ")"
