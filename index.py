import os, psycopg2, psycopg2.extras, json
from flask import Flask, Response, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

app = Flask(__name__)

# ====================================================================================
@app.before_request
def before_request():
  try:
    g.db = psycopg2.connect(os.environ['DATABASE_URL'])
    g.db.autocommit = True
    g.db_cursor = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
  except Exception as inst:
    app.logger.error('Error: %s' % inst)
    abort(500)
# ====================================================================================
@app.route('/groups/count_cities.html')
@app.route('/groups/count_states.html')
def horizontal_barchart_tsv_html():
  return render_template("horizontal-barchart-tsv.html", data_url = request.path.replace('.html', '.tsv') )

@app.route('/groups/count_cities.tsv')
def count_cities():
    try: 
      result = "label\tfrequency"
      g.db_cursor.execute("""select city as label,count(*) as count from groups group by city order by count desc""")
      for row in g.db_cursor.fetchall():
        result += "\n%s\t%d" % ( row['label'], row['count'] )
    except Exception as ex:
      app.logger.error('exception %s' % ex)
      pass
    return Response(result, mimetype='text/plain')
    #return Response(result, mimetype='text/tab-separated-values')

@app.route('/groups/count_states.tsv')
def count_states():
    try: 
      result = "label\tfrequency"
      g.db_cursor.execute("""select state as label,count(*) as count from groups group by state order by count desc""")
      for row in g.db_cursor.fetchall():
        result += "\n%s\t%d" % ( row['label'], row['count'] )
    except Exception as ex:
      app.logger.error('exception %s' % ex)
      pass
    #return Response(result, mimetype='text/plain')
    return Response(result, mimetype='text/tab-separated-values')

@app.route('/groups/group_size_histogram.json')
def group_size_histogram():
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
    except Exceptions as ex:
      app.logger.error('Error: could not read from database %s' % ex)
      resp = jsonify({ 'status': 404, 'message': 'could not read from database'})
      resp.status_code = 500
    return resp

# ====================================================================================
@app.route('/')
def index():
    g.db_cursor.execute("""select a.no_groups, b.no_events, c.no_members, d.no_venues, e.no_rsvps from 
      (select count(*) as no_groups from groups) AS a, 
      (select count(*) as no_events from events) AS b,
      (select count(*) as no_members from members) AS c,
      (select count(*) as no_venues from venues) AS d,
      (select count(*) as no_rsvps from rsvps) AS e
      """)
    return render_template("index.html", db = g.db_cursor.fetchone())
# ====================================================================================
if __name__ == '__main__':
  app.run(debug=True)
# ====================================================================================
