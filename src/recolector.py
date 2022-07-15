from flask import flash, redirect, url_for, request, render_template, session
from app import app, db
from src.models import TipoRecolector, Recolector, Evento
from src.verificadores import verificar_recolector
from src.decoradores import login_required, analyst_only
import datetime

#----------------------------------------------------------------------------------------------------------------------
# Datos del Recolector (requiere iniciar sesión)
@app.route('/recolector', methods=['GET', 'POST'])
@login_required
@analyst_only
def recolector():
    error=None
    tipo_recolector = TipoRecolector.query.all()
    recolectores = Recolector.query.all()

    if request.method == 'POST':
        error = verificar_recolector(request.form, Recolector)
        if error is not None:
            return render_template("recolector.html", error=error, tipo_prod=tipo_recolector, recolector=recolectores) 
            
        try:
            ci, rol = request.form['cedula'], request.form['rol']   
            nombre, apellido = request.form['nombre'], request.form['apellido']
            telefono, celular = request.form['telefono'], request.form['celular']
            dir1, dir2 = request.form['direccion1'], request.form['direccion2']

            tipo_prod = TipoRecolector.query.filter_by(id=rol).first()
            new_prod = Recolector(ci=ci, nombre=nombre, apellido=apellido, telefono=telefono, celular=celular,
                        tipo_recolector=tipo_prod, direccion1=dir1, direccion2=dir2)

            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Agregar Recolector'
            modulo = 'Recolector'
            evento_desc = 'AGREGAR DESCRIPCION'
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            db.session.add(evento)
            
            db.session.add(new_prod)
            db.session.commit()
            flash('Se ha registrado exitosamente.')
            return redirect(url_for('recolector'))
        except:
            error = 'No se pudo guardar el usuario en la base de datos'

    return render_template('recolector.html', error=error, recolector=recolectores, tipo_prod=tipo_recolector) 

# Actualizar datos de /recolector
@app.route('/recolector/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_recolector(id):
    error=None
    tipo_prod = TipoRecolector.query.all()
    recolectores = Recolector.query.all()
    reco = Recolector.query.get_or_404(id)

    if request.method == "POST":
        error = verificar_recolector(request.form, Recolector, reco)
        if error is not None:
            return render_template("recolector.html", error=error, recolector=recolectores, tipo_prod=tipo_prod)     
        
        try:
            reco.ci = request.form['cedula']
            reco.nombre = request.form['nombre']
            reco.apellido = request.form['apellido']
            reco.telefono = request.form['telefono']
            reco.celular = request.form['celular']
            reco.direccion1 = request.form['direccion1']
            reco.direccion2 = request.form['direccion2']
            reco.tipo_prod = request.form['rol'] 

            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Editar Recolector'
            modulo = 'Recolector'
            evento_desc = 'AGREGAR DESCRIPCION'
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            db.session.add(evento)    
            db.session.commit()
            flash('Se ha modificado exitosamente.')
            return redirect(url_for('recolector'))
        except:
            error = 'No se pudo actualizar el recolector.'
    
    return render_template('recolector.html', error=error, recolector=recolectores, tipo_prod=tipo_prod) 

# Borrar datos de /recolector
@app.route('/recolector/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_recolector(id):
    error=None
    tipo_prod = TipoRecolector.query.all()
    recolectores = Recolector.query.all()
    prod_to_delete = Recolector.query.get_or_404(id)
    if request.method == "POST":
        try:
            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Eliminar Recolector'
            modulo = 'Recolector'
            evento_desc = 'AGREGAR DESCRIPCION'
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            db.session.add(evento)
            db.session.delete(prod_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('recolector'))
        except:
            error = "Hubo un error eliminando el recolector."

    return render_template('recolector.html', error=error, recolector=recolectores, tipo_prod=tipo_prod)

# Search Bar Recolector
@app.route('/recolector/search', methods=['GET', 'POST'])
@login_required
def search_recolector():
    error = None
    recolectores = []
    
    if request.method == "POST":
        palabra = request.form['search_recolector']
        cedula = Recolector.query.filter(Recolector.ci.like('%' + palabra + '%'))
        nombre = Recolector.query.filter(Recolector.nombre.like('%' + palabra + '%'))
        apellido = Recolector.query.filter(Recolector.apellido.like('%' + palabra + '%'))
        telefono = Recolector.query.filter(Recolector.telefono.like('%' + palabra + '%'))
        direc1 = Recolector.query.filter(Recolector.direccion1.like('%' + palabra + '%'))
        direc2 = Recolector.query.filter(Recolector.direccion2.like('%' + palabra + '%'))
        tmp = TipoRecolector.query.filter(TipoRecolector.descripcion.like('%' + palabra + '%')).first()
        if tmp != None:
            tipo = Recolector.query.filter(Recolector.tipo_prod.like('%' + str(tmp.id) + '%'))
            recolectores = cedula.union(nombre, apellido, telefono, direc1, direc2, tipo)
        else:
            recolectores = cedula.union(nombre, apellido, telefono, direc1, direc2)

    tipo_prod = TipoRecolector.query.all()
    return render_template('recolector.html', error=error, recolector=recolectores, tipo_prod=tipo_prod)
