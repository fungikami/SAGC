from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

# Configuracion (aplicación y database)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'unaclavesecreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Crear modelo de usuario (python db_create_user.py)
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False) 

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}')"

# Decorador de login requerido (para hacer logout hay que estar login)
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Necesitas iniciar sesión primero')
            return redirect(url_for('login'))
    return wrap

# Página principal (no requiere iniciar sesión)
@app.route("/")
def home():
    return render_template("home.html")

# Página de inicio de sesión
@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar que los campos estén llenos
        if username != '' and password != '':
            # Verificar que el usuario existe
            user = User.query.filter_by(username=username).first()
            if user is not None:
                if user.password == password:
                    session['logged_in'] = True
                    #session['username'] = username
                    flash('Te has conectado')
                    return redirect(url_for('portafolio'))
                else:
                    error = 'Contraseña incorrecta'
            else:
                error = 'El usuario no existe'
        else:
            error = 'Todos los campos son obligatorios'
            
    return render_template("login.html", error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('Te has desconectado.')
    return redirect(url_for('home'))

# Portafolio de Proyectos (requiere iniciar sesión)
@app.route('/portafolio')
@login_required
def portafolio():
    return render_template('portafolio.html')

# Página de registro (requiere iniciar sesión)
@app.route("/perfiles", methods=['GET', 'POST'])
@login_required
def perfiles():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if username == '' or email == '' or password == '':
            flash('Todos los campos son obligatorios.')
            return redirect(url_for('perfiles'))

        # Verificar que el usuario no existe
        name = User.query.filter_by(username=username).first()
        if name is not None:
            flash('El nombre de usuario ya está en uso.')
            return redirect(url_for('perfiles'))

        # Verificar que el email no existe
        user = User.query.filter_by(email=email).first()
        if user is not None:
            flash('El email ya está registrado.')
            return redirect(url_for('perfiles'))

        # --------------------------------------
        # Verificar que la contraseña es válida
        # --------------------------------------
        # Verificar que la longitud de la contraseña es válida
        if password.length > 80:
            flash('La contraseña es demasiado larga.')
            return redirect(url_for('perfiles'))
        # Verificar que haya al menos una letra mayúscula
        if not password.islower():
            flash('El password debe contener almenos una letra mayúscula.')
            return redirect(url_for('perfiles'))
        # Verificar que haya al menos un numero
        if any(char.isdigit() for char in password):
            flash('El password debe contener almenos un número.')
            return redirect(url_for('perfiles'))
        # Verificar simbolos especiales
        # especialSymbols = ['!', '@', '#', '$', '%', '&', '*', '_', '+', '-', '=', '?'] # por si se necesitan mas
        especialSymbols = ['@','*','.','-']
        if any(char in especialSymbols for char in password):
            flash('El password debe contener almenos uno de los siguientes símbolos especiales "@","*",".","-"')
            return redirect(url_for('perfiles'))
        
        # Guardar usuario en la base de datos
        else:
            try:
                new_user = User(username=username, email=email, password=password)
                db.session.add(new_user)
                db.session.commit()
                flash('Te has registrado correctamente.')
                session['logged_in'] = True
                return redirect(url_for('portafolio'))
            except:
                return 'Ha ocurrido un error'

    return render_template("perfiles.html")

# Logger de Eventos (requiere iniciar sesión)
@app.route('/eventos')
@login_required
def eventos():
    return render_template('eventos.html')

if __name__ == '__main__':
    app.run(debug=True)