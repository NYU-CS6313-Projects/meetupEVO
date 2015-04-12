/* drop tables in reverse order of creating */

DROP TABLE rsvps;

CREATE TABLE rsvps (
  id_rsvp BIGINT NOT NULL,
  /* this is a join table between member and event */
  id_member VARCHAR(30) NULL, /* one day this will REFERENCES members (id_member),  */
  id_event VARCHAR(30) NULL,  /* one day this will REFERENCES events (id_event), */
  name_event VARCHAR(100) DEFAULT '',
  time_event TIMESTAMP NULL,
  time_event_time TIME NULL,
  time_event_wday SMALLINT NULL,

  id_group  VARCHAR(30) NULL,   /* on day this will   REFERENCES groups (id_group), */
  join_mode_group VARCHAR(100)  NULL,
  created_group TIMESTAMP NULL,
  created_group_time TIME NULL,
  created_group_wday SMALLINT NULL,

  lon_group FLOAT,
  lat_group FLOAT,
  urlname_group VARCHAR(250)  NULL,

  /* core attributes */
  response VARCHAR(20)  NULL,
  watching BOOLEAN  NULL,
  comments VARCHAR(1000)  NULL,
  guests BIGINT  NULL,
  /* time */
  created TIMESTAMP NULL,
  created_time TIME  NULL,
  created_wday SMALLINT  NULL,
  mtime TIMESTAMP NULL,
  mtime_time TIME NULL,
  mtime_wday SMALLINT  NULL
);
CREATE INDEX index_rsvps_id_rsvp   ON rsvps(id_rsvp);
CREATE INDEX index_rsvps_id_event  ON rsvps(id_event);
CREATE INDEX index_rsvps_id_member ON rsvps(id_member);
CREATE INDEX index_rsvps_created      ON rsvps(created);
CREATE INDEX index_rsvps_created_time ON rsvps(created_time);
CREATE INDEX index_rsvps_created_wday ON rsvps(created_wday);
CREATE INDEX index_rsvps_mtime      ON rsvps(mtime);
CREATE INDEX index_rsvps_mtime_time ON rsvps(mtime_time);
CREATE INDEX index_rsvps_mtime_wday ON rsvps(mtime_wday);

CREATE INDEX index_rsvps_id_group  ON rsvps(id_group);
