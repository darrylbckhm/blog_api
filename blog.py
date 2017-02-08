#!/usr/bin/python
#Author: Darryl Beckham

import json
import sqlite3
import wtforms
from flask import Flask, request, render_template

from wtforms import Form, TextField, TextAreaField, SubmitField, validators

#Creates basic html form with two TextField boxes for entry
class PostForm(Form):
  title=TextField('Title', [validators.Length(min=1)])
  body=TextField('Body', [validators.Length(min=1)])

#Creates flask object to run app
app = Flask(__name__)

#Returns connection to blog database
def connectDB():
  return sqlite3.connect('blog.db')

#Connects to database. Counts the total number of entries in the database + 1 to find out the post_id of the next blog post.
#Takes two parameters: title of article, and body of article
#Parameters and post_id are inserted into the database with a sql statement
def insertDB(title,body):
  try:
    conn = connectDB()
    c = conn.cursor()
    post_id = int(str(c.execute('SELECT Count(*) FROM posts').fetchone()).translate(None, '(),')) + 1
    c.execute("INSERT INTO posts VALUES (?, ?, ?)", (post_id,title,body))
    conn.commit()
    conn.close()
    return True
  except:
    return False

#prints the column headers within a row of db
def printDBInfo():
  conn = connectDB()
  c = conn.cursor()
  for row in conn.execute("pragma table_info('posts')").fetchall():
    print(row)
  conn.close()

#Deletes everything from the database
def clearDB():
  conn = connectDB()
  conn.execute('DELETE FROM posts')
  conn.commit()
  conn.close()

#Prints everything in database
def printDB():
  conn = connectDB()
  c = conn.cursor()
  for row in c.execute('SELECT * from posts'):
    print(row)
  conn.close()

#Creates endpoint at /posts and handles a GET request to the blog database and returns all entries in posts
@app.route('/posts', methods=['GET'])
def posts():
  conn = connectDB()
  c = conn.cursor()
  formattedPosts = []
  for row in c.execute('SELECT * FROM posts'):
    formattedPosts.append({
      'post_id': row[0],
      'title': row[1],
      'body': row[2]
    })
  conn.close()

  return json.dumps({'posts': formattedPosts}), 200, {'Content-Type': 'application/json'}

#Creates endpoint at the root which returns the api homepage
#From here, users can choose between adding a new post or displaying all posts
@app.route('/', methods=['GET'])
def index():
  return render_template("index.html")

#Creates endpoint at /post which invokes the PostForm object. If we POST, then we select the data entered into the title and body fields and pass them into our insertDB function and return to the root page
@app.route('/post', methods=['GET','POST'])
def post():
  form = PostForm(request.form)
  if request.method == "POST":
    title = form.title.data
    body = form.body.data
    if(title != ""):
      insertDB(title,body)
      return render_template('index.html')
  return render_template('post.html', form=form) 

if __name__ == "__main__":
  app.run(debug=True)
