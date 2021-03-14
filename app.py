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


from dotenv import load_dotenv
load_dotenv()
import os
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_USER = os.environ.get("DATABASE_USER")

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
		print(cursor.execute("INSERT INTO Users (email, password, first_name, last_name) VALUES ('{0}', '{1}','{2}','{3}')".format(email, password, first_name, last_name)))
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

def getUserInfo(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()
def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getPhotosForHomePage():
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption, email FROM Pictures JOIN Users ON Pictures.user_id = Users.user_id")
	return cursor.fetchall()

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile",photos=getUsersPhotos(uid),base64=base64)

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption) VALUES (%s, %s, %s )''' ,(photo_data,uid, caption))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code

@app.route("/comment/<photo_id>", methods=['POST'])
def leaveComment(photo_id):
	cursor = conn.cursor()
	comment = request.form.get('comment')
	print(comment)
	uid = getUserIdFromEmail(flask_login.current_user.id)
	now = datetime.now()
	formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
	cursor.execute('''INSERT INTO Comments (user_id, comment_text, created_date) VALUES (%s,%s,%s)''',(uid,comment,formatted_date))
	conn.commit()
	return flask.redirect(flask.url_for('hello'))

#default page
@app.route("/", methods=['GET','POST'])
def hello():
	comment = CommentForm(request.form) #I'm passing this form as an arugment to the html file so that each photo can have a comment input section

	return render_template('home.html', message='Welcome to Photoshare',photos=getPhotosForHomePage(),base64=base64, form=comment)


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
