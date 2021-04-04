from flask import *
import numpy as np
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ab'

path_dp = r'/static/dp'
path_db = 'static/db/'
path_style = r'/static/styles'

# global profile_db, blog_dp
profile_db = pd.read_csv(path_db + 'profile_db.csv')
profile_db.where(profile_db.isna(), profile_db.astype(str))
blog_db = pd.read_csv(path_db + 'blog_db.csv')
blog_db.where(blog_db.isna(), blog_db.astype(str))

#login page
@app.route('/')
def main():
	return render_template('login.html')

#login function
@app.route('/login', methods=['post'])
def login():
	mail = request.form['mail']
	password = request.form['pswd']
	profile = profile_db[profile_db.EMAIL==mail][profile_db[profile_db.EMAIL==mail].PASSWORD==password]
	if profile.empty:
		return '''<script>alert('Invalid Login Details');window.location='/'</script>'''
	if str(profile['TYPE'].tolist()[0]) == 'admin':
		session['lid'] = profile['LOGIN_ID'].tolist()[0]
		return '''<script>alert('Loging In');window.location='/admin_home'</script>'''
	elif str(profile['TYPE'].tolist()[0]) == 'user':
		session['lid'] = profile['LOGIN_ID'].tolist()[0]
		return '''<script>alert('Loging In');window.location='/user_home'</script>'''
	else:
		return '''<script>alert('Invalid Login Details');window.location='/'</script>'''

#register page
@app.route('/register')
def register():
	return render_template('register.html')

#signup function
@app.route('/signup')
def signup():
	name = request.form['name']
	mail = request.form['mail']
	pswd1 = request.form['pswd1']
	pswd2 = request.form['pswd2']
	return '''<script>alert('Registeration Successfull');window.location='/'</script>'''

#admin home page
@app.route('/admin_home')
def admin_home():
	if 'lid' in session:
		return render_template('home_admin.html')
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#user home page
@app.route('/user_home')
def user_home():
	if 'lid' in session:
		return render_template('home_user.html')
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

if __name__ == '__main__':
	app.run(debug=True)
