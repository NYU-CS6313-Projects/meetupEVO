alter table groups add column average_rsvps_per_event float default 0.0;
alter table groups add column r1 float default 0.0;
alter table groups add column r2 float default 0.0;

UPDATE groups
SET r1 = b.sum, r2 = b.c
FROM ( SELECT id_group, sum(yes_rsvp_count_from_rsvps) as sum, count(*) as c from events GROUP BY id_group) b  
WHERE groups.id_group = b.id_group;

UPDATE groups set average_rsvps_per_event = r1 / r2 WHERE r2 > 0;

