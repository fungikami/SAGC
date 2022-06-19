from crypt import methods
from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from sqlalchemy import ForeignKey, true
from roles import Roles
from verificadores import verificar_perfil, verificar_tipo_productor, verificar_productor

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
            flash("Debes ser administrador para ver 'Perfiles de Usuarios'.")
            return redirect(url_for('productor'))

    return wrap

def analyst_only(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'rol_analyst' in session and session['rol_analyst'] == True:
            return f(*args, **kwargs)
        else:
            flash("Debes ser Analista de Ventas para acceder 'Datos del Productor y Tipos de Productor'.")
            return redirect(url_for('perfiles'))

    return wrap

#----------------------------------------------------------------------------------------------------------------------
# Página principal (no requiere iniciar sesión)
@app.route("/")
def home():
    return render_template("home.html")

#----------------------------------------------------------------------------------------------------------------------
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

                # Agregar configuración administrador y analista
                session['rol_admin'] = False
                session['rol_analyst'] = False
                if user.rols.name == "Administrador":
                    session['rol_admin'] = True
                    return redirect(url_for('perfiles'))

                if user.rols.name == "Analista de Ventas":
                    session['rol_analyst'] = True
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

#----------------------------------------------------------------------------------------------------------------------
# Perfiles de usuarios (requiere iniciar sesión)
@app.route("/perfiles", methods=['GET', 'POST'])
@login_required
@admin_only
def perfiles():
    error=None
    users = User.query.all()
    rols = Rol.query.all()

    if request.method == 'POST':
        error = verificar_perfil(request.form, User)
        if error is not None:
            return render_template("perfiles.html", error=error, users=users, rols=rols) 

        username = request.form['username']
        name = request.form['name']
        surname = request.form['surname']
        password = request.form['password']
        rol = request.form['rol']
        cosecha = request.form['cosecha']

        # Guardar usuario en la base de datos
        try:
            new_user = User(username=username, name=name, surname=surname, password=password, rol=rol)
            db.session.add(new_user)
            if cosecha != '':
                tmp = Cosecha.query.filter_by(date=cosecha).first()
                new_user.cosechas.append(tmp if tmp != None else Cosecha(date=cosecha))
            db.session.commit()
            flash('Se ha registrado correctamente.')
            #session['logged_in'] = True
            return redirect(url_for('perfiles'))
        except:
            error = 'No se pudo guardar el usuario en la base de datos'
            return render_template("perfiles.html", error=error, users=users, rols=rols)
    
    # Method GET
    return render_template("perfiles.html", error=error, users=users, rols=rols)


# Actualizar datos de /Perfiles
@app.route('/updateperfil/<int:id>', methods=['GET', 'POST'])
@login_required
def update_perfiles(id):
    error=None
    users = User.query.all()
    rols = Rol.query.all()
    user_to_update = User.query.get_or_404(id)
    
    if request.method == "POST":
        error = verificar_perfil(request.form, User, user_to_update)
        if error is not None:
            return render_template("perfiles.html", error=error, users=users, rols=rols)  

        user_to_update.username = request.form['username']
        user_to_update.name = request.form['name']
        user_to_update.surname = request.form['surname']
        user_to_update.password = request.form['password']
        user_to_update.rol = request.form['rol']
        cosecha = request.form['cosecha']
        if cosecha != '' and cosecha.lower() != 'ninguna':
            tmp = Cosecha.query.filter_by(date=cosecha).first()
            user_to_update.cosechas.append(tmp if tmp != None else Cosecha(date=cosecha))

        try:
            db.session.commit()
            flash('Se ha modificado correctamente.')
            return redirect(url_for('perfiles'))
        except:
            error = 'No se pudo actualizar al usuario.'
            return render_template("perfiles.html", error=error, users=users, rols=rols)  
    
    return render_template("perfiles.html", error=error, users=users, rols=rols)

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

#----------------------------------------------------------------------------------------------------------------------
# Datos del Productor (requiere iniciar sesión)
@app.route('/productor', methods=['GET', 'POST'])
@login_required
@analyst_only
def productor():
    error=None
    tipo_productor = TypeProducer.query.all()
    productores = Producer.query.all()

    if request.method == 'POST':
        # Verifica los campos del registro de Productor
        error = verificar_productor(request.form, Producer)
        if error is not None:
            return render_template("productor.html", error=error, admin=session['rol_admin'], tipo_productor=tipo_productor, productor=productores)
            
        # Guardar usuario en la base de datos
        try:
            ci = request.form['cedula']
            name = request.form['name']
            surname = request.form['surname']
            telephone = request.form['telephone']
            phone = request.form['phone']
            dir1 = request.form['direction1']
            dir2 = request.form['direction2']
            rol = request.form['rol']     # Esto es un número id que indica el TypeProducer  

            type_prod = TypeProducer.query.filter_by(id=rol).first()
            new_prod = Producer(ci=ci, name=name, surname=surname, telephone=telephone, phone=phone,
                        type_producer=type_prod, direction1=dir1, direction2=dir2)
            
            db.session.add(new_prod)
            db.session.commit()
            flash('Se ha registrado correctamente.')
            #session['logged_in'] = True
            return redirect(url_for('productor'))
        except:
            error = 'No se pudo guardar el usuario en la base de datos'

    return render_template('productor.html', error=error, admin=session['rol_admin'], productor=productores, type_prod=tipo_productor)

# Actualizar datos de /productor
@app.route('/update_productor/<int:id>', methods=['GET', 'POST'])
@login_required
def update_productor(id):
    error=None
    type_prod = TypeProducer.query.all()
    productores = Producer.query.all()
    prod_to_update = Producer.query.get_or_404(id)

    if request.method == "POST":
        # Verifica los campos del registro de Productor
        error = verificar_productor(request.form, Producer, prod_to_update)
        if error is not None:
            return render_template("productor.html", error=error, admin=session['rol_admin'], productor=productores, type_prod=type_prod)     
        
        # Modificar los datos del tipo de productor
        try:
            prod_to_update.ci = request.form['cedula']
            prod_to_update.name = request.form['name']
            prod_to_update.surname = request.form['surname']
            prod_to_update.telephone = request.form['telephone']
            prod_to_update.phone = request.form['phone']
            prod_to_update.direction1 = request.form['direction1']
            prod_to_update.direction2 = request.form['direction2']
            prod_to_update.type_prod = request.form['rol']            
            db.session.commit()
            flash('Se ha modificado correctamente.')
            return redirect(url_for('productor'))
        except:
            error = 'No se pudo actualizar el productor.'
    
    return render_template('productor.html', error=error, admin=session['rol_admin'], productor=productores, type_prod=type_prod)

# Borrar datos de /productor
@app.route('/delete_productor/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_productor(id):
    error=None
    type_prod = TypeProducer.query.all()
    productores = Producer.query.all()
    prod_to_delete = Producer.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(prod_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('productor'))
        except:
            error = "Hubo un error eliminando el productor."

    return render_template('productor.html', error=error, admin=session['rol_admin'], productor=productores, type_prod=type_prod)

#----------------------------------------------------------------------------------------------------------------------------
# Tipos de Productor (requiere iniciar sesión)
@app.route('/tipo_productor', methods=['GET', 'POST'])
@login_required
@analyst_only
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
            flash('Se ha modificado correctamente.')
            return redirect(url_for('tipo_productor'))
        except:
            error = 'No se pudo actualizar el tipo de productor.'
    
    return render_template("tipo_productor.html", error=error, admin=session['rol_admin'], type_prod=type_prod)

# Borrar datos de /tipo_productor
@app.route('/delete_tipo_productor/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_tipo_productor(id):
    error=None
    type_prod = TypeProducer.query.all()
    type_to_delete = TypeProducer.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(type_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('tipo_productor'))
        except:
            return "Hubo un error eliminando el tipo de productor."

    return render_template("tipo_productor.html", error=error, admin=session['rol_admin'], type_prod=type_prod)

# Search Bar Perfiles
@app.route('/search_perfil/', methods=['GET', 'POST'])
@login_required
def search_perfil():
    error = None
    users = []
    rols = Rol.query.all()
    
    if request.method == "POST":
        palabra = request.form['search_perfil']
        usuario = User.query.filter(User.username.like('%' + palabra + '%'))
        nombre = User.query.filter(User.name.like('%' + palabra + '%'))
        apellido = User.query.filter(User.surname.like('%' + palabra + '%'))

        users = usuario.union(nombre, apellido)

    return render_template("perfiles.html", error=error, users=users, rols=rols)

# Search Bar Tipo Productor
@app.route('/search_tipo_productor', methods=['GET', 'POST'])
@login_required
def search_tipo_productor():
    type_prod = []

    if request.method == "POST":
        palabra = request.form['search_tipo_productor']
        type_prod = TypeProducer.query.filter(TypeProducer.description.like('%' + palabra + '%'))
        
    return render_template("/tipo_productor.html", admin=session['rol_admin'], type_prod=type_prod)

# Search Bar Productor
@app.route('/search_productor', methods=['GET', 'POST'])
@login_required
def search_productor():
    error = None
    productores = []
    
    if request.method == "POST":
        palabra = request.form['search_productor']
            
        cedula = Producer.query.filter(Producer.ci.like('%' + palabra + '%'))
        nombre = Producer.query.filter(Producer.name.like('%' + palabra + '%'))
        apellido = Producer.query.filter(Producer.surname.like('%' + palabra + '%'))
        telefono = Producer.query.filter(Producer.telephone.like('%' + palabra + '%'))
        direc1 = Producer.query.filter(Producer.direction1.like('%' + palabra + '%'))
        direc2 = Producer.query.filter(Producer.direction2.like('%' + palabra + '%'))
        tipo = Producer.query.filter(Producer.type_prod.like('%' + palabra + '%'))

        productores = cedula.union(nombre, apellido, telefono, direc1, direc2, tipo)

    type_prod = TypeProducer.query.all()
    return render_template('productor.html', error=error, admin=session['rol_admin'], productor=productores, type_prod=type_prod)

#----------------------------------------------------------------------------------------------------------------------
# Logger de Eventos (requiere iniciar sesión)
@app.route('/eventos')
@login_required
def eventos():
    return render_template('eventos.html')

#----------------------------------------------------------------------------------------------------------------------
@app.route("/prueba")
def prueba():
    return render_template("perfiles2.html")

if __name__ == '__main__':
    app.run(debug=True)