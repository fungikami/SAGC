from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from sqlalchemy import ForeignKey, true
from roles import Roles

# Configuracion (aplicación y database)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'unaclavesecreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from models import *

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

# Decorador de logout requerido (para no poder entrar a login una vez ya estás loggeado)
def logout_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            flash('No puedes loggearte una vez estás dentro.') #cambiar mensaje
            return redirect(url_for('productor'))
        else:
            return f(*args, **kwargs)
    return wrap

# Decorador de admin requerido
def admin_only(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'rol_admin' in session and session['rol_admin'] == True:
            return f(*args, **kwargs)
        else:
            flash("Debes ser administrador para ver esa página.")
            return redirect(url_for('productor'))

    return wrap

# Página principal (no requiere iniciar sesión)
@app.route("/")
def home():
    return render_template("home.html")

# Página de inicio de sesión
@app.route("/login", methods=['GET', 'POST'])
@logout_required
def login():
    error = None 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar que los campos estén llenos
        if username != '' and password != '':
            # Verificar que el usuario existe
            user = User.query.filter_by(username=username).first()
            
            if user is not None and user.password == password:
                session['logged_in'] = True
                #session['username'] = username
                flash('Se ha iniciado la sesion correctamente')

                # Agregar configuración administrador
                session['rol_admin'] = False
                if user.rol == Roles.Administrador.name:
                    session['rol_admin'] = True
                return redirect(url_for('productor'))
            else:
                error = 'Credenciales invalidas'
        else:
            error = 'Todos los campos son obligatorios'
            
    return render_template("login.html", error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('rol_admin', default=None)
    session.pop('logged_in', None)
    flash('Se ha cerrado la sesion')
    return redirect(url_for('home'))

# Perfiles de usuarios (requiere iniciar sesión)
@app.route("/perfiles", methods=['GET', 'POST'])
@login_required
@admin_only
def perfiles():
    error=None
    users = User.query.all()

    if request.method == 'POST':
        print(request.form)
        username = request.form['username']
        name = request.form['name']
        surname = request.form['surname']
        #email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']

        # Verificar que los campos estén llenos
        if username == '' or name == '' or surname == '' or password == '' or rol == '':
            error = 'Todos los campos son obligatorios.'
            return render_template("perfiles.html", error=error, users=users)

        # USUARIO
        # Verificar que la longitud del username sea menor a 20
        if len(username) > 20:
            error = 'El nombre de usuario no puede tener mas de 20 caracteres.'
            return render_template("perfiles.html", error=error, users=users)

        # Verificar que el usuario no existe
        usernamedb = User.query.filter_by(username=username).first()
        if usernamedb is not None:
            error = 'El nombre de usuario ya se encuentra en uso.'
            return render_template("perfiles.html", error=error, users=users)

        # CONTRASEÑA
        # Verificar longitud de la contraseña
        if len(password) < 8:
            error = 'La contraseña debe tener al menos 8 caracteres.'
            return render_template("perfiles.html", error=error, users=users)

        if len(password) > 80:
            error = 'La contraseña no puede tener mas de 80 caracteres.'
            return render_template("perfiles.html", error=error, users=users)

        # Verificar que haya al menos una letra mayúscula
        if password.islower():
            error = 'La contraseña debe contener al menos una letra mayúscula.'
            return render_template('perfiles.html', error=error, users=users)
        # Verificar que haya al menos un numero
        if all(not char.isdigit() for char in password):
            error = 'La contraseña debe contener almenos un número.'
            return render_template('perfiles.html', error=error, users=users)
        # Verificar simbolos especiales
        # especialSymbols = ['!', '@', '#', '$', '%', '&', '*', '_', '+', '-', '=', '?'] # por si se necesitan mas
        especialSymbols = ['@','*','.','-']
        if all(not char in especialSymbols for char in password):
            error = 'La contraseña debe contener almenos uno de los siguientes símbolos especiales "@","*",".","-"'
            return render_template('perfiles.html', error=error, users=users)

        # Verificar que el email no existe
        # user = User.query.filter_by(email=email).first()
        # if user is not None:
        #     flash('El email ya está registrado.')
        #     return redirect(url_for('perfiles'))

        if rol != Roles.Administrador.name and rol != Roles.Usuario.name:
            error = 'El rol debe ser Administrador o Usuario.'
            return render_template("perfiles.html", error=error, users=users)

        # Guardar usuario en la base de datos
        try:
            new_user = User(username=username, name=name, surname=surname, password=password, 
                        rol = Roles.Administrador.name if rol == Roles.Administrador.name else Roles.Usuario.name)
            db.session.add(new_user)
            db.session.commit()
            flash('Se ha registrado correctamente.')
            #session['logged_in'] = True
            return redirect(url_for('perfiles'))
        except:
            error = 'No se pudo guardar el usuario en la base de datos'
            return render_template("perfiles.html", error=error, users=users)
    
    # Method GET
    users = User.query.all()
    return render_template("perfiles.html", error=error, users=users)

# Datos del Productor (requiere iniciar sesión)
@app.route('/productor')
@login_required
def productor():


    return render_template('productor.html', admin=session['rol_admin'])

# Datos del Productor (requiere iniciar sesión)
@app.route('/tipo_productor', methods=['GET', 'POST'])
@login_required
def tipo_productor():
    error=None
    type_prod = TypeProductor.query.all()

    if request.method == 'POST':
        print(request.form)
        description = request.form['description']

        # Verificar que los campos estén llenos
        if description == '':
            error = 'Todos los campos son obligatorios.'
            return render_template("tipo_productor.html", error=error, type_prod=type_prod)

        # Verificar que sea unico
        typedb = TypeProductor.query.filter_by(description=description).first()
        if typedb is not None:
            error = 'El tipo de productor ya se encuentra en uso.'
            return render_template("tipo_productor.html", error=error, type_prod=type_prod)

        try:
            new_type = TypeProductor(description=description)
            db.session.add(new_type)
            db.session.commit()
            flash('Se ha registrado correctamente.')
            return redirect(url_for('tipo_productor'))
        except:
            error = 'No se pudo guardar el tipo de productor en la base de datos'
            return render_template("tipo_productor.html", error=error, type_prod=type_prod)

    return render_template('tipo_productor.html', admin=session['rol_admin'], type_prod=type_prod)

# Logger de Eventos (requiere iniciar sesión)
@app.route('/eventos')
@login_required
def eventos():
    return render_template('eventos.html')

@app.route("/prueba")
def prueba():
    return render_template("perfiles2.html")

if __name__ == '__main__':
    app.run(debug=True)