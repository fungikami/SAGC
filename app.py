from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
# db = SQLAlchemy(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/users.db'
app.config['SECRET_KEY'] = 'unaclavesecreta'

# Crear modelo de usuario (aquí hay que crear la database con python)
# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), nullable=False, unique=True)
#     password = db.Column(db.String(80), nullable=False) 

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

# Página principal (no requiere iniciar sesión)
@app.route("/")
def home():
    return render_template("home.html")

# Página de inicio (requiere iniciar sesión)
@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')

# Página de inicio de sesión
@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None 
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Credenciales inválidas. Intentalo de nuevo.'
        else:
            session['logged_in'] = True
            flash('Te has conectado.')
            return redirect(url_for('welcome'))
    return render_template("login.html", error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('Te has desconectado.')
    return redirect(url_for('home'))

# Página de registro
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if username == '' or email == '' or password == '':
            flash('Todos los campos son obligatorios.')
            return redirect(url_for('register'))
#         else:
#             new_user = User(username=username, email=email, password=password)
#             db.session.add(new_user)
#             db.session.commit()
#             flash('Te has registrado correctamente.')
#             return redirect(url_for('welcome'))

    return render_template("register.html")

if __name__ == '__main__':
    app.run(debug=True)