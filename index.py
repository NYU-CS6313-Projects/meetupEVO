import os, psycopg2, psycopg2.extras, json, re, random, csv, io, sys
import numpy as np
import pandas as pd
from flask import Flask, Response, request, session, g, redirect, url_for, abort, render_template, flash, jsonify, json
from collections import Counter
import mimetypes

mimetypes.add_type('text/plain', '.csv')

app = Flask(__name__)

app.json_encoder =  json.JSONEncoder
app.config['JSON_AS_ASCII'] = True
app.config['JSON_SORT_KEYS'] = True

# ====================================================================================
@app.before_request
def before_request():
  g.db = None
  g.db_cursor = None
  try:
    g.db = psycopg2.connect(os.environ['DATABASE_URL'])
    g.db.autocommit = True
    g.db_cursor = g.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
  except Exception as inst:
    app.logger.error('Error connecting to %s' % os.environ['DATABASE_URL'])
    g.error_message = "Could not connect to database."
    # abort(500)

# ====================================================================================
@app.route('/about.html')
def about():
  return render_template("about.html", title = "About this Site")

@app.route('/rsvps/weekday_histogram.html')
def circle():
  return render_template("rsvp_weekday_histogram.html", title = "Histogram of RSVPs on Weekdays")


# Ouafa Trying Out!
# ====================================================================================
@app.route('/events/Timeseries_group_Evolution_by_RSVP.html')
def line():
  return render_template("Timeseries_group_Evolution_by_RSVP.html", title = "Timeline of group evolution by Event RSVPs")


# ======== this version of map does not work: openstreetmap only served on http ======
# ======== not https, so is not loaded :( 
@app.route('/map.html')
def map():
  return render_template("map.html", title = "Map of Locations", description = "Showing no data as of yet.")

# ====================================================================================
@app.route('/groups/index.html')
def groups():
  return render_template("groups.html", title = "List of Groups")

@app.route('/groups/static.html')
def groups_static():
  g.db_cursor.execute("""select * from groups order by name""")
  list_of_groups = g.db_cursor.fetchall()
  return render_template("groups-static.html", title = "List of Groups", groups = list_of_groups)

@app.route('/group/<id_group>')
def group(id_group):
  g.db_cursor.execute("""select * from groups where id_group=%(id)s""", { 'id': id_group })
  this_group = g.db_cursor.fetchone()
  g.db_cursor.execute("""select * from events where id_group=%(id)s order by time""", { 'id': id_group })
  list_of_events = g.db_cursor.fetchall()
  app.logger.error(this_group['name'])
  g.db_cursor.execute("""
      SELECT
        EXTRACT(EPOCH FROM time) AS starting_time, 
        EXTRACT(EPOCH FROM time) + COALESCE(duration,0) AS ending_time,  
        yes_rsvp_count_from_rsvps AS yes,
        yes_rsvp_count_from_rsvps/max_yes_at_one_event AS size
      FROM 
        events LEFT JOIN groups USING (id_group)
      WHERE events.id_group=%(id)s 
      ORDER BY time""", { 'id': id_group })
  timeline=[]
  for t in g.db_cursor.fetchall():
    timeline.append(t)
  app.logger.error(timeline)
  return render_template("group.html", 
      title = "Group %s" % this_group["name"], 
      group = this_group, 
      events = list_of_events, 
      timeline_json=json.dumps(timeline)
  )

###Timeline series data
@app.route('/events/group_evolution_timeseries.json')
def events_group_evoltution_timeseries_json():
    try: 
      c = request.args.get("category")

      if c is None or c == '' or c == '*':
        g.db_cursor.execute("""
          select * from (select extract(year from created) "year", id_group, SUM(yes_rsvp_count_from_rsvps) from events 
          group by year, id_group 
          order by id_group, "year"
          )t 
          Where t."year" is not null
          """)
          #limit 500
      else:
        g.db_cursor.execute("""
          select t.year, t.id_group, t.sum  from (select extract(year from created) "year", id_group, SUM(yes_rsvp_count_from_rsvps) from events 
          group by year, id_group 
          order by id_group, "year"
          ) t LEFT JOIN groups USING (id_group)
          where t."year" is not null
          AND groups.name_category = %(category)s
          """, { "category": c } )
          # limit 500

      resp = jsonify({ 
          'status': 200, 
          'color': 'pink',
          'message': 'ok', 
          'x_label': 'year', 
          'y_label': 'number of rsvps on this year', 
          'data':  g.db_cursor.fetchall() 
      })
      resp.status_code = 200
    except Exception as ex:
      app.logger.error('Error: could not read from database %s' % ex)
      resp = jsonify({ 'status': 404, 'message': 'could not read from database'})
      resp.status_code = 500
    return resp

# ====================================================================================
@app.route('/intro.html')
def intro():
  try:
    g.db_cursor.execute("""select a.no_groups, b.no_events, c.no_members, d.no_venues, e.no_rsvps from 
      (select count(*) as no_groups from groups) AS a, 
      (select count(*) as no_events from events) AS b,
      (select count(*) as no_members from members) AS c,
      (select count(*) as no_venues from venues) AS d,
      (select count(*) as no_rsvps from rsvps) AS e
      """)
    counts = g.db_cursor.fetchone()
    g.db_cursor.execute("""select name from groups where name is not null and random() < 1""")
    word_counter = Counter()
    total_count = 0
    for name in g.db_cursor.fetchall():
      for w in name['name'].split(" "):
        w = w.lower()
        if re.match("^\w+$", w) and not w in ['of', 'the', 'and', 'in', 'meetup', 'for', 'club', 'group', 'city', 'nyc', 'new', 'york']:
            # 'nyc', 'new', 'york', 'brooklyn', 'jersey', 'ny', 'westchester', 'nj','manhattan', 'staten', 'island'
          total_count += 1
          word_counter[ w ] += 1 
    word_weight={}
    for w in word_counter.keys():
      p = 100.0 * word_counter[ w ]  / total_count
      if p > 0.2:
        word_weight[ w ] = p 
  except Exception as ex:
    counts = { 'no_groups': 0, 'no_events': 0, 'no_members': 0, 'no_venues': 0, 'no_rsvps': 0 }
    word_weight = { 'error': 0.70, 'no': 0.1, 'database': 0.3, 'sorry': 0.2, 'broken': 0.3, 'sad': 0.4 }
  word_counter_keys = word_weight.keys()
  random.shuffle(word_counter_keys)
  return render_template("intro.html", counts = counts, word_counter = word_weight, word_counter_keys = word_counter_keys )

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/v2.html')
def sketch():
  return render_template("v2.html")

@app.route('/events/time.csv')
def event_time():
  l = 9000
  if len(request.args.getlist('id_group[]')) == 0:
    sql = g.db_cursor.mogrify("""
      SELECT * FROM event_rsvps_by_year WHERE id_group IN (
        SELECT id_group FROM groups WHERE number_of_events>0 LIMIT %s
      )""", (l,))
  else:
    sql = g.db_cursor.mogrify("""
      SELECT * FROM event_rsvps_by_year WHERE id_group IN (
        SELECT id_group FROM groups WHERE number_of_events>0 AND id_group IN %s  LIMIT %s
      )""", ( tuple( request.args.getlist('id_group[]') ), l ) )
  app.logger.error('time.csv: %s' % sql)
  df = pd.read_sql(sql , g.db)
  return Response(df.to_csv(index=False), mimetype='text/plain')

@app.route('/build-csv')
def build_csv():
  columns = [
      "id_group", "id_category", "name_category", "shortname_category",
      "name", "link", "join_mode", "created", 
      "no_members", "rating",
      "city", "lat", "lon", "state", "country", 
      "number_of_events", "first_event_time", "last_event_time",
      "max_yes_at_one_event", "no_member_who_ever_rsvpd_yes"
  ]
  db = g.db
  sql = "SELECT " + (",".join(columns)) + " from groups where (created is not null) and (created < '2014-01-01') and (no_member_who_ever_rsvpd_yes > 0) and (number_of_events > 0)"
  group_df = pd.read_sql(sql, db, index_col='id_group')
  group_df.to_csv(open("static/groups.csv", "w"))

  df = pd.read_sql("SELECT * from event_rsvps_by_year", db)
  df.to_csv(open("static/group-evolution-by-year.csv","w"), index=False)
  
  rsvp_by_year = df.pivot(index='id_group', columns='time_bin', values='sum')
  rsvp_by_year.rename(columns=lambda x: "rsvps-year-%04d" % x.year, inplace=True)
  rsvp_by_year.fillna(0, inplace=True)
  for c in rsvp_by_year.columns.values:
    if "rsvps-" in c:
      rsvp_by_year[c] =  rsvp_by_year[c].astype('int')

  df = pd.read_sql("SELECT * from event_rsvps_by_month", db)
  df.to_csv(open("static/group-evolution-by-month.csv","w"), index=False)

  rsvp_by_month = df.pivot(index='id_group', columns='time_bin', values='sum')
  rsvp_by_month = pd.read_sql("SELECT * from event_rsvps_by_month", db).pivot(index='id_group', columns='time_bin', values='sum')
  rsvp_by_month.rename(columns=lambda x: "rsvps-month-%04d-%02d" % (x.year, x.month), inplace=True)
  rsvp_by_month.fillna(0, inplace=True)
  for c in rsvp_by_month.columns.values:
    if "rsvps-" in c:
      rsvp_by_month[c] =  rsvp_by_month[c].astype('int')

  #data = group_df.merge(rsvp_by_year, left_index=True, right_index=True)
  #data = data.merge(rsvp_by_month, left_index=True, right_index=True)


  return "<h1>Created</h1><a href='static/groups.csv'>group.csv</a>"

# ====================================================================================
@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_rror(e):
  app.logger.error('Internal Server Error:')
  return render_template('500.html'), 500
# ====================================================================================
if __name__ == '__main__':
  app.run(debug=True)
# ====================================================================================

