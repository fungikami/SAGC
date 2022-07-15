from flask import flash, redirect, url_for, request, render_template, session
from werkzeug.security import generate_password_hash
from app import app, db
from src.decoradores import login_required, admin_only
from src.models import *
from src.verificadores import verificar_perfil
import datetime

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

        try:
            nombre_usuario = request.form['nombre_usuario']
            nombre, apellido = request.form['nombre'], request.form['apellido']
            password = generate_password_hash(request.form['password'], "sha256")
            rol, cosecha = request.form['rol'], request.form['cosecha']
            new_user = Usuario(nombre_usuario=nombre_usuario, nombre=nombre, apellido=apellido, password=password, rol=rol)
            db.session.add(new_user)
            if cosecha != '':
                tmp = Cosecha.query.filter_by(id = cosecha).first()
                new_user.cosechas.append(tmp)

            #fecha = datetime.datetime.now()
            #evento_user = session['usuario']
            #operacion = 'Agregar Usuario'
            #modulo = 'Perfiles'
            #evento_desc = 'AGREGAR DESCRIPCION'
            #evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            #db.session.add(evento)    
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
    cosechas = Cosecha.query.all()
    rols = Rol.query.all()
    user = Usuario.query.get_or_404(id)
    
    if request.method == "POST":
        error = verificar_perfil(request.form, Usuario, user)
        if error is not None:
            return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols, cosechas=cosechas)   

        user.nombre_usuario = request.form['nombre_usuario']
        user.nombre, user.apellido = request.form['nombre'], request.form['apellido']
        user.rol, cosecha = request.form['rol'], request.form['cosecha']
        if cosecha != '' and cosecha.lower() != 'ninguna':
            tmp = Cosecha.query.filter_by(id = cosecha).first()
            user.cosechas.append(tmp)

        try:
            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Editar Usuario'
            modulo = 'Perfiles'
            evento_desc = 'AGREGAR DESCRIPCION'
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            db.session.add(evento)  
            db.session.commit()
            flash('Se ha modificado exitosamente.')
            return redirect(url_for('perfiles'))
        except:
            error = 'No se pudo actualizar al usuario.'
            return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols, cosechas=cosechas)   
    
    return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols) 

# Borrar datos de /Perfiles
@app.route('/perfiles/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_perfiles(id):
    user = Usuario.query.get_or_404(id)
    if request.method == "POST":
        try:
            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Eliminar Usuario'
            modulo = 'Perfiles'
            evento_desc = 'AGREGAR DESCRIPCION'
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            db.session.add(evento)  
            db.session.delete(user)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('perfiles'))
        except:
            return "Hubo un error borrando al usuario."

# Search Bar Perfiles
@app.route('/perfiles/search', methods=['GET', 'POST'])
@login_required
def search_perfil():
    error = None
    usuarios = []
    cosechas = Cosecha.query.all()
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

    return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols, cosechas=cosechas) 
