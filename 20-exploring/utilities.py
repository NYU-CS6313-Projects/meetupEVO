import pandas as pd
import os

def flatten_col(df, col):
    try: 
        sub_df = df[col].apply(pd.Series)
        sub_cols = [ c for c in list(sub_df.columns.values) if type(c) != int]
        print sub_cols
        new_df = pd.merge(df, sub_df,  left_index=True, right_index=True, suffixes = ('_main','_%s' % col))
        rename_columns = {}
	if len(sub_cols)==0:
	    return df
        for c in sub_cols:
            if c.startswith('%s_' % col):
                c_new =  c.replace('%s_' % col, '') + "_" + col
                rename_columns[c] = c_new
                # print "renaming %s to %s" % (c, c_new)
            elif c.endswith('_%s' % col):
                pass
            else:
                c_new = c + "_" + col
                rename_columns[c] = c_new
                #print "renaming %s to %s" % (c, c_new)
            
        new_df.rename(columns=rename_columns, inplace=True)
        del(new_df[col])
        return new_df 
    except Exception as e:
        print "could not convert! %s" % e
        return df


class EventReader:
  def __init__(self,group_ids, dir="../10-data/events_updated/", ext=".json"):
    self.filenames = [ dir + f.strip() + ext for f in group_ids]
    self.cursor = 0
    self.dir = dir
    self.ext = ext

  def __iter__(self):
    return self

  def next(self):
    # find the next (non-empty) file on my list, or stop
    while self.cursor < len( self.filenames ) and os.path.getsize(self.filenames[self.cursor])==0:
      self.cursor += 1
    if self.cursor >= len( self.filenames ):
      raise StopIteration

    # found a file
    filename = self.filenames[ self.cursor ] 
    self.cursor += 1
 
    df = pd.read_json(filename)
    if len(df) == 0:
        return df
    df[u'filename'] = filename.replace(self.ext,"").replace(self.dir,"")
    df = flatten_col(df, "group")
    df = flatten_col(df, "rating") 
    return df
    

class GroupMemberReader:
  def __init__(self,group_ids, members_dir="../10-data/members_updated/", ext=".json"):
    self.filenames = [ members_dir + f.strip() + ext for f in group_ids]
    self.cursor = 0
    self.members_dir = members_dir
    self.ext = ext

  def __iter__(self):
    return self

  def next(self):
    # find the next (non-empty) file on my list, or stop
    while self.cursor < len( self.filenames ) and os.path.getsize(self.filenames[self.cursor])==0:
      self.cursor += 1
    if self.cursor >= len( self.filenames ):
      raise StopIteration

    # found a file
    filename = self.filenames[ self.cursor ] 
    self.cursor += 1
 
    df = pd.read_json(filename)
    if len(df) == 0:
        return df
    df[u'filename'] = filename.replace(self.ext,"").replace(self.members_dir,"")
    del(df['self'])
    df = flatten_col(df, "photo")
    return df
    
