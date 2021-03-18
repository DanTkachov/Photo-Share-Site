######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################
#this is a test. change should be merged; only this line changed
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from forms import UserSearchForm, CommentForm
from datetime import datetime
import pw

from dotenv import load_dotenv
load_dotenv()
import os
DATABASE_PASSWORD = pw.DATABASE_PASSWORD_PW
DATABASE_USER = pw.DATABASE_USER_PW

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!



#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = DATABASE_USER
app.config['MYSQL_DATABASE_PASSWORD'] = DATABASE_PASSWORD
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		cursor.execute("INSERT INTO Users (email, password, first_name, last_name) VALUES ('{0}','{1}','{2}','{3}')".format(email, password, first_name, last_name))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=first_name, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

'''
	This is the search method
	It's called whenever the user enters the search page.

	It creates a form called search that is an object of type UserSearchForm defined in forms.py.

	if it's a POST type, that means that the user has submitted information in a form and clicked submit or enter. 
	In that case, it calls another method search_results with the search form as it's argument
'''
@app.route("/search", methods=['GET','POST'])
def search():
	search = UserSearchForm(request.form)
	if(request.method == 'POST'):
		return search_results(search)


	return render_template('search.html', form=search)

@app.route("/searchTag", methods=['GET','POST'])
def searchTag():
	if(request.method == 'POST'):
		tag = request.form.get("searchtag")
		return search_by_tag(tag)


	return render_template('searchtag.html')


@app.route("/like/<picture_id>.html", methods=['POST'])
def likePhoto(picture_id):
	if(flask_login.current_user.is_authenticated):
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("INSERT IGNORE INTO UserLikes (picture_id, user_id) VALUES (%s,%s)",(picture_id, uid))
		conn.commit()
		return flask.redirect(('/picture/'+picture_id))
	else:
		return render_template("home.html", message = "Please login to like a photo")


def search_by_tag(tag):
	results = getAllPhotosByTag(tag)
	print(results)
	return render_template('searchtag.html', results = results)

'''
	This is the search_results method

	It takes a search form object and queries our database based on whatever the user searched for

	It returns the results.html file with the query results passed as an argument
'''
@app.route('/results')
def search_results(search):
	results = []
	search_string = search.search.data #search(the search for object).search(the search field in the form).data(the data inside of the search field)
	select = search.select.data #select is the selection the user made to filter the search
	cursor = conn.cursor() #we create a cursor in order to run an sql query
	cursor.execute("SELECT email, first_name, last_name, user_id FROM Users AS u WHERE {0} REGEXP '^{1}'".format(select,search_string)) #we execute the query using our parameters from the search form object
	results = cursor.fetchall() #fetchall grabs all the rows returned by our query as a list
	return render_template('results.html', results=results)

@app.route('/user/<uid>', methods=['GET'])
def userProfile(uid):
	return render_template('UserProfile.html', user=getUserInfo(uid), photos=getUsersPhotos(uid),base64=base64)

@app.route('/user/<uid2>', methods=['GET','POST'])
def addFriend(uid2):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	#print(uid,uid2)
	cursor.execute("INSERT IGNORE INTO Friends(user_id1, user_id2) VALUES (%s,%s)", (uid, uid2))
	conn.commit()
	cursor.execute("INSERT IGNORE INTO Friends(user_id2, user_id1) VALUES (%s,%s)", (uid, uid2))
	conn.commit()
	return flask.redirect(flask.url_for('userProfile', uid=uid2))
def getUserFriends(uid):
	cursor = conn.cursor()
	#print(uid2)
	cursor.execute("SELECT DISTINCT first_name FROM Users WHERE user_id = (SELECT user_id2 FROM friends WHERE user_id1 = %s)",(uid))
	#cursor.execute("SELECT DISTINCT user_id2 FROM friends WHERE user_id1 = %s",(uid2))
	return cursor.fetchall()

@app.route('/<uid>/friendlist.html', methods=['POST'])
def viewFriends(uid):
	return render_template('friendlist.html', friends = getUserFriends(uid), user = getUserInfo(uid), base64=base64)


def getContributionScores():
	cursor = conn.cursor()
	#con = cursor.execute("SELECT user_id FROM Pictures FULL JOIN Comments ON user_id GROUP BY user_id ORDER BY COUNT(*) DESC LIMIT 10")
	#con = cursor.execute("SELECT users.first_name FROM users WHERE user_id IN (SELECT user_id FROM Pictures GROUP BY user_id ORDER BY COUNT(*) DESC LIMIT 10)")
	con = cursor.execute(\
		"SELECT users.first_name \
			FROM users \
				JOIN Pictures ON pictures.user_id = users.user_id \
					JOIN comments ON comments.user_id = users.user_id \
						GROUP BY users.user_id \
							ORDER BY COUNT(*) DESC LIMIT 10")
	print(con)
	return cursor.fetchall()
@app.route('/useractivity.html', methods=['POST'])	
def viewActivity():
	return render_template('useractivity.html', con=getContributionScores(), base64=base64)

def findFriends(uid):
	cursor = conn.cursor()
	logged = getUserIdFromEmail(flask_login.current_user.id)
	con2 = cursor.execute('SELECT first_name FROM users WHERE user_id <> %s AND user_id IN (SELECT user_id2 FROM Friends WHERE user_id1 IN (SELECT user_id2 AS uid2 FROM Friends WHERE user_id1 = %s))',(logged, uid))
	return cursor.fetchall()
@app.route('/fr.html', methods=['POST'])
def recommendFriends():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('fr.html', user=getUserInfo(uid),  fr=findFriends(uid), base64=base64)

@app.route('/album/<album_id>', methods=['GET'])
def album(album_id):
	return render_template('albumpage.html', photos=getAlbumPhotos(album_id), album=getAlbumFromId(album_id),base64=base64)


@app.route('/picture/<picture_id>', methods=['GET'])
def photoPage(picture_id):
	comment = CommentForm(request.form)
	return render_template('photoPage.html', photo=getPhotoFromId(picture_id), comments = getCommentsFromId(picture_id), base64=base64, form = comment)


@app.route('/populartags', methods=['GET'])
def popularTagsPage():
	results = getMostPopularTags()
	return render_template('populartags.html', results = results)

def getUserInfo(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name, user_id FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getAlbumPhotos(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, p.picture_id, caption FROM Pictures AS p JOIN AlbumContains AS a ON p.picture_id = a.picture_id WHERE a.album_id = '{0}'".format(album_id))
	return cursor.fetchall()

def getPhotosForHomePage():
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption, email FROM Pictures JOIN Users ON Pictures.user_id = Users.user_id")
	return cursor.fetchall()

def getTagsfromPhoto():
	cursor = conn.cursor()
	#cursor.execute("SELECT Tagged.tag FROM Tagged, Pictures WHERE Tagged.picture_id = Pictures.picture_id")
	cursor.execute("SELECT Tagged.tag FROM Tagged JOIN Pictures ON Pictures.picture_id = Tagged.picture_id")
	return cursor.fetchall()

def getAlbumFromId(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, album_name FROM Album WHERE album_id = '{0}'".format(album_id))
	return cursor.fetchone()
def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getNumberOfPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT LAST_INSERT_ID() FROM Pictures")
	return cursor.fetchone()[0]
def getPhotoFromId(picture_id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE picture_id = '{0}'".format(picture_id))
	return cursor.fetchone()

def getCommentsFromId(picture_id):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Comments as c JOIN HasComment AS hc ON c.comment_id = hc.comment_id WHERE hc.picture_id = '{0}'".format(picture_id))
	return cursor.fetchall()
def getAllAlbums():
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, album_name FROM Album")
	return cursor.fetchall()
def getUserAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, album_name FROM Album WHERE user_id='{0}'".format(uid))
	return cursor.fetchall()
def getAllPhotosByTag(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT p.picture_id, p.caption FROM Pictures AS p JOIN Tagged AS t ON p.picture_id = t.picture_id WHERE t.tag = '{0}'".format(tag))
	return cursor.fetchall()

def getMostPopularTags():
	cursor = conn.cursor()
	cursor.execute("SELECT tag, COUNT(*) AS num \
					FROM Tagged \
					GROUP BY tag \
					ORDER BY num DESC \
					LIMIT 10")
	return cursor.fetchall()
def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile",photos=getUsersPhotos(uid),user = getUserInfo(uid),base64=base64)


@app.route('/createalbum', methods=['GET'])
def createAlbumGet():
	return render_template('createAlbum.html')

@app.route('/createalbum', methods=['POST'])
def createAlbumPost():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	album_name=request.form.get('album_name')
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Album (album_name, user_id) VALUES ('{0}', '{1}')".format(album_name, uid))
	conn.commit()

	return render_template('createAlbum.html', message="Album Created!")

@app.route('/albums', methods=['GET'])
def albumsPage():
	albums = getAllAlbums()
	return render_template('albums.html', albums = albums)


@app.route('/deleteAlbum/<album_id>.html', methods = ['POST'])
def deleteAlbum(album_id):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Album WHERE album_id = '{0}'".format(int(album_id)))
	conn.commit()
	return flask.redirect(flask.url_for('hello'))

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':	
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tags = request.form.get('tags')
		album_id = request.form.get('album')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES (%s, %s, %s, %s )''' ,(photo_data,uid, caption, album_id))
		conn.commit()
		tags = tags.split()
		for tag in tags:
			cursor.execute("INSERT IGNORE INTO Tag (tag) VALUES (%s)",(tag))
			conn.commit()
		numPhoto = getNumberOfPhotos()
		print(numPhoto)
		#numphoto = numphoto + 1
		for tag in tags:
			cursor.execute("INSERT IGNORE INTO Tagged (picture_id, tag) VALUES (%s, %s)",(numPhoto, tag))
			conn.commit()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO AlbumContains (album_id, picture_id) VALUES (%s, (SELECT LAST_INSERT_ID()) )''' ,(album_id))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),user=getUserInfo(uid),base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html', albums=getUserAlbums(uid))
#end photo uploading code

@app.route("/comment/<photo_id>", methods=['POST'])
def leaveComment(photo_id):

		cursor = conn.cursor()
		comment = request.form.get('comment')
		print(comment)
		uid = getUserIdFromEmail(flask_login.current_user.id)
		now = datetime.now()
		formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
		if(flask_login.current_user.is_authenticated):
			cursor.execute('''INSERT INTO Comments (user_id, comment_text, created_date) VALUES (%s,%s,%s)''',(uid,comment,formatted_date))
			conn.commit()
		else:
			cursor.execute('''INSERT INTO Comments  (comment_text, created_date) VALUES (%s,%s,%s)''',(comment,formatted_date))
			conn.commit()
		return flask.redirect(flask.url_for('hello'))


#default page
@app.route("/", methods=['GET','POST'])
def hello():
	comment = CommentForm(request.form) #I'm passing this form as an arugment to the html file so that each photo can have a comment input section
	
	return render_template('home.html', message='Welcome to Photoshare',photos=getPhotosForHomePage(), tagONE = getTagsfromPhoto(),base64=base64, form=comment)

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
