## Structure of the Data

### events_updated

The Events folder has a total of 10,942 files. It represents meetup.com events
held in New York State since the beginning of meetup.com until a certain point
of time. 

Each file is named after the groupid and represents the events of one group and
contains an array of events. There are 15~20 attributes for each event record.

* events_updated/10007032.json
* events_updated/10007272.json
* events_updated/10008572.json

### groups_new

The Groups folder has a total of 35 files. It represents all meetup.com groups
located in New York State captured at a certain point of time. 

Each file contains an array of the groups belonging to one thematic category and is named
for the category id. There are 20~21 main attributes for each group record.

3 example files are called:

* groups_new/category_10.json
* groups_new/category_11.json
* groups_new/category_12.json

### members_updated

The Members folder has a total of 10,942 files. 
It represents all meetup.com members of the groups mentioned above. 

Each file has a set of members for one group and is named after the group id. 
There are 13~17 main attributes for each member record.

3 example files are called:

* members_updated/10007032.json
* members_updated/10007272.json
* members_updated/10008572.json

### rsvps.list

The Rsvps folder is the biggest folder, it contains 627,415 files. Each file
represents one event and is named after the event id.  Each file contains 
an array of members rsvps for that event.  

The files contain a lot of redundant data: the groups info and venue info are
repeated for each member. There are only very few attributes of interest!

3 example files are called:

* ktpdpypmbjb.json
* 40582862.json
* 40680002.json
