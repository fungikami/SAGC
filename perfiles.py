from flask import flash, redirect, url_for, request, render_template
from werkzeug.security import generate_password_hash
from __init__ import app, db
from decoradores import login_required, admin_only
from models import *
from verificadores import verificar_perfil

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
    cosechas = Cosecha.query.all()
    rols = Rol.query.all()
    user_to_update = Usuario.query.get_or_404(id)
    
    if request.method == "POST":
        error = verificar_perfil(request.form, Usuario, user_to_update)
        if error is not None:
            return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols, cosechas=cosechas)   

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
            return render_template("perfiles.html", error=error, usuarios=usuarios, rols=rols, cosechas=cosechas)   
    
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
