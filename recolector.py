from flask import flash, redirect, url_for, request, render_template
from __init__ import app, db
from models import TipoRecolector, Recolector
from verificadores import verificar_recolector
from decoradores import login_required, analyst_only

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
        # Verifica los campos del registro de Recolector
        error = verificar_recolector(request.form, Recolector)
        if error is not None:
            return render_template("recolector.html", error=error, tipo_prod=tipo_recolector, recolector=recolectores) 
            
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
    prod_to_update = Recolector.query.get_or_404(id)

    if request.method == "POST":
        # Verifica los campos del registro de Recolector
        error = verificar_recolector(request.form, Recolector, prod_to_update)
        if error is not None:
            return render_template("recolector.html", error=error, recolector=recolectores, tipo_prod=tipo_prod)     
        
        # Modificar los datos del tipo de recolector
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
