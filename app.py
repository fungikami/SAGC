from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from sqlalchemy import ForeignKey, true
from roles import Roles
from verificadores import verificar_perfil

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
        error = verificar_perfil(request.form, User)
        if error is not None:
            return render_template("perfiles.html", error=error, users=users) 

        username = request.form['username']
        name = request.form['name']
        surname = request.form['surname']
        password = request.form['password']
        rol = request.form['rol']

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
    return render_template("perfiles.html", error=error, users=users)


# Actualizar datos de /Perfiles
@app.route('/updateperfil/<int:id>', methods=['GET', 'POST'])
@login_required
def update_perfiles(id):
    error=None
    users = User.query.all()
    user_to_update = User.query.get_or_404(id)
    
    if request.method == "POST":
        error = verificar_perfil(request.form, User)
        if error is not None:
            return render_template("perfiles.html", error=error, users=users)  

        user_to_update.username = request.form['username']
        user_to_update.name = request.form['name']
        user_to_update.surname = request.form['surname']
        user_to_update.password = request.form['password']
        user_to_update.rol = request.form['rol']

        try:
            db.session.commit()
            return redirect(url_for('perfiles'))
        except:
            error = 'No se pudo actualizar al usuario.'
            return render_template("perfiles.html", error=error, users=users)  
    
    return render_template("perfiles.html", error=error, users=users)

# Borrar datos de /Perfiles
@app.route('/deleteperfil/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_perfiles(id):
    user_to_delete = User.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('perfiles'))
        except:
            return "Hubo un error borrando al usuario."

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
            return render_template("tipo_productor.html", error=error, admin=session['rol_admin'], type_prod=type_prod)

        # Verificar que sea unico
        typedb = TypeProductor.query.filter_by(description=description).first()
        if typedb is not None:
            error = 'El tipo de productor ya se encuentra en uso.'
            return render_template("tipo_productor.html", error=error, admin=session['rol_admin'], type_prod=type_prod)

        try:
            new_type = TypeProductor(description=description)
            db.session.add(new_type)
            db.session.commit()
            flash('Se ha registrado correctamente.')
            return redirect(url_for('tipo_productor'))
        except:
            error = 'No se pudo guardar el tipo de productor en la base de datos'
            return render_template("tipo_productor.html", error=error, admin=session['rol_admin'], type_prod=type_prod)

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