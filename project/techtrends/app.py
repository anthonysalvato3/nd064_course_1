import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

import sys, logging, datetime

conn_count = 0
time_format = "%m-%d-%Y, %H:%M:%S"

# Function to get a database connection.
# This function connects to database with the name `database.db`


def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global conn_count
    conn_count += 1
    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info("%s, Article does not exist!", datetime.datetime.now().strftime(time_format))
      return render_template('404.html'), 404
    else:
      app.logger.info("%s, Article \"%s\" retrieved!", datetime.datetime.now().strftime(time_format), post[2])
      return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    app.logger.info("%s, About page retrieved!", datetime.datetime.now().strftime(time_format))
    return render_template('about.html')

# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info("%s, Post with title \"%s\" created!", datetime.datetime.now().strftime(time_format), title)

            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result": "OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    return response


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    post_count = len(posts)
    connection.close()
    response = app.response_class(
            response=json.dumps({"status": "success", "code": 200, "data": {
                                "db_connection_count": conn_count, "post_count": post_count}}),
            status=200,
            mimetype='application/json'
    )

    return response


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # root = logging.getLogger()
    # root.setLevel(logging.DEBUG)
    
    # handler1 = logging.StreamHandler(sys.stdout)

    # handler2 = logging.StreamHandler(sys.stderr)

    # root.addHandler(handler1)
    # root.addHandler(handler2)

    app.run(host='0.0.0.0', port='3111')
