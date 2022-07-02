from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from verificadores import *
import datetime

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
            if (session['rol_admin']):
                return redirect(url_for('perfiles'))
            return redirect(url_for('productor'))
        else:
            return f(*args, **kwargs)
    return wrap

# Decorador de Administrador requerido
def admin_only(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'rol_admin' in session and session['rol_admin'] == True:
            return f(*args, **kwargs)
        else:
            flash("Debes ser administrador para ver 'Perfiles de Usuarios'.")
            return redirect(url_for('productor'))

    return wrap

# Decorador de Analista de Ventas requerido
def analyst_only(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'rol_analyst' in session and session['rol_analyst'] == True:
            return f(*args, **kwargs)
        else:
            flash("Debes ser Analista de Ventas para acceder 'Datos del Recolector y Tipos de Recolector'.")
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
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']

        if nombre_usuario != '' and password != '':
            user = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
            
            if user is not None and (check_password_hash(user.password, password) or password == user.password):
                session['logged_in'] = True
                flash('Se ha iniciado la sesion exitosamente')

                # Agregar configuración administrador y analista
                session['rol_admin'] = False
                session['rol_analyst'] = False
                if user.rols.nombre == "Administrador":
                    session['rol_admin'] = True
                    return redirect(url_for('perfiles'))

                if user.rols.nombre == "Analista de Ventas":
                    session['rol_analyst'] = True
                    return redirect(url_for('productor')) 
            else:
                error = 'Credenciales invalidas'
        else:
            error = 'Todos los campos son obligatorios'
            
    return render_template("login.html", error=error)

# Cambiar contraseña
@app.route('/login/update_password/', methods=['GET', 'POST'])
@logout_required
def update_password():
    error = None 
    if request.method == 'POST':

        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        new_password = request.form['npassword']

        if nombre_usuario != '' and password != '':
            user = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
            
            if user is not None and (check_password_hash(user.password, password) or password == user.password):
                userID = user.id
                user_to_update = Usuario.query.get_or_404(userID)

                error = verificar_contrasena(new_password)
                if error is not None:
                    return render_template("update_password.html", error=error)  

                user_to_update.password = generate_password_hash(new_password, "sha256")

                try:
                    db.session.commit()
                    flash('La contraseña se ha modificado exitosamente.')
                    return redirect(url_for('login'))
                except:
                    error = 'No se pudo modificar la contraseña.'
                    return render_template("update_password.html", error=error)     
            else:
                error = 'Credenciales invalidas'
        else:
            error = 'Todos los campos son obligatorios'
            
    return render_template("update_password.html", error=error)

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
    usuarios = Usuario.query.all()
    cosechas = Cosecha.query.all()
    rols = Rol.query.all()

    if request.method == 'POST':
        error = verificar_perfil(request.form, Usuario)
        if error is not None:
            return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols, cosechas=cosechas) 

        nombre_usuario = request.form['nombre_usuario']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        password = generate_password_hash(request.form['password'], "sha256")
        rol = request.form['rol']
        cosecha = request.form['cosecha']

        try:
            new_user = Usuario(nombre_usuario=nombre_usuario, nombre=nombre, apellido=apellido, password=password, rol=rol)
            db.session.add(new_user)
            if cosecha != '':
                tmp = Cosecha.query.filter_by(id = cosecha).first()
                new_user.cosechas.append(tmp)
            db.session.commit()
            flash('Se ha registrado exitosamente.')
            return redirect(url_for('perfiles'))
        except:
            error = 'No se pudo guardar el usuario en la base de datos'
            return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols, cosechas=cosechas) 
    
    return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols, cosechas=cosechas) 


# Actualizar datos de /Perfiles
@app.route('/perfiles/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_perfiles(id):
    error=None
    usuarios = Usuario.query.all()
    rols = Rol.query.all()
    user_to_update = Usuario.query.get_or_404(id)
    
    if request.method == "POST":
        error = verificar_perfil(request.form, Usuario, user_to_update)
        if error is not None:
            return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols)  

        user_to_update.nombre_usuario = request.form['nombre_usuario']
        user_to_update.nombre = request.form['nombre']
        user_to_update.apellido = request.form['apellido']
        user_to_update.rol = request.form['rol']
        cosecha = request.form['cosecha']
        if cosecha != '' and cosecha.lower() != 'ninguna':
            tmp = Cosecha.query.filter_by(id = cosecha).first()
            user_to_update.cosechas.append(tmp)

        try:
            db.session.commit()
            flash('Se ha modificado exitosamente.')
            return redirect(url_for('perfiles'))
        except:
            error = 'No se pudo actualizar al usuario.'
            return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols)  
    
    return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols)

# Borrar datos de /Perfiles
@app.route('/perfiles/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_perfiles(id):
    user_to_delete = Usuario.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('perfiles'))
        except:
            return "Hubo un error borrando al usuario."

#----------------------------------------------------------------------------------------------------------------------
# Datos del Recolector (requiere iniciar sesión)
@app.route('/recolector', methods=['GET', 'POST'])
@login_required
@analyst_only
def productor():
    error=None
    tipo_recolector = TipoRecolector.query.all()
    productores = Recolector.query.all()

    if request.method == 'POST':
        # Verifica los campos del registro de Recolector
        error = verificar_productor(request.form, Recolector)
        if error is not None:
            return render_template("recolector.html", error=error, admin=session['rol_admin'], tipo_prod=tipo_recolector, productor=productores)
            
        # Guardar usuario en la base de datos
        try:
            ci = request.form['cedula']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            telefono = request.form['telefono']
            celular = request.form['celular']
            dir1 = request.form['direccion1']
            dir2 = request.form['direccion2']
            rol = request.form['rol']     

            tipo_prod = TipoRecolector.query.filter_by(id=rol).first()
            new_prod = Recolector(ci=ci, nombre=nombre, apellido=apellido, telefono=telefono, celular=celular,
                        tipo_recolector=tipo_prod, direccion1=dir1, direccion2=dir2)
            
            db.session.add(new_prod)
            db.session.commit()
            flash('Se ha registrado exitosamente.')
            return redirect(url_for('productor'))
        except:
            error = 'No se pudo guardar el usuario en la base de datos'

    return render_template('recolector.html', error=error, admin=session['rol_admin'], productor=productores, tipo_prod=tipo_recolector)

# Actualizar datos de /recolector
@app.route('/recolector/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_productor(id):
    error=None
    tipo_prod = TipoRecolector.query.all()
    productores = Recolector.query.all()
    prod_to_update = Recolector.query.get_or_404(id)

    if request.method == "POST":
        # Verifica los campos del registro de Recolector
        error = verificar_productor(request.form, Recolector, prod_to_update)
        if error is not None:
            return render_template("recolector.html", error=error, admin=session['rol_admin'], productor=productores, tipo_prod=tipo_prod)     
        
        # Modificar los datos del tipo de productor
        try:
            prod_to_update.ci = request.form['cedula']
            prod_to_update.nombre = request.form['nombre']
            prod_to_update.apellido = request.form['apellido']
            prod_to_update.telefono = request.form['telefono']
            prod_to_update.celular = request.form['celular']
            prod_to_update.direccion1 = request.form['direccion1']
            prod_to_update.direccion2 = request.form['direccion2']
            prod_to_update.tipo_prod = request.form['rol']            
            db.session.commit()
            flash('Se ha modificado exitosamente.')
            return redirect(url_for('productor'))
        except:
            error = 'No se pudo actualizar el productor.'
    
    return render_template('recolector.html', error=error, admin=session['rol_admin'], productor=productores, tipo_prod=tipo_prod)

# Borrar datos de /recolector
@app.route('/recolector/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_productor(id):
    error=None
    tipo_prod = TipoRecolector.query.all()
    productores = Recolector.query.all()
    prod_to_delete = Recolector.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(prod_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('productor'))
        except:
            error = "Hubo un error eliminando el productor."

    return render_template('recolector.html', error=error, admin=session['rol_admin'], productor=productores, tipo_prod=tipo_prod)

#----------------------------------------------------------------------------------------------------------------------------
# Tipos de Recolector (requiere iniciar sesión)
@app.route('/tipo_recolector', methods=['GET', 'POST'])
@login_required
@analyst_only
def tipo_recolector():
    error=None
    tipo_prod = TipoRecolector.query.all()

    if request.method == 'POST':
        # Verificar los campos del tipo de productor
        error = verificar_tipo_productor(request.form, TipoRecolector)
        if error is not None:
            return render_template("tipo_recolector.html", error=error, admin=session['rol_admin'], tipo_prod=tipo_prod)

        # Registra el tipo de productor en la base de datos
        try:
            descripcion = request.form['descripcion']
            precio = request.form['precio']
            new_type = TipoRecolector(descripcion=descripcion, precio=precio)
            db.session.add(new_type)
            db.session.commit()
            flash('Se ha registrado exitosamente.')
            return redirect(url_for('tipo_recolector'))
        except:
            error = 'No se pudo guardar el tipo de productor en la base de datos'
            
    return render_template("tipo_recolector.html", error=error, admin=session['rol_admin'], tipo_prod=tipo_prod)

# Actualizar datos de /tipo_recolector
@app.route('/tipo_recolector/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_tipo_productor(id):
    error=None
    tipo_prod = TipoRecolector.query.all()
    type_to_update = TipoRecolector.query.get_or_404(id)

    if request.method == "POST":
        # Verificar los campos del tipo de productor
        error = verificar_tipo_productor(request.form, TipoRecolector, type_to_update)
        if error is not None:
            return render_template("tipo_recolector.html", error=error, admin=session['rol_admin'], tipo_prod=tipo_prod)

        # Modificar los datos del tipo de productor
        try:
            type_to_update.descripcion = request.form['descripcion']
            type_to_update.precio = request.form['precio']
            db.session.commit()
            flash('Se ha modificado exitosamente.')
            return redirect(url_for('tipo_recolector'))
        except:
            error = 'No se pudo actualizar el tipo de productor.'
    
    return render_template("tipo_recolector.html", error=error, admin=session['rol_admin'], tipo_prod=tipo_prod)

# Borrar datos de /tipo_recolector
@app.route('/tipo_recolector/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_tipo_productor(id):
    error=None
    tipo_prod = TipoRecolector.query.all()
    type_to_delete = TipoRecolector.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(type_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('tipo_recolector'))
        except:
            return "Hubo un error eliminando el tipo de productor."

    return render_template("tipo_recolector.html", error=error, admin=session['rol_admin'], tipo_prod=tipo_prod)

# Search Bar Perfiles
@app.route('/perfiles/search', methods=['GET', 'POST'])
@login_required
def search_perfil():
    error = None
    usuarios = []
    rols = Rol.query.all()
    
    if request.method == "POST":
        palabra = request.form['search_perfil']

        usuario = Usuario.query.filter(Usuario.nombre_usuario.like('%' + palabra + '%'))
        nombre = Usuario.query.filter(Usuario.nombre.like('%' + palabra + '%'))
        apellido = Usuario.query.filter(Usuario.apellido.like('%' + palabra + '%'))
        tmp = Rol.query.filter(Rol.nombre.like('%' + palabra + '%')).first()
        if tmp != None:
            rol = Usuario.query.filter(Usuario.rol.like('%' + str(tmp.id) + '%'))
            usuarios = usuario.union(nombre, apellido, rol)
        else:
            usuarios = usuario.union(nombre, apellido)

    return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols)

# Search Bar Tipo Recolector
@app.route('/tipo_recolector/search', methods=['GET', 'POST'])
@login_required
def search_tipo_productor():
    tipo_prod = []

    if request.method == "POST":
        palabra = request.form['search_tipo_productor']
        tipo_prod = TipoRecolector.query.filter(TipoRecolector.descripcion.like('%' + palabra + '%'))
        
    return render_template("/tipo_recolector.html", admin=session['rol_admin'], tipo_prod=tipo_prod)

# Search Bar Recolector
@app.route('/recolector/search', methods=['GET', 'POST'])
@login_required
def search_productor():
    error = None
    productores = []
    
    if request.method == "POST":
        palabra = request.form['search_productor']
            
        cedula = Recolector.query.filter(Recolector.ci.like('%' + palabra + '%'))
        nombre = Recolector.query.filter(Recolector.nombre.like('%' + palabra + '%'))
        apellido = Recolector.query.filter(Recolector.apellido.like('%' + palabra + '%'))
        telefono = Recolector.query.filter(Recolector.telefono.like('%' + palabra + '%'))
        direc1 = Recolector.query.filter(Recolector.direccion1.like('%' + palabra + '%'))
        direc2 = Recolector.query.filter(Recolector.direccion2.like('%' + palabra + '%'))
        tmp = TipoRecolector.query.filter(TipoRecolector.descripcion.like('%' + palabra + '%')).first()
        if tmp != None:
            tipo = Recolector.query.filter(Recolector.tipo_prod.like('%' + str(tmp.id) + '%'))
            productores = cedula.union(nombre, apellido, telefono, direc1, direc2, tipo)
        else:
            productores = cedula.union(nombre, apellido, telefono, direc1, direc2)

    tipo_prod = TipoRecolector.query.all()
    return render_template('recolector.html', error=error, admin=session['rol_admin'], productor=productores, tipo_prod=tipo_prod)

#----------------------------------------------------------------------------------------------------------------------
# Logger de Eventos (requiere iniciar sesión)
@app.route('/eventos')
@login_required
def eventos():
    return render_template('eventos.html')

#----------------------------------------------------------------------------------------------------------------------
# Portafolio de Cosechas
@app.route("/cosecha", methods=['GET', 'POST'])
@login_required
def cosecha():
    error=None
    cosechas = Cosecha.query.all()

    if request.method == 'POST':
        # error = verificar_cosecha(request.form, Cosecha)
        if error is not None:
            return render_template('cosecha.html', error=error, admin=session['rol_admin'], cosechas=cosechas)
        print(request.form)
        try:
            descripcion = request.form['descripcion']
            y, m, d = request.form['inicio'].split('-')
            inicio = datetime.datetime(int(y), int(m), int(d))
            y, m, d = request.form['cierre'].split('-')
            cierre = datetime.datetime(int(y), int(m), int(d))
            
            cosecha = Cosecha(descripcion=descripcion, inicio=inicio, cierre=cierre)
            db.session.add(cosecha)
            db.session.commit()
            flash('Se ha agregado exitosamente.')
            return redirect(url_for('cosecha'))
        except:
            error = "Hubo un error agregando la cosecha."

    return render_template('cosecha.html', error=error, admin=session['rol_admin'], cosechas=cosechas)

# Borrar datos de /cosecha
@app.route('/cosecha/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_cosecha(id):
    cosecha_to_delete = Cosecha.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(cosecha_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('cosecha'))
        except:
            error = "Hubo un error borrando la cosecha."
            
# Modificar datos de /cosecha
@app.route('/cosecha/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_cosecha(id):
    error=None
    cosechas = Cosecha.query.all()
    cosecha_to_update = Cosecha.query.get_or_404(id)
    
    if request.method == "POST":
        # error = verificar_cosecha(request.form, Cosecha)
        if error is not None:
            return render_template('cosecha.html', error=error, admin=session['rol_admin'], cosechas=cosechas)
        
        cosecha_to_update.descripcion = request.form['descripcion']
        y, m, d = request.form['inicio'].split('-')
        cosecha_to_update.inicio = datetime.datetime(int(y), int(m), int(d))
        y, m, d = request.form['cierre'].split('-')
        cosecha_to_update.cierre = datetime.datetime(int(y), int(m), int(d))

        try:
            db.session.commit()
            flash('Se ha modificado exitosamente.')
            return redirect(url_for('cosecha'))
        except:
            error = 'No se pudo actualizar la cosecha.'
            return render_template('cosecha.html', error=error, admin=session['rol_admin'], cosechas=cosechas)

    return render_template('cosecha.html', error=error, admin=session['rol_admin'], cosechas=cosechas)

# Habilitar / Deshabilitar Cosechas
@app.route('/cosecha/<int:id>/habilitar', methods=['GET'])
@login_required
def habilitar_cosecha(id):
    error=None
    cosechas = Cosecha.query.all()
    cosecha_to_update = Cosecha.query.get_or_404(id)

    try:
        cosecha_to_update.estado = not cosecha_to_update.estado
        db.session.commit()
        if (cosecha_to_update.estado):
            flash('Se ha habilitado la cosecha exitosamente.')
        else:
            flash('Se ha deshabilitado la cosecha exitosamente.')
        return redirect(url_for('cosecha'))
    except:
        if (cosecha_to_update.estado):
            error = 'No se pudo habilitar la cosecha.'
        else:
            error = 'No se pudo deshabilitar la cosecha.'
        return render_template('cosecha.html', error=error, admin=session['rol_admin'], cosechas=cosechas)

# Search Bar Cosechas
@app.route('/cosecha/search', methods=['GET', 'POST'])
@login_required
def search_cosecha():
    cosechas = []

    if request.method == "POST":
        palabra = request.form['search_cosecha']
        descripcion = Cosecha.query.filter(Cosecha.descripcion.like('%' + palabra + '%'))
        inicio = Cosecha.query.filter(Cosecha.inicio.like('%' + palabra + '%'))
        cierre = Cosecha.query.filter(Cosecha.cierre.like('%' + palabra + '%'))
        cosechas = descripcion.union(inicio).union(cierre).all()

    return render_template("/cosecha.html", admin=session['rol_admin'], cosechas=cosechas)


#----------------------------------------------------------------------------------------------------------------------
# Generar Compras 
@app.route("/cosecha/<int:id>/compras", methods=['GET', 'POST'])
@login_required
def compras(id):
    error=None
    cosecha= Cosecha.query.get_or_404(id)
    compras = Compra.query.filter_by(cosecha_id=id).all()
    tipo_prod = TipoRecolector.query.all()

    if request.method == "POST":
        # error = verificar_compra(request.form, Compra)
        if error is not None:
            return render_template('compras.html', error=error, admin=session['rol_admin'], cosecha=cosecha, tipo_prod=tipo_prod)

        try:
            y, m, d = request.form['fecha'].split('-')
            fecha = datetime.datetime(int(y), int(m), int(d))
            prod = Recolector.query.filter_by(ci=request.form['cedula']).first()
            tipo_recolector = TipoRecolector.query.filter_by(id=request.form['rol']).first() 
            clase_cacao = request.form['clase_cacao']
            precio = request.form.get('precio', type=float)
            cantidad = request.form.get('cantidad', type=float)
            humedad = request.form.get('humedad', type=float)
            merma_porcentaje = request.form.get('merma_porcentaje', type=float)
            merma_kg = request.form.get('merma_kg', type=float)
            cantidad_total = request.form.get('cantidad_total', type=float)
            monto = request.form.get('monto', type=float)
            observacion = request.form['observacion']
           
            compra = Compra(cosechas=cosecha, fecha=fecha, productores=prod, tipo_prod=tipo_recolector, 
                            clase_cacao=clase_cacao, precio=precio, cantidad=cantidad, humedad=humedad, 
                            merma_porcentaje=merma_porcentaje, merma_kg=merma_kg, cantidad_total=cantidad_total, monto=monto, 
                            observacion=observacion)

            db.session.add(compra)
            db.session.commit()
            flash('Se ha registrado exitosamente.')
            return redirect(url_for('compras', id=id))            
        except:
            error = "Hubo un error agregando la compra."

    return render_template('compras.html', error=error, admin=session['rol_admin'], 
                            cosecha=cosecha, compras=compras, tipo_prod=tipo_prod)

# Search Bar de compras
@app.route("/cosecha/<int:id>/compras/search", methods=['GET', 'POST'])
@login_required
def search_compras(id):
    error = None
    cosecha= Cosecha.query.get_or_404(id)
    tipo_prod = TipoRecolector.query.all()
    compras = []

    if request.method == "POST":
        palabra = request.form['search_compra']
        fecha = Compra.query.filter(Compra.fecha.like('%' + palabra + '%'), Compra.cosecha_id==id)
        clase_cacao = Compra.query.filter(Compra.clase_cacao.like('%' + palabra + '%'), Compra.cosecha_id==id)
        precio = Compra.query.filter(Compra.precio.like('%' + palabra + '%'), Compra.cosecha_id==id)
        cantidad = Compra.query.filter(Compra.cantidad.like('%' + palabra + '%'), Compra.cosecha_id==id)
        humedad = Compra.query.filter(Compra.humedad.like('%' + palabra + '%'), Compra.cosecha_id==id)
        merma_porcentaje = Compra.query.filter(Compra.merma_porcentaje.like('%' + palabra + '%'), Compra.cosecha_id==id)
        merma_kg = Compra.query.filter(Compra.merma_kg.like('%' + palabra + '%'), Compra.cosecha_id==id)
        cantidad_total = Compra.query.filter(Compra.cantidad_total.like('%' + palabra + '%'), Compra.cosecha_id==id)
        monto = Compra.query.filter(Compra.monto.like('%' + palabra + '%'), Compra.cosecha_id==id)
        observacion = Compra.query.filter(Compra.observacion.like('%' + palabra + '%'), Compra.cosecha_id==id)
        compras = fecha.union(clase_cacao, precio, cantidad, humedad, merma_porcentaje, merma_kg, cantidad_total, monto, observacion)

        tmp = Recolector.query.filter(Recolector.ci.like('%' + palabra + '%')).first()
        if tmp is not None:
            prod = Compra.query.filter(Compra.productor_id.like('%' + str(tmp.id) + '%'), Compra.cosecha_id==id)
            compras = compras.union(prod)

        tmp = TipoRecolector.query.filter(TipoRecolector.descripcion.like('%' + palabra + '%')).first()
        if tmp is not None:
            tipo = Compra.query.filter(Compra.tipo_recolector.like('%' + str(tmp.id) + '%'), Compra.cosecha_id==id)
            compras = compras.union(tipo)    

    return render_template('compras.html', error=error, admin=session['rol_admin'], 
                            cosecha=cosecha, compras=compras, tipo_prod=tipo_prod)

# Borrar datos de compra
@app.route('/cosecha/<int:cosecha_id>/compras/<int:compra_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_compra(cosecha_id, compra_id):
    compra_to_delete = Compra.query.get_or_404(compra_id)
    if request.method == "POST":
        try:
            db.session.delete(compra_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('compras', id=cosecha_id))
        except:
            error = "Hubo un error borrando la cosecha."

# Editar datos de compra
@app.route('/cosecha/<int:cosecha_id>/compras/<int:compra_id>/update', methods=['GET', 'POST'])
@login_required
def update_compra(cosecha_id, compra_id):
    error=None
    cosecha = Cosecha.query.get_or_404(cosecha_id)
    compra_to_update = Compra.query.get_or_404(compra_id)
    tipo_prod = TipoRecolector.query.all()
    compras = Compra.query.filter_by(cosecha_id=cosecha_id).all()

    if request.method == "POST":
        print(request.form)

        # Verifica los campos de compra
        # error = verificar_compra(request.form, Compra)
        if error is not None:
            return render_template('compras.html', error=error, admin=session['rol_admin'], 
                    cosecha=cosecha, compras=compras, tipo_prod=tipo_prod)

        try:
            compra_to_update.clase_cacao = request.form['clase_cacao']
            compra_to_update.precio = request.form.get('precio', type=float)
            compra_to_update.cantidad = request.form.get('cantidad', type=float)
            compra_to_update.humedad = request.form.get('humedad', type=float)
            compra_to_update.merma_porcentaje = request.form.get('merma_porcentaje', type=float)
            compra_to_update.merma_kg = request.form.get('merma_kg', type=float)
            compra_to_update.cantidad_total = request.form.get('cantidad_total', type=float)
            compra_to_update.monto = request.form.get('monto', type=float)
            compra_to_update.observacion = request.form['observacion']

            db.session.commit()
            flash('Se ha actualizado exitosamente.')
            return redirect(url_for('compras', id=cosecha_id))
        except:
            error = "Hubo un error actualizando la cosecha."
    
    return render_template('compras.html', error=error, admin=session['rol_admin'], 
                            cosecha=cosecha, compras=compras, tipo_prod=tipo_prod)


if __name__ == '__main__':
    app.run(debug=True)