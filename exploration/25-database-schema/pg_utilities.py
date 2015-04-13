import numpy as np
from numpy import dtype
import pandas as pd
import os
from glob import glob


def empty_df_of_type( d ):
    dict = {}
    for k,v in d.items():
       dict[k] = pd.Series(dtype=v) 
    full_df = pd.DataFrame(dict)
    return full_df

def date_time_col(df, col):
    if not col in df.columns:
      return df
    df[col] = pd.to_datetime(df[col],unit='ms')  # just guessing here
    df[col + "_wday"] = df[col].apply(lambda x: x.weekday())
    df[col + "_time"] = df[col].apply(lambda x: x.time())
    return df

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


GroupReaderCOLUMNS = {
      'city': dtype('O'),
      'country': dtype('O'),
      'created': dtype('<M8[ns]'),
      'created_wday': dtype('int64'),
      'description': dtype('O'),
      'id_category': dtype('int64'),
      'id_group': dtype('int64'),
      'join_mode': dtype('O'),
      'lat': dtype('float64'),
      'link': dtype('O'),
      'lon': dtype('float64'),
      'member_id_organizer': dtype('int64'),
      'members': dtype('int64'),
      'name_category': dtype('O'),
      'name': dtype('O'),
      'name_organizer': dtype('O'),
      'rating': dtype('float64'),
      'shortname_category': dtype('O'),
      'state': dtype('O'),
      'timezone': dtype('O'),
      'urlname': dtype('O'),
      'visibility': dtype('O'),
      'who': dtype('O')
    }

class GroupReader:
  def __init__(self, dir="../10-data/groups_new/", ext=".json", do_max = False, do_text = True, max_columns = GroupReaderCOLUMNS):
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
    # df[u'filename'] = filename.replace(self.ext,"").replace(self.dir,"")
    df = flatten_col(df, "category") 
    df = flatten_col(df, "organizer")
    df = date_col(df, "created") 
    df.rename(columns={ 'id_main': 'id_group', 'name_main': 'name' }, inplace=True)
    del(df["group_photo"])
    del(df["topics"])

    if not self.do_text:
      del(df["description"])

    if not self.do_max:
      return df

    full_df = empty_df_of_type(self.max_columns)

    for k in self.max_columns.keys():
	if k in df.columns:
	   full_df[k] = df[k]
    if not self.do_text:
      del(full_df["description"])
    return full_df
    

RsvpReaderCOLUMNS = {
  'comments': dtype('O'),
  'created': dtype('<M8[ns]'),
  'created_time': dtype('O'),
  'created_wday': dtype('int64'),
  'id_event': dtype('O'),
  'guests': dtype('int64'),
  'id_member': dtype('int64'),
  'mtime': dtype('<M8[ns]'),
  'mtime_time': dtype('O'),
  'mtime_wday': dtype('int64'),
  'name_member': dtype('O'),
  'response': dtype('O'),
  'rsvp_id': dtype('int64'),
  'watching': dtype('float64')
}
class RsvpReader:
  def __init__(self,dir="../10-data/rsvps/", ext=".json", do_text = True, do_max = False, max_columns = RsvpReaderCOLUMNS):
    self.filenames = glob( dir + "*" + ext )
    self.cursor = 0
    self.dir = dir
    self.ext = ext
    self.do_max = do_max
    self.max_columns = max_columns
    # print "Reader created, %d files in the pipe" % len(self.filenames)

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
    # print "Next in Reader: %s" % filename
    self.cursor += 1
 
    df = pd.read_json(filename)
    if len(df) == 0:
        return df
    df[u'id_event'] = filename.replace(self.ext,"").replace(self.dir,"")
    if 'event' in df.columns:
      del(df['event'])
    if 'group' in df.columns:
      del(df['group'])
    if 'tallies' in df.columns:
      del(df['tallies'])
    if 'venue' in df.columns:
       del(df['venue']) 
    if 'member_photo' in df.columns:
      del(df['member_photo']) 
    df = flatten_col(df, "member") 
    df = date_time_col(df, "created") 
    df = date_time_col(df, "mtime") 

    if not self.do_max:
      return df

    full_df = empty_df_of_type(self.max_columns)
    for k in self.max_columns.keys():
	if k in df.columns:
	   full_df[k] = df[k]
    return full_df
    

VenueCOLUMNS = {
    'address_1': dtype('O'),
    'address_2': dtype('O'),
    'city': dtype('O'),
    'country': dtype('O'),
    'id_venue': dtype('float64'),
    'lat': dtype('float64'),
    'lon': dtype('float64'),
    'name': dtype('O'),
    'phone': dtype('O'),
    'repinned': dtype('O'),
    'state': dtype('O'),
    'zip': dtype('O')
  }

class VenuesReader:
  def __init__(self,group_ids, dir="../10-data/events_updated/", ext=".json", do_max = False, max_columns = VenueCOLUMNS):
    self.filenames = [ dir + f.strip() + ext for f in group_ids]
    self.cursor = 0
    self.dir = dir
    self.ext = ext
    self.do_max = do_max
    self.max_columns = max_columns
    self.used_ids = set()

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

    df = flatten_col(df, "venue") 
    for oldname,newname in { 'address_1_venue': 'address_1', 
              'address_2_venue': 'address_2', 
              'city_venue': 'city',
              'country_venue': 'country',
              'lat_venue': 'lat',
              'lon_venue': 'lon',
              'name_venue': 'name',
              'phone_venue': 'phone',
              'repinned_venue': 'repinned',
              'state_venue': 'state',
              'zip_venue': 'zip' }.items():
        if oldname in df.columns:
            df.rename(columns={ oldname: newname }, inplace=True)

    for colname in df.columns:
       if colname not in [ 'address_1', 'address_2', 'city', 'country', 'id_venue',
	    'lat', 'lon', 'name', 'phone', 'repinned', 'state', 'zip' ]:
          del( df[colname] )

    if not 'id_venue' in df.columns:
      print "ERROR: no id_venue in df of len %d, columns %s" % ( len(df.index), df.columns.values )
      return empty_df_of_type(self.max_columns)
      
    for i in self.used_ids:
      df = df[ df.id_venue != i ]

    df.drop_duplicates(subset = ['id_venue'], inplace = True)
    df.dropna(subset = ['id_venue'], inplace = True)
    self.used_ids.update( df.id_venue.values )

    if len(df.id_venue.unique()) != len(df.index):
      print "ERROR: we need to delete non-uniq"


    if not self.do_max:
      return df

    full_df = empty_df_of_type(self.max_columns)

    for k in self.max_columns.keys():
      if k in df.columns:
        full_df[k] = df[k]
    return full_df
    

EventCOLUMNS = {
    'accepts_fee': dtype('O'),
    'amount_fee': dtype('float64'),
    'average_rating': dtype('float64'),
    'count_rating': dtype('int64'),
    'created': dtype('<M8[ns]'),
    'created_wday': dtype('int64'),
    'currency_fee': dtype('O'),
    'description': dtype('O'),
    'description_fee': dtype('O'),
    'duration': dtype('O'),
    'event_url': dtype('O'),
    'headcount': dtype('int64'),
    'how_to_find_us': dtype('O'),
    'id_event': dtype('int64'),
    'id_group': dtype('int64'),
    'id_venue': dtype('int64'),
    'label_fee': dtype('O'),
    'maybe_rsvp_count': dtype('int64'),
    'name': dtype('O'),
    'photo_url': dtype('O'),
    'rating': dtype('float64'),
    'required_fee': dtype('O'),
    'status': dtype('O'),
    'time': dtype('<M8[ns]'),
    'time_wday': dtype('int64'),
    'updated': dtype('<M8[ns]'),
    'updated_wday': dtype('int64'),
    'updated': dtype('int64'),
    'utc_offset': dtype('int64'),
    'venue_visibility': dtype('O'),
    'waitlist_count': dtype('int64'),
    'why': dtype('O'),
    'yes_rsvp_count': dtype('int64'),
  }

class EventReader:
  def __init__(self,group_ids, dir="../10-data/events_updated/", ext=".json", do_max = False, max_columns = EventCOLUMNS):
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
    df = date_col(df, "updated") 
    df = date_col(df, "created") 
    df = date_col(df, "created_group") 
    df = date_col(df, "time") 
    df.rename(columns={'id_main': 'id_event', 'visibility': 'venue_visibility'}, inplace=True)
    df.dropna(subset = ['id_event'], inplace = True)

    if not self.do_max:
      return df

    full_df = empty_df_of_type(self.max_columns)

    for k in self.max_columns.keys():
	if k in df.columns:
	   full_df[k] = df[k]
    return full_df
    
GroupMemberCOLUMNS = {
  'id_group': dtype('O'),
  'id_member': dtype('int64'),
  'name': dtype('O'),
  'bio': dtype('O'),
  'visited': dtype('int64'),
  'visited_time': dtype('O'),
  'visited_wday': dtype('int64'),
  'joined': dtype('int64'),
  'joined_time': dtype('O'),
  'joined_wday': dtype('int64')
}
class GroupMemberReader:
  def __init__(self,group_ids, members_dir="../10-data/members_updated/", ext=".json", do_max = False, max_columns = GroupMemberCOLUMNS):
    self.filenames = [ members_dir + f.strip() + ext for f in group_ids]
    self.cursor = 0
    self.members_dir = members_dir
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
    df[u'id_group'] = filename.replace(self.ext,"").replace(self.members_dir,"")
    df.rename(columns={'id': 'id_member'}, inplace=True)
    del(df['self'])
    del(df['other_services'])
    df = flatten_col(df, "photo")
    df = date_time_col(df, "joined") 
    df = date_time_col(df, "visited") 
    
    if not self.do_max:
      return df
    
    full_df = empty_df_of_type(self.max_columns)
   
    for k in self.max_columns.keys():
	if k in df.columns:
	   full_df[k] = df[k]
    return full_df
    
MemberCOLUMNS = {
  'city': dtype('O'),
  'country': dtype('O'),
  'highres_link_photo': dtype('O'),
  'hometown': dtype('O'),
  'id_member': dtype('int64'),
  'id_photo': dtype('float64'),
  'lat': dtype('float64'),
  'link': dtype('O'),
  'link_photo': dtype('O'),
  'lon': dtype('float64'),
  'state': dtype('O'),
  'thumb_link_photo': dtype('O')
}

class MemberReader:
  def __init__(self,group_ids, members_dir="../10-data/members_updated/", ext=".json", do_max = False, max_columns = MemberCOLUMNS):
    self.filenames = [ members_dir + f.strip() + ext for f in group_ids]
    self.cursor = 0
    self.members_dir = members_dir
    self.ext = ext
    self.do_max = do_max
    self.max_columns = max_columns
    self.used_ids = set()

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
    df[u'id_group'] = filename.replace(self.ext,"").replace(self.members_dir,"")
    df.rename(columns={'id': 'id_member'}, inplace=True)
    del(df['self'])
    del(df['other_services'])
    df = flatten_col(df, "photo")
    df = date_time_col(df, "joined") 
    
    for i in self.used_ids:
      df = df[ df.id_member != i ]

    df.drop_duplicates(subset = ['id_member'], inplace = True)
    df.dropna(subset = ['id_member'], inplace = True)
    self.used_ids.update( df.id_member.values )

    if not self.do_max:
      return df
    
    full_df = empty_df_of_type(self.max_columns)
   
    for k in self.max_columns.keys():
	if k in df.columns:
	   full_df[k] = df[k]
    return full_df
    
