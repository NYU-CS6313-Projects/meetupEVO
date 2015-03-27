import numpy as np
from numpy import dtype
import pandas as pd
import os
from glob import glob


def date_col(df, col):
    if not col in df.columns:
      return df
    df[col] = pd.to_datetime(df[col],unit='ms')  # just guessing here
    df[col + "_wday"] = df[col].apply(lambda x: x.weekday())
    return df

def flatten_col(df, col):
    if not col in df.columns:
      return df
    try: 
        sub_df = df[col].apply(pd.Series)
        sub_cols = [ c for c in list(sub_df.columns.values) if type(c) != int]
        # print sub_cols
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


class CategoryReader:
  def __init__(self, dir="../10-data/groups_new/", ext=".json", do_max = False, do_text = True, max_columns = {
      'city': dtype('O'),
      'country': dtype('O'),
      'created': dtype('<M8[ns]'),
      'created_wday': dtype('int64'),
      'description': dtype('O'),
      'filename': dtype('O'),
      'id_category': dtype('int64'),
      'id_main': dtype('int64'),
      'join_mode': dtype('O'),
      'lat': dtype('float64'),
      'link': dtype('O'),
      'lon': dtype('float64'),
      'member_id_organizer': dtype('int64'),
      'members': dtype('int64'),
      'name_category': dtype('O'),
      'name_main': dtype('O'),
      'name_organizer': dtype('O'),
      'rating': dtype('float64'),
      'shortname_category': dtype('O'),
      'state': dtype('O'),
      'timezone': dtype('O'),
      'urlname': dtype('O'),
      'visibility': dtype('O'),
      'who': dtype('O')
    }):
    self.filenames = glob( dir + "*" + ext )
    self.cursor = 0
    self.dir = dir
    self.ext = ext
    self.do_max = do_max
    self.do_text = do_text
    self.max_columns = max_columns

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
    df = flatten_col(df, "category") 
    df = flatten_col(df, 'organizer')
    df = date_col(df, "created") 
    del(df["group_photo"])
    del(df["topics"])

    if not self.do_text:
      del(df["description"])

    if not self.do_max:
      return df
    full_df = pd.DataFrame({k: pd.Series(dtype=v) for k,v in self.max_columns.items()})
    for k in self.max_columns.keys():
	if k in df.columns:
	   full_df[k] = df[k]
    if not self.do_text:
      del(full_df["description"])
    return full_df
    

class EventReader:
  def __init__(self,group_ids, dir="../10-data/events_updated/", ext=".json", do_max = False, max_columns = {
    0: dtype('float64'),
    u'rating': dtype('float64'),
    u'event_url': dtype('O'),
    u'who_group': dtype('O'),
    u'lon_venue': dtype('float64'),
    u'photo_url': dtype('O'),
    u'amount_fee': dtype('float64'),
    u'id_group': dtype('int64'),
    u'accepts_fee': dtype('O'),
    'time_wday': dtype('int64'),
    u'group': dtype('O'),
    u'currency_fee': dtype('O'),
    u'lon_group': dtype('float64'),
    u'zip_venue': dtype('O'),
    u'yes_rsvp_count': dtype('int64'),
    u'city_venue': dtype('O'),
    u'lat_group': dtype('float64'),
    u'count_rating': dtype('float64'),
    u'join_mode_group': dtype('O'),
    u'description_fee': dtype('O'),
    u'updated': dtype('int64'),
    '0_main': dtype('float64'),
    u'required_fee': dtype('O'),
    u'visibility': dtype('O'),
    u'name_venue': dtype('O'),
    u'created_group': dtype('<M8[ns]'),
    'created_group_wday': dtype('int64'),
    'created_wday': dtype('int64'),
    u'name_main': dtype('O'),
    u'name_group': dtype('O'),
    u'how_to_find_us': dtype('O'),
    u'utc_offset': dtype('int64'),
    u'urlname_group': dtype('O'),
    u'address_1_venue': dtype('O'),
    u'duration': dtype('float64'),
    u'description_main': dtype('O'),
    u'id': dtype('int64'),
    u'rsvp_limit': dtype('float64'),
    u'lat_venue': dtype('float64'),
    u'created_main': dtype('int64'),
    u'filename': dtype('O'),
    u'average_rating': dtype('float64'),
    u'id_main': dtype('int64'),
    u'country_venue': dtype('O'),
    u'waitlist_count': dtype('int64'),
    u'maybe_rsvp_count': dtype('int64'),
    u'status': dtype('O'),
    '0_venue': dtype('float64'),
    u'state_venue': dtype('O'),
    u'description': dtype('O'),
    u'repinned_venue': dtype('O'),
    u'phone_venue': dtype('O'),
    u'why': dtype('O'),
    u'id_venue': dtype('float64'),
    u'created': dtype('<M8[ns]'),
    u'label_fee': dtype('O'),
    u'time': dtype('<M8[ns]'),
    u'address_2_venue': dtype('O'),
    u'headcount': dtype('int64')
  }):
    self.filenames = [ dir + f.strip() + ext for f in group_ids]
    self.cursor = 0
    self.dir = dir
    self.ext = ext
    self.do_max = do_max
    self.max_columns = max_columns

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
    df = flatten_col(df, "fee") 
    df = flatten_col(df, "venue") 
    df = date_col(df, "created") 
    df = date_col(df, "created_group") 
    df = date_col(df, "time") 

    # copy over to new df?
    #return df[[ self.max_columns ]]
    if not self.do_max:
      return df
    full_df = pd.DataFrame({k: pd.Series(dtype=v) for k,v in self.max_columns.items()})
    for k in self.max_columns.keys():
	if k in df.columns:
	   full_df[k] = df[k]
    return full_df
    

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
    
