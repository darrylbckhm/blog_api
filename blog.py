#!/usr/bin/python
#Author: Darryl Beckham

import json
import sqlite3
import wtforms
from flask import Flask, request, render_template

from wtforms import Form, TextField, TextAreaField, SubmitField, validators

class MainForm(Form):
  data = None

class PostForm(Form):
  title=TextField('Title', [validators.Length(min=1)])
  body=TextField('Body', [validators.Length(min=1)])

app = Flask(__name__)

def connectDB():
  return sqlite3.connect('blog.db')

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

def printDBInfo():
  conn = connectDB()
  c = conn.cursor()
  for row in conn.execute("pragma table_info('posts')").fetchall():
    print(row)
  conn.close()

def clearDB():
  conn = connectDB()
  conn.execute('DELETE FROM posts')
  conn.commit()
  conn.close()

def printDB():
  conn = connectDB()
  c = conn.cursor()
  for row in c.execute('SELECT * from posts'):
    print(row)
  conn.close()

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

@app.route('/', methods=['GET'])
def index():
  return render_template("index.html")

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
