from flask import Flask, render_template, request, flash, redirect, url_for, send_file,session
from flask_bootstrap import Bootstrap
from gtts import gTTS
import pyttsx3
import os
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash
import re
from win10toast import ToastNotifier


app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'text2speak' 

DB_NAME = 'database.db'
toaster=ToastNotifier()


def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regis (
            id INTEGER  AUTO INCREMENT,
            username TEXT NOT NULL,
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact (
            id INTEGER  AUTO INCREMENT,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_table()
@app.route('/')
def home():
    if 'user_id' in session :
        conn=sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id,email,username from regis ')
        user_data=cursor.fetchall()
   
        return render_template('dashbord.html',user_data=user_data)
        
    else:
        return render_template('admin_login.html')
    
@app.route('/messages')
def messages():
    conn=sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id,email,message from contact DESC')
    user_data=cursor.fetchall()
   
    return render_template('messages.html',user_data=user_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("hello")   
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            toaster.show_toast("Alert","All fields are required.",duration=3)
            return redirect(url_for('login'))

        if not validate_email(email):
            toaster.show_toast("Alert","Invalid email address..",duration=3)
            return redirect(url_for('login'))
    
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM regis WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        
    
        if user and check_password_hash(user[3], password):
            # Login successful, store user info in session
            session['user_id'] = user[0]
            session['user_email'] = user[2]
            toaster.show_toast("Alert","Login successfully!!",duration=2)
            return redirect(url_for('dashbord'))
        else:
            
            toaster.show_toast("Alert","Invalid email or password. Please try again.",duration=3)
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    session.pop('user_email',None)
    toaster.show_toast("Alert","Logout successfully!!",duration=2)
    return redirect(url_for('login'))

@app.route('/dashbord')
def dashbord():
     return redirect(url_for('home'))
     conn=sqlite3.connect('database.db')
     cursor = conn.cursor()
     cursor.execute('SELECT id,username,email from regis')
     user_data=cursor.fetchall()
     for user in user_data:
        id,username,email=user
        print(f"User id:{id},Username:{username},Email:{email}")


def validate_email(email):
    # Simple email validation using regex
    pattern = r'^\S+@\S+\.\S+$'
    return re.match(pattern, email)


    
    
if __name__ == '__main__':
    app.run(debug=True)