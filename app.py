from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
# db = SQLAlchemy(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/users.db'
app.config['SECRET_KEY'] = 'unaclavesecreta'

# Crear modelo de usuario  
# class User(db.Model, UserMixin):
#     __tablename__ = 'user'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), nullable=False, unique=True)
#     email = db.Column(db.String(200))
#    password = db.Column(db.String(80), nullable=False) 

# Decorador de login requerido (para hacer logout hay que estar login)
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Necesitas iniciar sesión primero.')
            return redirect(url_for('login'))
    return wrap

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None 
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Credenciales inválidas. Intentalo de nuevo.'
        else:
            session['logged_in'] = True
            flash('Te has conectado.')
            return redirect(url_for('home'))
    return render_template("login.html", error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('Te has desconectado.')
    return redirect(url_for('welcome'))

@app.route("/register")
def register():
    return render_template("register.html")

if __name__ == '__main__':
    app.run(debug=True)