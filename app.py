from crypt import methods
from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from sqlalchemy import ForeignKey, true
from roles import Roles
from verificadores import verificar_perfil, verificar_tipo_productor

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
            new_user = User(username=username, name=name, surname=surname, password=password, rol=rol)
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
        error = verificar_perfil(request.form, User, user_to_update)
        if error is not None:
            return render_template("perfiles.html", error=error, users=users)  

        user_to_update.username = request.form['username']
        user_to_update.name = request.form['name']
        user_to_update.surname = request.form['surname']
        user_to_update.password = request.form['password']
        user_to_update.rol = request.form['rol']

        try:
            db.session.commit()
            flash('Se ha modificado correctamente.')
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
@app.route('/productor', methods=['GET', 'POST'])
@login_required
def productor():
    tipo_productor = TypeProducer.query.all()
    # productores = session.query(Producer, TypeProducer)\
    #                 .join(TypeProducer, TypeProducer.id == Producer.type_producer)

    # productores = session.query(Producer, TypeProducer).filter(Producer.type_producer == TypeProducer.id)

    productores = Producer.query.all()

    if request.method == 'POST':
        print(request.form)
        ci = request.form['cedula']
        name = request.form['name']
        surname = request.form['surname']
        telephone = request.form['telephone']
        phone = request.form['phone']
        dir1 = request.form['direction1']
        dir2 = request.form['direction2']
        rol = request.form['rol']                   # Esto es un número id que indica el TypeProducer
        list = [ci, name, surname, telephone, phone, rol]
        # Verificar que los campos estén llenos
        if not any(list):
            error = 'Todos los campos son obligatorios.'
            return render_template("productor.html", error=error, tipos=tipo_productor)

        # USUARIO
        # Verificar que la longitud del username sea menor a 20
        if len(name) > 20:
            error = 'El nombre no puede tener mas de 20 caracteres.'
            return render_template("productor.html", error=error, tipos=tipo_productor)

        # Verificar que la cedula no exista
        ci_db = Producer.query.filter_by(ci=ci).first()
        if ci_db is not None:
            error = 'El nombre ya se encuentra en uso.'
            return render_template("productor.html", error=error, tipos=tipo_productor)

        # Guardar usuario en la base de datos
        try:
            type_prod = TypeProducer.query.filter_by(id=rol).first()
            new_prod = Producer(ci=ci, name=name, surname=surname, telephone=telephone, phone=phone,
                        type_prod=type_prod, direction1=dir1, direction2=dir2)
            print(new_prod)
            db.session.add(new_prod)
            db.session.commit()
            flash('Se ha registrado correctamente.')
            #session['logged_in'] = True
            return redirect(url_for('productor'))
        except:
            error = 'No se pudo guardar el usuario en la base de datos'
            return render_template("productor.html", error=error, productor=productores, tipos=tipo_productor)

    return render_template('productor.html', admin=session['rol_admin'], productor=productores, tipos=tipo_productor)

# Borrar datos de /productor
@app.route('/delete_productor/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_productor(id):
    prod_to_delete = Producer.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(prod_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('productor'))
        except:
            return "Hubo un error eliminando el tipo de productor."
    return render_template('productor.html')


# Tipos de Productor (requiere iniciar sesión)
@app.route('/tipo_productor', methods=['GET', 'POST'])
@login_required
def tipo_productor():
    error=None
    type_prod = TypeProducer.query.all()

    if request.method == 'POST':
        # Verificar los campos del tipo de productor
        error = verificar_tipo_productor(request.form, TypeProducer)
        if error is not None:
            return render_template("tipo_productor.html", error=error, admin=session['rol_admin'], type_prod=type_prod)

        # Registra el tipo de productor en la base de datos
        try:
            description = request.form['description']
            new_type = TypeProducer(description=description)
            db.session.add(new_type)
            db.session.commit()
            flash('Se ha registrado correctamente.')
            return redirect(url_for('tipo_productor'))
        except:
            error = 'No se pudo guardar el tipo de productor en la base de datos'
            return render_template("tipo_productor.html", error=error, admin=session['rol_admin'], type_prod=type_prod)

    return render_template('tipo_productor.html', admin=session['rol_admin'], type_prod=type_prod)

# Actualizar datos de /tipo_productor
@app.route('/update_tipo_productor/<int:id>', methods=['GET', 'POST'])
@login_required
def update_tipo_productor(id):
    error=None
    type_prod = TypeProducer.query.all()
    type_to_update = TypeProducer.query.get_or_404(id)

    if request.method == "POST":
        # Verificar los campos del tipo de productor
        error = verificar_tipo_productor(request.form, TypeProducer)
        if error is not None:
            return render_template("tipo_productor.html", error=error, admin=session['rol_admin'], type_prod=type_prod)

        # Modificar los datos del tipo de productor
        try:
            type_to_update.description = request.form['description']
            db.session.commit()
            return redirect(url_for('tipo_productor'))
        except:
            error = 'No se pudo actualizar el tipo de productor.'
            return render_template('tipo_productor.html')
    
    return render_template('tipo_productor.html')

# Borrar datos de /tipo_productor
@app.route('/delete_tipo_productor/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_tipo_productor(id):
    type_to_delete = TypeProducer.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(type_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('tipo_productor'))
        except:
            return "Hubo un error eliminando el tipo de productor."
    return render_template('tipo_productor.html')
# Search Bar Perfiles
@app.route('/search_perfil/', methods=['GET', 'POST'])
@login_required
def search_perfil():
    error = None
    users = []
    
    if request.method == "POST":
        if 'search_perfil' in request.form:
            form = request.form
            usuario = User.query.filter_by(username=form['search_perfil'])
            nombre = User.query.filter_by(name=form['search_perfil'])
            apellido = User.query.filter_by(surname=form['search_perfil'])

            users = usuario.union(nombre, apellido)
    return render_template("/search_perfil.html", error=error, users=users)

# Search Bar Tipo Productor (da proxy error)
@app.route('/search_tipoproductor/', methods=['GET', 'POST'])
@login_required
def search_tipoprod():
    type_prod = []
    
    if request.method == "POST":
        if 'search_tipoproductor' in request.form:
            form = request.form
            type_prod = TypeProducer.query.filter_by(description=form['search_tipoproductor'])

    return render_template("/search_tipoproductor.html", type_prod=type_prod)

# Search Bar Productor (TO DO)
@app.route('/search_productor/', methods=['GET', 'POST'])
@login_required
def search_prod():
    error = None
    prod = []
    
    if request.method == "POST":
        if 'search_productor' in request.form:
            form = request.form
            prod = Producer.query.filter_by(TODO=form['search_productor'])

    return render_template("/search_productor.html", error=error, prod=prod)

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