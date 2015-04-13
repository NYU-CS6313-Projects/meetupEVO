### normalizing time series

see http://stackoverflow.com/questions/25059936/normalization-of-several-time-series-of-different-lengths-and-scale

### working with rsvps instead of events and groups

We have a lot more rsvps than events or groups.
a lot of rsvps refer to events we have no details on:

infovis_meetup=> select count(*) from (select distinct id_event from rsvps) rsvps_events 
		 left join events using (id_event)  where events.id_event is not null limit 10;
 count 
-------
 18656

infovis_meetup=> select count(*) from (select distinct id_event from rsvps) rsvps_events 
		 left join events using (id_event)  where events.id_event is null;
 count  
--------
 585734


The same goes for groups:
