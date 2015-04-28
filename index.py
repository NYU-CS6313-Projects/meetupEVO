import os, psycopg2, psycopg2.extras, json, re, random, csv, io, sys, numpy, pandas
from flask import Flask, Response, request, session, g, redirect, url_for, abort, render_template, flash, jsonify, json
from collections import Counter

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
@app.route('/groups/count_cities.html')
def groups_count_cities_html():
  return render_template("horizontal-barchart-tsv.html", 
      data_url = request.path.replace('.html', '.tsv'), 
      title = "Count Groups in Cities" )

@app.route('/groups/all.csv')
def groups_all_csv():
    result = io.BytesIO()
    writer = csv.writer(result, quoting=csv.QUOTE_NONNUMERIC)
    try: 
      all_columns = [
          "id_group", "id_organizer", "name_organizer", "id_category", "name_category", "shortname_category",
          "name", "description", "link", "who", "join_mode", "created", "created_wday",
          "urlname", "visibility", "no_members",
          "rating",
          "city", "lat", "lon", "state", "country", "timezone",
          "number_of_events", "first_event_time", "last_event_time",
          "max_yes_at_one_event", "no_member_who_ever_rsvpd_yes"
          ]
      columns = [
          "id_group", "id_organizer", "name_organizer", "id_category", "name_category", "shortname_category",
          "name", "link", "join_mode", "created", 
          "no_members", "rating",
          "city", "lat", "lon", "state", "country", "timezone",
          "number_of_events", "first_event_time", "last_event_time",
          "max_yes_at_one_event", "no_member_who_ever_rsvpd_yes"
      ]
      writer.writerow( columns )
      g.db_cursor.execute("select " + ",".join(columns) + " from groups where created is not null and number_of_events > 0 limit 3000")
      for row in g.db_cursor.fetchall():
        writer.writerow( [ row[c] for c in columns ] )
    except Exception as ex:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      app.logger.error('exception %s in line %d' % (ex, exc_tb.tb_lineno))
      pass
    return Response(result.getvalue(), mimetype='text/plain')

@app.route('/groups/count_cities.tsv')
def groups_count_cities_tsv():
    try: 
      result = "label\tfrequency"
      g.db_cursor.execute("""select city as label,count(*) as count from groups group by city order by count desc""")
      for row in g.db_cursor.fetchall():
        result += "\n%s\t%d" % ( row['label'], row['count'] )
    except Exception as ex:
      app.logger.error('exception %s' % ex)
      pass
    return Response(result, mimetype='text/plain')

# ====================================================================================
@app.route('/groups/index.html')
def groups():
  return render_template("groups.html", title = "List of Groups")

@app.route('/groups/simple.html')
def groups_simple():
  return render_template("groups_simple.html", title = "List of Groups")

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

@app.route('/groups/count_states.html')
def groups_count_states_html():
  return render_template("horizontal-barchart-tsv.html", 
      data_url = request.path.replace('.html', '.tsv'), 
      title = "Count Groups in State")

@app.route('/groups/count_states.tsv')
def groups_count_states_tsv():
    try: 
      result = "label\tfrequency"
      g.db_cursor.execute("""select state as label,count(*) as count from groups group by state order by count desc""")
      for row in g.db_cursor.fetchall():
        result += "\n%s\t%d" % ( row['label'], row['count'] )
    except Exception as ex:
      app.logger.error('exception %s' % ex)
      pass
    return Response(result, mimetype='text/plain')
    
@app.route('/rsvps/weekday_histogram.json')
def rsvps_weekday_histogram_json():
    try: 
      g.db_cursor.execute("""
        select created_wday, count(*) from rsvps group by created_wday
        """)
      resp = jsonify({ 
          'status': 200, 
          'color': 'purple',
          'message': 'ok', 
          'x_label': 'day of the week', 
          'y_label': 'number of rsvps on this day', 
          'data':  g.db_cursor.fetchall() 
      })
      resp.status_code = 200
    except Exception as ex:
      app.logger.error('Error: could not read from database %s' % ex)
      resp = jsonify({ 'status': 404, 'message': 'could not read from database'})
      resp.status_code = 500
    return resp  


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




@app.route('/groups/group_size_histogram.json')
def group_size_histogram_json():
    try: 
      g.db_cursor.execute("""
        select width_bucket(no_members,0,50000,30) as bucket, count(*) as count from groups group by 1 order by 1
        """)
      resp = jsonify({ 
          'status': 200, 
          'message': 'ok', 
          'x_label': 'number of members in group, 30 bins', 
          'y_label': 'number of group', 
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

@app.route('/o.html')
def o():
  return render_template("o.html")

@app.route('/l.html')
def l():
  return render_template("l.html")

@app.route('/b.html')
def b():
  return render_template("b.html")

@app.route('/histo.html')
def histo():
  group_df = pd.read_sql("SELECT * from groups", g.db, index_col='id_group')
  rsvp_df  = pd.read_sql("SELECT * from event_rsvps_by_year", g.db)

  rsvp_df.groupby('id_group')
  return render_template("histo.html", data =  [])

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

