#importing libraries to use
from flask import *
import numpy as np
import pandas as pd
import os
from werkzeug.utils import secure_filename
from datetime import *

app = Flask(__name__)
app.secret_key = 'ab'
###	created flask object
###	set  secret key
###	paths
path_dp = r'static/dp/'
path_db = 'static/db/'
path_style = r'/static/styles'

profile_db = pd.read_csv(path_db + 'profile_db.csv')
blog_db = pd.read_csv(path_db + 'blog_db.csv')

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
@app.route('/signup', methods=['post'])
def signup():
	global profile_db
	name = request.form['name']
	mail = request.form['mail']
	pswd1 = request.form['pswd1']
	pswd2 = request.form['pswd2']
	if pswd1 != pswd2:
		return '''<script>alert('Passwords Not Matching');window.location='/register'</script>'''
	if True in list(profile_db.EMAIL == mail):
		return '''<script>alert('Account Already Exists. Try Logging In');window.location='/register'</script>'''
	new_LID = profile_db.LOGIN_ID.max() + 1
	profile_db = profile_db.append({'LOGIN_ID':new_LID, 'NAME':name, 'EMAIL':mail, 'PASSWORD':pswd1, 'IMAGE':'None', 'TYPE':'user'}, ignore_index=True)
	profile_db.to_csv(path_db + 'profile_db.csv', index=False)
	profile_db = pd.read_csv(path_db + 'profile_db.csv')
	return '''<script>alert('Registeration Successfull. Login To Continue');window.location='/'</script>'''

#admin home page
@app.route('/admin_home')
def admin_home():
	if 'lid' in session:
		joined_df = blog_db.merge(profile_db[['NAME','EMAIL', 'IMAGE', 'LOGIN_ID']], left_on='AUTHOR_ID', right_on='LOGIN_ID').drop('LOGIN_ID', axis=1)
		sort_joined_df = joined_df.sort_values(by='BLOG_ID', ascending=False)
		return render_template('home_admin.html', val = sort_joined_df.to_numpy())
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#view users page
@app.route('/view_users')
def view_users():
	if 'lid' in session:
		user_list = profile_db[profile_db.TYPE == 'user']
		return render_template('view_users.html', val = user_list.to_numpy())
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#delete user function
@app.route('/delete_user')
def delete_user():
	if 'lid' in session:
		global profile_db, blog_db
		user_id = request.args.get('id')
		del_profile_db = profile_db[profile_db.LOGIN_ID != int(user_id)]
		del_blog_db = blog_db[blog_db.AUTHOR_ID != int(user_id)]
		del_profile_db.to_csv(path_db + 'profile_db.csv', index=False)
		del_blog_db.to_csv(path_db + 'blog_db.csv', index=False)
		profile_db = pd.read_csv(path_db + 'profile_db.csv')
		blog_db = pd.read_csv(path_db + 'blog_db.csv')
		return '''<script>alert('User Deleted');window.location='/view_users'</script>'''
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#user home page
@app.route('/user_home')
def user_home():
	if 'lid' in session:
		joined_df = blog_db.merge(profile_db[['NAME','EMAIL', 'IMAGE', 'LOGIN_ID']], left_on='AUTHOR_ID', right_on='LOGIN_ID').drop('LOGIN_ID', axis=1)
		sort_joined_df = joined_df.sort_values(by='BLOG_ID', ascending=False)
		return render_template('home_user.html', val = sort_joined_df.to_numpy())
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#write blog page
@app.route('/write_blog')
def write_blog():
	if 'lid' in session:
		return render_template('write_blog.html')
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#upload blog function
@app.route('/upload_blog', methods=['post'])
def upload_blog():
	if 'lid' in session:
		global blog_db
		title = request.form['title']
		content = request.form['content']
		new_BID = blog_db.BLOG_ID.max() + 1
		blog_db = blog_db.append({'BLOG_ID':new_BID, 'AUTHOR_ID':session['lid'], 'TITLE':title, 'CONTENT':content}, ignore_index=True)
		blog_db.to_csv(path_db + 'blog_db.csv', index=False)
		blog_db = pd.read_csv(path_db + 'blog_db.csv')
		return '''<script>alert('Your Blog has been Uploaded');window.location='/user_home'</script>'''
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#my blogs page
@app.route('/my_blogs')
def my_blogs():
	if 'lid' in session:
		joined_df = blog_db.merge(profile_db[['NAME','EMAIL', 'IMAGE', 'LOGIN_ID']], left_on='AUTHOR_ID', right_on='LOGIN_ID').drop('LOGIN_ID', axis=1)
		sort_joined_df = joined_df.sort_values(by='BLOG_ID', ascending=False)
		filter_sort_joined_df = sort_joined_df[sort_joined_df.AUTHOR_ID == session['lid']]
		return render_template('my_blogs.html', val=filter_sort_joined_df.to_numpy())
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#edit blog page
@app.route('/edit_blog')
def edit_blog():
	if 'lid' in session:
		blog_id = request.args.get('id')
		s = blog_db[blog_db.BLOG_ID == int(blog_id)]
		return render_template('edit_blog.html', val=s.to_numpy()[0])
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#update blog function
@app.route('/update_blog', methods=['post'])
def update_blog():
	if 'lid' in session:
		global blog_db
		blog_id = int(request.args.get('id'))
		title = request.form['title']
		content = request.form['content']
		blog_db.at[blog_db.BLOG_ID == blog_id, 'TITLE'] = title
		blog_db.at[blog_db.BLOG_ID == blog_id, 'CONTENT'] = content
		blog_db.to_csv(path_db + 'blog_db.csv', index=False)
		blog_db = pd.read_csv(path_db + 'blog_db.csv')
		return '''<script>alert('Your Blog has been Updated');window.location='/my_blogs'</script>'''
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#my profile page
@app.route('/my_profile')
def my_profile():
	if 'lid' in session:
		s = profile_db[profile_db.LOGIN_ID == session['lid']]
		return render_template('my_profile.html', val=s.to_numpy()[0])
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#edit profile page
@app.route('/edit_profile')
def edit_profile():
	if 'lid' in session:
		s = profile_db[profile_db.LOGIN_ID == session['lid']]
		return render_template('edit_profile.html', val=s.to_numpy()[0])
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#update profile function
@app.route('/update_profile', methods=['post'])
def update_profile():
	if 'lid' in session:
		global profile_db
		name = request.form['name']
		mail = request.form['mail']
		profile_db.at[session['lid'], 'NAME'] = name
		profile_db.at[session['lid'], 'EMAIL'] = mail
		profile_db.to_csv(path_db + 'profile_db.csv', index=False)
		profile_db = pd.read_csv(path_db + 'profile_db.csv')
		return '''<script>alert('Proile Updated');window.location='/my_profile'</script>'''
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#change dp page
@app.route('/change_dp')
def change_dp():
	if 'lid' in session:
		return render_template('change_dp.html')
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#update dp function
@app.route('/update_dp', methods=['post'])
def update_dp():
	if 'lid' in session:
		global profile_db
		time = datetime.now().strftime('%Y%m%d%H%M%S')
		img = request.files['file']
		img_name = str(session['lid']) + time
		img.save(os.path.join(path_dp, img_name+'.png'))
		img_old = profile_db[profile_db.LOGIN_ID == session['lid']].IMAGE.tolist()[0]
		print(img_old)
		if img_old != 'None':
			os.remove(path_dp + img_old + '.png')
		profile_db.at[session['lid'], 'IMAGE'] = img_name
		profile_db.to_csv(path_db + 'profile_db.csv', index=False)
		profile_db = pd.read_csv(path_db + 'profile_db.csv')
		return '''<script>alert('Updated Profile Picture');window.location='/my_profile'</script>'''
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#delete blog function
@app.route('/delete_blog')
def delete_blog():
	if 'lid' in session:
		global blog_db
		blog_id = request.args.get('id')
		del_blog_db = blog_db[blog_db['BLOG_ID'] != int(blog_id)]
		del_blog_db.to_csv(path_db + 'blog_db.csv', index=False)
		blog_db = pd.read_csv(path_db + 'blog_db.csv')
		return '''<script>alert('Blog Deleted');window.location='/admin_home'</script>'''
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''


#change password page
@app.route('/change_password')
def change_password():
	if 'lid' in session:
		return render_template('change_password.html')
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#change password function
@app.route('/update_password', methods=['post'])
def update_password():
	if 'lid' in session:
		global profile_db
		pswd = request.form['pswd']
		pswd1 = request.form['pswd1']
		pswd2 = request.form['pswd2']
		if pswd1 != pswd2:
			return '''<script>alert('Passwords Not Matching. Try Again');window.location='/change_password'</script>'''
		if profile_db[profile_db.LOGIN_ID==session['lid']].PASSWORD.tolist()[0] != pswd:
			return '''<script>alert('Wrong Password');window.location='/change_password'</script>'''
		profile_db.at[session['lid'], 'PASSWORD'] = pswd1
		profile_db.to_csv(path_db + 'profile_db.csv', index=False)
		profile_db = pd.read_csv(path_db + 'profile_db.csv')
		if session['lid'] == 0:
			return '''<script>alert('Password Successfully Updated');window.location='/admin_home'</script>'''
		return '''<script>alert('Password Successfully Updated');window.location='/user_home'</script>'''
	else:
		return '''<script>alert('Not Allowed');window.location='/'</script>'''

#logout function
@app.route('/logout')
def logout():
	session.clear()
	return '''<script>window.location='/'</script>'''

if __name__ == '__main__':
	app.run(debug=True)
