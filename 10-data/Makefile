all: rsvps.list events_updated.list groups_new.list members_updated.list
	wc -l *.list | grep -v total

members-small.csv: members.csv
	csvcut -C 1,2,5,7,9,10,13,15,16,18,20 members.csv > members-small.csv

members-small-uniq.csv: members-small.csv
	head -1 members-small.csv > members-small-uniq.csv
	tail -n +2 members-small.csv | sort | uniq >> members-small-uniq.csv

pg_dump:
	pg_dump -Fc --no-acl --no-owner  infovis_meetup > infovis_meetup.dump
	cp  infovis_meetup.dump ~/Dropbox/Public/

clean: 
	rm *.list

clean_data:
	rm rsvps/* events_updated/* groups_new/* members_updated/*

organizers.json:
	echo "[" > organizers.json
	jq -c '.[]|.organizer' groups_new/category_* | sort | uniq | sed -e "s/$$/,/" >> organizers.json
	echo "{}]" >> organizers.json

id_group.txt:
	jq -c '.[]|.id' groups_new/category_*.json | grep -v null | sort -n | uniq > id_group.txt
	wc -l id_group.txt

id_venue.txt:
	jq ".[]|.venue.id" events_updated/*.json | grep -v null | sort -n | uniq > id_venue.txt
	wc -l id_venue.txt

id_event.txt:
	jq -c '.[]|.id' events_updated/*.json | grep -v null | sort -n | uniq > id_event.txt
	wc -l id_event.txt

count_id_member.txt:
	jq ".[]|.id" members_updated/*.json | grep -v null | sort -n | uniq -c > count_id_member.txt

id_member.txt: count_id_member.txt
	cut -c9- count_id_member.txt > id_member.txt

id_organizer.txt: organizers.json
	jq '.[].member_id' organizers.json | sort | uniq > id_organizer.txt

rsvps.list:
	ls -U rsvps/ | grep .json > rsvps.list

rsvps.csv:
	cp rsvps.parts/rsvp.1.csv rsvps.csv
	tail -n +2 rsvps.parts/rsvp.2.csv >> rsvps.csv
	tail -n +2 rsvps.parts/rsvp.3.csv >> rsvps.csv
	tail -n +2 rsvps.parts/rsvp.4.csv >> rsvps.csv
	tail -n +2 rsvps.parts/rsvp.5.csv >> rsvps.csv
	tail -n +2 rsvps.parts/rsvp.6.csv >> rsvps.csv
	tail -n +2 rsvps.parts/rsvp.7.csv >> rsvps.csv
	tail -n +2 rsvps.parts/rsvp.8.csv >> rsvps.csv

events_updated.list:
	ls -U events_updated/ | grep .json > events_updated.list

groups_new.list:
	ls -U groups_new/ | grep category | grep .json > groups_new.list
	
members_updated.list:
	ls -U members_updated/ | grep .json > members_updated.list
