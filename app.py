from flask import Flask, render_template, json, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from waitress import serve
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'GorshkovyXolo$897'
app.config['MYSQL_DB'] = 'contatrc_python666'
app.config['MYSQL_HOST'] = 'localhost'
# Intialize MySQL
mysql = MySQL(app)

# Session
app.secret_key = 'mysecretkey'

@app.route('/')
def main():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from users')
    data = cursor.fetchall()
    return render_template('index.html', contacts=data)

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'userlevel' in request.form:
        # Create variables for easy access
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        userlevel = request.form['userlevel']
        hashed_password = generate_password_hash(password)
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE name = %s', (name,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Username must contain only characters and numbers!'
        elif not name or not hashed_password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.callproc('sp_createUser', (name, hashed_password, email, userlevel))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)

    flash('Contacto agregado satisfactoriamente')
    return redirect(url_for('main'))

#@app.route('/')
#def index():
#    return 'Welcome to the index page'

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        # Create variables for easy access
        name = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE name = %s AND password = %s', (name, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            # Redirect to home page
            return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_contact(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = {0}'.format(id))
    conn.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('main'))


if __name__ == '__main__':
    app.run('0.0.0.0',port=5001)
    serve(app)
