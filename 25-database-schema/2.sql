
CREATE TABLE groups (
  id_group BIGINT primary key NOT NULL,
  -- has one organizer
  id_organizer BIGINT NULL references members(id_member),
  name_organizer VARCHAR(100)  NULL,
  -- is in one category
  id_category BIGINT  NULL,
  name_category VARCHAR(100)  NULL,
  shortname_category VARCHAR(100)  NULL,
  -- core group attributes
  name VARCHAR(100)  NULL,
  description VARCHAR(100)  NULL,
  link VARCHAR(100)  NULL,
  who VARCHAR(100)  NULL,
  join_mode VARCHAR(100)  NULL,
  created VARCHAR(1000)  NULL,
  created_wday BIGINT  NULL,
  urlname VARCHAR(100)  NULL,
  visibility VARCHAR(100)  NULL,
  -- attributes that change over time
  no_members BIGINT NULL,
  rating FLOAT NULL,
  -- location
  city VARCHAR(100)  NULL,
  lat FLOAT  NULL,
  lon FLOAT  NULL,
  state VARCHAR(100)  NULL,
  country VARCHAR(100)  NULL,
  timezone VARCHAR(100)  NULL
);

CREATE TABLE events (
  id_event BIGINT primary key NULL,
  -- belongs to one group
  id_group BIGINT NOT NULL references groups(id_group),
  -- has one venue
  id_venue BIGINT NOT NULL references venue(id_venue),
  -- core event attributes
  name VARCHAR(100)  NULL,
  description VARCHAR(100)  NULL,
  time VARCHAR(1000)  NULL,
  time_wday BIGINT  NULL,
  utc_offset BIGINT  NULL,
  event_url VARCHAR(100)  NULL,
  duration FLOAT  NULL,
  status VARCHAR(100)  NULL,
  description VARCHAR(100)  NULL,
  why VARCHAR(100)  NULL,
  how_to_find_us VARCHAR(100)  NULL,
  rating FLOAT  NULL,
  visibility VARCHAR(100)  NULL,
  created VARCHAR(1000)  NULL,
  created_wday BIGINT  NULL,
  updated BIGINT  NULL,
  photo_url VARCHAR(100)  NULL,
  -- fee
  label_fee VARCHAR(100)  NULL,
  amount_fee FLOAT  NULL,
  accepts_fee VARCHAR(100)  NULL,
  currency_fee VARCHAR(100)  NULL,
  description_fee VARCHAR(100)  NULL,
  required_fee VARCHAR(100)  NULL,
  -- counts
  yes_rsvp_count BIGINT  NULL,
  waitlist_count BIGINT  NULL,
  maybe_rsvp_count BIGINT  NULL,
  count_rating FLOAT  NULL,
  average_rating FLOAT  NULL,
  headcount BIGINT  NULL,
);

CREATE TABLE venue (
  id_venue BIGINT primary key NULL,
  name VARCHAR(100)  NULL,
  address_1 VARCHAR(100)  NULL,
  address_2 VARCHAR(100)  NULL,
  phone VARCHAR(100)  NULL,
  lon FLOAT  NULL,
  lat FLOAT  NULL,
  zip VARCHAR(100)  NULL,
  city VARCHAR(100)  NULL
  state VARCHAR(100)  NULL,
  country VARCHAR(100)  NULL,
  repinned VARCHAR(100)  NULL
);

CREATE TABLE members (
  id_member BIGINT primary key NULL,
  -- belongs to many groups!!! should be a separate table!!
  id_group VARCHAR(100)  NULL,
  -- core member attributes
  name VARCHAR(100)  NULL,
  status VARCHAR(100)  NULL,
  bio VARCHAR(100)  NULL,
  visited BIGINT  NULL,
  joined BIGINT  NULL,
  link VARCHAR(100)  NULL,
  -- location
  city VARCHAR(100)  NULL,
  lon FLOAT  NULL,
  lat FLOAT  NULL,
  state VARCHAR(100)  NULL,
  country VARCHAR(100)  NULL,
  hometown VARCHAR(100)  NULL,
  -- photo
  id_photo FLOAT  NULL,
  link_photo VARCHAR(100)  NULL,
  thumb_link_photo VARCHAR(100)  NULL,
  highres_link_photo VARCHAR(100)  NULL,
);

CREATE TABLE rsvps (
  rsvp_id BIGINT primary key NULL,
  -- this is a join table between member and event
  id_member BIGINT NOT NULL references members(id_member),
  id_event VARCHAR(100) NOT NULL references events(id_event),
  -- core attributes
  response VARCHAR(100)  NULL,
  watching FLOAT  NULL,
  comments VARCHAR(100)  NULL,
  guests BIGINT  NULL,
  -- time
  created VARCHAR(1000)  NULL,
  created_time VARCHAR(100)  NULL,
  created_wday BIGINT  NULL,
  mtime VARCHAR(1000)  NULL,
  mtime_time VARCHAR(100)  NULL,
  mtime_wday BIGINT  NULL
);
