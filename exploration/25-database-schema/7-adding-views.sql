create view event_rsvps_by_month as     
  select id_group, date_trunc('month', time) time_bin, SUM(yes_rsvp_count_from_rsvps) 
  from events 
  group by id_group, time_bin
  order by id_group, time_bin;

create view event_rsvps_by_year as      
  select id_group, date_trunc('year', time) time_bin, SUM(yes_rsvp_count_from_rsvps) 
  from events 
  group by id_group, time_bin
  order by id_group, time_bin;

