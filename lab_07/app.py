from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Replace with your secret key

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not (re.search('[a-z]', password) and
                re.search('[A-Z]', password) and
                re.search('[0-9]$', password) and
                len(password) >= 8):
            flash('Password must contain at least 8 characters with lowercase, uppercase, and end with a number', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('signup'))

        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return render_template('thankyou.html')

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and password:
            session['user'] = user.id 
            return redirect(url_for('secret_page'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('signin'))

    return render_template('signin.html')

@app.route('/secret')
def secret_page():

    if 'user' in session:
        user_id = session['user']
        user = User.query.get(user_id)
        return render_template('secretPage.html', user=user)
    else:
        flash('You must be logged in to view this page', 'error')
        return redirect(url_for('signin'))

@app.route('/logout')
def logout():
    session.pop('user', None)  
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
