from flask import *
import numpy as np
import pandas as pd

app = Flask(__name__)

@app.route('/')
def main():
	return render_template('login.html')

@app.route('/register')
def register():
	return render_template('register.html')

if __name__ == '__main__':
	app.run(debug=True)
