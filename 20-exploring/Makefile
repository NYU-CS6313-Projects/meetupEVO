groups_events_yes.html: generate_sparkline
	select_groups | generate_sparkline > groups_events_yes.html
	# ls ../10-data/events_updated/*.json | generate_sparkline > groups_events_yes.html

groups-and-no-of-events.png: 
	select_groups | plot_eventline 
