import os, psycopg2, psycopg2.extras
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


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
