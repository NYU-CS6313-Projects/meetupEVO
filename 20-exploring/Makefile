groups-notext.csv:
	./convert_groups > groups-notext.csv

explore-groups:
	./select_groups all | ./explore_groups  > groupscolumns.txt

events.csv:
	./select_groups all | ./convert_events > events.csv

explore-events:
	./select_groups all | ./explore_events  > eventscolumns.txt

member-retention.png: 
	select_groups 1 | plot_member_retention

groups_events_yes.html: generate_sparkline
	select_groups 10 | generate_sparkline > groups_events_yes.html

groups-and-no-of-events.png: 
	select_groups | plot_eventline 
