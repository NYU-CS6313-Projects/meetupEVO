/* drop tables in reverse order of creating */

DROP TABLE members;

CREATE TABLE members (
  id_member VARCHAR(20) primary key NULL,
  /* belongs to many groups!!! should be a separate table!! */
  id_group VARCHAR(20)  NULL,
  /* core member attributes */
  name VARCHAR(100)  NULL,
  status VARCHAR(100)  NULL,
  bio VARCHAR(500)  NULL,
  visited BIGINT  NULL,
  joined BIGINT  NULL,
  link VARCHAR(100)  NULL,
  /* location */
  city VARCHAR(100)  NULL,
  lon FLOAT  NULL,
  lat FLOAT  NULL,
  state VARCHAR(100)  NULL,
  country VARCHAR(100)  NULL,
  hometown VARCHAR(100)  NULL,
  /* photo */
  id_photo FLOAT  NULL,
  link_photo VARCHAR(100)  NULL,
  thumb_link_photo VARCHAR(100)  NULL,
  highres_link_photo VARCHAR(100)  NULL
);
