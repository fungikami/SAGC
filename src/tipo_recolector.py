from flask import flash, redirect, url_for, request, render_template, session
from app import app, db
from src.decoradores import login_required, analyst_only
from src.models import TipoRecolector, Evento
from src.verificadores import verificar_tipo_recolector
import datetime

@app.route('/tipo_recolector', methods=['GET', 'POST'])
@login_required
@analyst_only
def tipo_recolector():
    """ Página de tipo de recolectores """

    error=None
    tipo_prod = TipoRecolector.query.all()

    if request.method == 'POST':
        error = verificar_tipo_recolector(request.form, TipoRecolector)
        if error is not None:
            return render_template("tipo_recolector.html", error=error, tipo_prod=tipo_prod) 

        try:
            descripcion, precio = request.form['descripcion'], request.form['precio']
            new_type = TipoRecolector(descripcion=descripcion, precio=precio)

            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Agregar Tipo Recolector'
            modulo = 'Tipo Recolector'
            evento_desc = str(new_type)
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            db.session.add(evento)
            db.session.add(new_type)
            db.session.commit()
            flash('Se ha registrado exitosamente.')
            return redirect(url_for('tipo_recolector'))
        except:
            error = 'No se pudo guardar el tipo de recolector en la base de datos'
            
    return render_template("tipo_recolector.html", error=error, tipo_prod=tipo_prod) 

@app.route('/tipo_recolector/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_tipo_recolector(id):
    """ Actualiza los datos de un tipo de recolector """

    error=None
    tipo_prod = TipoRecolector.query.all()
    tipo = TipoRecolector.query.get_or_404(id)

    if request.method == "POST":
        error = verificar_tipo_recolector(request.form, TipoRecolector, tipo)
        if error is not None:
            return render_template("tipo_recolector.html", error=error, tipo_prod=tipo_prod) 

        try:
            evento_desc = str(tipo)
            tipo.descripcion = request.form['descripcion']
            tipo.precio = request.form['precio']

            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Editar Tipo Recolector'
            modulo = 'Tipo Recolector'
            evento_desc += ";" + str(tipo)
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            db.session.add(evento)
            db.session.commit()
            flash('Se ha modificado exitosamente.')
            return redirect(url_for('tipo_recolector'))
        except:
            error = 'No se pudo actualizar el tipo de recolector.'
    
    return render_template("tipo_recolector.html", error=error, tipo_prod=tipo_prod) 

@app.route('/tipo_recolector/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_tipo_recolector(id):
    """ Borra un tipo de recolector """

    error=None
    tipo_prod = TipoRecolector.query.all()
    tipo = TipoRecolector.query.get_or_404(id)
    if request.method == "POST":
        try:
            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Eliminar Tipo Recolector'
            modulo = 'Tipo Recolector'
            evento_desc = str(tipo)
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            db.session.add(evento)
            db.session.delete(tipo)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('tipo_recolector'))
        except:
            return "Hubo un error eliminando el tipo de recolector."

    return render_template("tipo_recolector.html", error=error, tipo_prod=tipo_prod)

@app.route('/tipo_recolector/search', methods=['GET', 'POST'])
@login_required
def search_tipo_recolector():
    """ Busca un tipo de recolector """

    tipo_prod = []
    if request.method == "POST":
        palabra = request.form['search_tipo_recolector']
        tipo_prod = TipoRecolector.query.filter(TipoRecolector.descripcion.like('%' + palabra + '%'))
        
    return render_template("/tipo_recolector.html", tipo_prod=tipo_prod) 