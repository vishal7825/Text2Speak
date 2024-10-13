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
    return render_template('text_to_speech.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
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
            return redirect(url_for('home'))
        else:
            
            toaster.show_toast("Alert","Invalid email or password. Please try again.",duration=3)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    session.pop('user_email',None)
    toaster.show_toast("Alert","Logout successfully!!",duration=2)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
 if request.method != 'POST':
  return render_template('register.html')
 else:
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Validate name, email, and password
    if not name or not email or not password or not confirm_password:
        toaster.show_toast("Alert","All fields are required.",duration=3)
        return redirect(url_for('register'))

    if not validate_email(email):
        toaster.show_toast("Alert","Invalid email address.",duration=3)
        return redirect(url_for('register'))

    if password != confirm_password:
        toaster.show_toast("Alert","Passwords do not match. Please try again.",duration=3)
        return redirect(url_for('register'))

    # Hash the password before storing
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Insert user into the database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO regis (username, email, password) VALUES (?, ?, ?)',
                   (name, email, hashed_password))
    conn.commit()
    conn.close()

    toaster.show_toast("Alert","Registration successful! You can now login.",duration=2)
    return redirect(url_for('login'))
    
@app.route('/contact', methods=['GET', 'POST'])
def contact():
  
    if request.method != 'POST':
        return render_template('contact.html')
    else:
        message = request.form['message']
    
    # Validate message
    if not message:
        toaster.show_toast("Alert","Please type some messsage to send.",duration=2)
        return redirect(url_for('contact'))
    else:
        if 'user_id' in session:
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            id=session.get("user_id")
            email=session.get("user_email")
            cursor.execute('INSERT INTO contact (id, email, message) VALUES (?, ?, ?)',
                   (id, email, message))
            conn.commit()
            conn.close()
            toaster.show_toast("Alert","Message sent successfully!!.",duration=2)
        else:
            toaster.show_toast("Alert","You have to login first to send message!!.",duration=2)
            return redirect(url_for('login'))
    return redirect(url_for('text_to_speech'))



@app.route('/about_us')
def about_us():
    return render_template('about_us.html')
    toaster.show_toast("Alert",session['user_id'],duration=3)

@app.route('/text_to_speech')
def text_to_speech():
    return render_template('text_to_speech.html')


def validate_email(email):
    # Simple email validation using regex
    pattern = r'^\S+@\S+\.\S+$'
    return re.match(pattern, email)

from flask import Flask,render_template,request
import pyttsx3
import os

@app.route('/')
def text_to_speech_page():
    return render_template('text_to_speech.html', audio_file=None)

@app.route('/generate', methods=['POST'])
def generate_text_to_speech():
  if 'user_id' in session:
    # Get user input
    text = request.form['text']
    speed = request.form['speed']
    gender = request.form['gender']

    # Generate text-to-speech
    audio_file = f'static/generated_audio_{speed}_{gender}.mp3'
    text_to_speech(text, speed, gender, audio_file)

    return render_template('text_to_speech.html', audio_file=audio_file)
  else:
    toaster.show_toast("Alert","You have to login first to convert audio!!.",duration=2)
    return redirect(url_for('login'))
def text_to_speech(text, speed, gender, filename):
    engine = pyttsx3.init()

    # Set speed
    if speed == 'slow':
        engine.setProperty('rate', 100)
    elif speed == 'medium':
        engine.setProperty('rate', 150)
    elif speed == 'fast':
        engine.setProperty('rate', 200)

    # Set voice gender
    voices = engine.getProperty('voices')
    if gender == 'male':
        engine.setProperty('voice', voices[0].id)  # Male voice
    elif gender == 'female':
        engine.setProperty('voice', voices[1].id)  # Female voice
    
    # Save speech to file
    engine.save_to_file(text, filename)
    engine.runAndWait()
  
    
    
if __name__ == '__main__':
    app.run(debug=True)