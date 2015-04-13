
ALTER TABLE events ADD COLUMN yes_rsvp_count_from_rsvps integer DEFAULT NULL;

UPDATE events 
SET yes_rsvp_count_from_rsvps = b.count
FROM (
  SELECT 
    events.id_event, count(id_rsvp) AS count
  FROM rsvps
  LEFT JOIN events  USING(id_event) 
  WHERE response = 'yes'
  GROUP BY events.id_event
) b
WHERE events.id_event = b.id_event;

ALTER TABLE events ADD COLUMN no_rsvp_count_from_rsvps integer DEFAULT NULL;

UPDATE events 
SET no_rsvp_count_from_rsvps = b.count
FROM (
  SELECT 
    events.id_event, count(id_rsvp) AS count
  FROM rsvps
  LEFT JOIN events  USING(id_event) 
  WHERE response = 'no'
  GROUP BY events.id_event
) b
WHERE events.id_event = b.id_event;


ALTER TABLE events ADD COLUMN waitlist_rsvp_count_from_rsvps integer DEFAULT NULL;

UPDATE events 
SET waitlist_rsvp_count_from_rsvps = b.count
FROM (
  SELECT 
    events.id_event, count(id_rsvp) AS count
  FROM rsvps
  LEFT JOIN events  USING(id_event) 
  WHERE response = 'waitlist'
  GROUP BY events.id_event
) b
WHERE events.id_event = b.id_event;

UPDATE events set yes_rsvp_count_from_rsvps=0 WHERE yes_rsvp_count_from_rsvps IS NULL;
UPDATE events set no_rsvp_count_from_rsvps=0 WHERE no_rsvp_count_from_rsvps IS NULL;
UPDATE events set waitlist_rsvp_count_from_rsvps=0 WHERE waitlist_rsvp_count_from_rsvps IS NULL;

ALTER TABLE groups ADD COLUMN number_of_events integer DEFAULT 0;
UPDATE groups 
SET number_of_events = b.count
FROM (
  SELECT 
    events.id_group, count(id_event) AS count
  FROM events
  LEFT JOIN groups  USING(id_group) 
  GROUP BY events.id_group
) b
WHERE groups.id_group = b.id_group;

ALTER TABLE groups ADD COLUMN first_event_time TIMESTAMP NULL;
ALTER TABLE groups ADD COLUMN last_event_time TIMESTAMP NULL;
UPDATE groups 
SET first_event_time = b.time
FROM ( SELECT events.id_group, min(time) AS time FROM events LEFT JOIN groups  USING(id_group) GROUP BY events.id_group) b
WHERE groups.id_group = b.id_group;

UPDATE groups 
SET last_event_time = b.time
FROM ( SELECT events.id_group, max(time) AS time FROM events LEFT JOIN groups  USING(id_group) GROUP BY events.id_group) b
WHERE groups.id_group = b.id_group;

ALTER TABLE groups ADD COLUMN max_yes_at_one_event integer DEFAULT 0;
UPDATE groups 
SET max_yes_at_one_event = b.count
FROM (
  SELECT 
    events.id_group, max(yes_rsvp_count_from_rsvps) AS count
  FROM events
  LEFT JOIN groups  USING(id_group) 
  GROUP BY events.id_group
) b
WHERE groups.id_group = b.id_group;

ALTER TABLE groups ADD COLUMN no_member_who_ever_rsvpd_yes integer DEFAULT 0;
UPDATE groups 
SET  no_member_who_ever_rsvpd_yes = b.count
FROM (
  SELECT 
    rsvps.id_group, count(DISTINCT id_member) AS count
  FROM rsvps
  LEFT JOIN groups  USING(id_group) 
  WHERE response='yes'
  GROUP BY rsvps.id_group
) b
WHERE groups.id_group = b.id_group;
