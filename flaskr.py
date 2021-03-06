# all the imports
import sqlite3
import configs
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

# create our little application :)
app = Flask(__name__)
app.config.from_object(configs) # we import the config values from configs.py

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select id, title, text from entries order by id desc')
    entries = [dict(id=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
    # Each entry in entries has the values id, title, and text.
    return render_template('show_entries.html', entries=entries)

# raccoon added view, for looking at individual blog entries
@app.route('/entry/<post_id>')
def show_entry(post_id):
    try:
        post_id = int(post_id)    # check if post_id is an int
    except:
        return abort(404)
    
    # Get entry from database
    cur = g.db.execute('select title, text from entries where id=%d' % post_id)
    entry = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    
    if len(entry) == 0:
        return abort(404) # entry did not exist
    else:
        entry = entry[0] # we only needed the first entry (and there should only be one)
    
    # example entry: {'text': u'my blogging', 'title': u'my title'}
    return render_template('entry.html', entry=entry)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

# This always goes at the bottom of the file
# What is ever inside this if statement runs automatically when file is running
if __name__ == '__main__':
    app.run(host='127.0.0.1')
