all: rsvps.list events_updated.list groups_new.list members_updated.list
	wc -l *.list | grep -v total

clean: 
	rm *.list

clean_data:
	rm rsvps/* events_updated/* groups_new/* members_updated/*

rsvps.list:
	ls -U rsvps/ | grep .json > rsvps.list

events_updated.list:
	ls -U events_updated/ | grep .json > events_updated.list

groups_new.list:
	ls -U groups_new/ | grep .json > groups_new.list
	
members_updated.list:
	ls -U members_updated/ | grep .json > members_updated.list
