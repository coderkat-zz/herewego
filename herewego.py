from flask import Flask, render_template, redirect, request, session
from flask import url_for, g, flash
import model
from model import session as db_session, Users, Stories, Preferences

app = Flask(__name__)
app.secret_key = "bananabananabanana"




@app.route("/")
def index():
	return render_template("index.html")

@app.route("/login", methods=["GET"])
def login():
	return render_template("login.html")

@app.route("/validate", methods=['POST'])
def validate_login():
	# TODO: GO THROUGH AND SANITIZE STUFF --> will need to encode form input to match what's encoded in the database (using urllib.quote())
	form_email = request.form['email']
	form_password = request.form['password']

	#form_email and form_password must both exist and match in db for row to be an object. Row is the entire row from the users table, including the id
	row = model.session.query(model.Users).filter_by(email=form_email, password=form_password).first()

	if row: 		
		session['email'] = request.form['email']
		session['user_id'] = row.id
		flash('Logged in as: ' + session['email'])
		return redirect("/news")		
	else:
		flash('Please enter a valid email address and password.')
		return redirect("/login") 

@app.route("/news")
def news():
	# TODO: make this more random, pull from various sources, etc...
	stories_list = model.session.query(model.Stories).limit(10).all()
	return render_template("news.html", story_list = stories_list)

@app.route("/like", methods=["POST"])
def like():
	story = request.form("story_id")
	new_like = model.Preferences(story_id=story, user_id=session['user_id'], preference=1)

	model.session.add(new_like)
	model.session.commit()
	return redirect(url_for('news'))


@app.route("/dislike", methods=["POST"])
def dislike():
	story = request.form("story_id")
	new_dislike = model.Preferences(story_id=story, user_id=session['user_id'], preference=0)

	model.session.add(new_dislike)
	model.session.commit()
	return redirect(url_for('news'))


if __name__ == "__main__":
	app.run(debug = True)