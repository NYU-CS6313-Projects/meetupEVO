all: rsvps.list events_updated.list groups_new.list members_updated.list
	wc -l *.list | grep -v total

pg_dump:
	pg_dump -Fc --no-acl --no-owner  infovis_meetup > infovis_meetup.dump

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
	cut -c6- count_id_member.txt > id_member.txt

rsvps.list:
	ls -U rsvps/ | grep .json > rsvps.list

events_updated.list:
	ls -U events_updated/ | grep .json > events_updated.list

groups_new.list:
	ls -U groups_new/ | grep category | grep .json > groups_new.list
	
members_updated.list:
	ls -U members_updated/ | grep .json > members_updated.list
