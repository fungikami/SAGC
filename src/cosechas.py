from flask import render_template, request, redirect, url_for, flash, session
from app import app, db
from src.models import Cosecha, Evento
from src.decoradores import login_required
from src.verificadores import verificar_cosecha
import datetime

@app.route("/cosecha", methods=['GET', 'POST'])
@login_required
def cosecha():
    """ Portafolio de cosechas """

    error=None
    cosechas = Cosecha.query.all()

    if request.method == 'POST':
        error = verificar_cosecha(request.form, Cosecha)
        if error is not None:
            return render_template('cosecha.html', error=error, cosechas=cosechas) 
        
        try:
            descripcion = request.form['descripcion']
            y, m, d = request.form['inicio'].split('-')
            inicio = datetime.datetime(int(y), int(m), int(d))
            y, m, d = request.form['cierre'].split('-')
            cierre = datetime.datetime(int(y), int(m), int(d))
            cosecha = Cosecha(descripcion=descripcion, inicio=inicio, cierre=cierre)

            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Agregar Cosecha'
            modulo = 'Cosecha'
            evento_desc = str(cosecha)
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            db.session.add(evento)
            db.session.add(cosecha)
            db.session.commit()
            flash('Se ha agregado exitosamente.')
            return redirect(url_for('cosecha'))
        except:
            error = "Hubo un error agregando la cosecha."

    return render_template('cosecha.html', error=error, cosechas=cosechas) 

@app.route('/cosecha/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_cosecha(id):
    """ Borrar cosecha """

    cosecha_to_delete = Cosecha.query.filter_by(id=id).first()

    # Verificar que la cosecha exista en la base de datos
    if cosecha_to_delete is None:
        cosechas = Cosecha.query.all()
        error = "La cosecha no se encuentra registrada."
        return render_template('cosecha.html', error=error, cosechas=cosechas) 

    if request.method == "POST":
        try:
            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Eliminar Cosecha'
            modulo = 'Cosecha'
            evento_desc = str(cosecha_to_delete)
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            db.session.add(evento)

            db.session.delete(cosecha_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('cosecha'))
        except:
            error = "Hubo un error borrando la cosecha."
            
@app.route('/cosecha/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_cosecha(id):
    """ Modificar cosecha """

    error=None
    cosechas = Cosecha.query.all()
    cosecha_to_update = Cosecha.query.filter_by(id=id).first()

    # Verificar que la cosecha exista en la base de datos
    if cosecha_to_update is None:
        error = "La cosecha no se encuentra registrada."
        return render_template('cosecha.html', error=error, cosechas=cosechas) 
    
    if request.method == "POST":
        error = verificar_cosecha(request.form, Cosecha, cosecha_to_update)
        if error is not None:
            return render_template('cosecha.html', error=error, cosechas=cosechas) 
        evento_desc = str(cosecha_to_update)
        cosecha_to_update.descripcion = request.form['descripcion']
        y, m, d = request.form['inicio'].split('-')
        cosecha_to_update.inicio = datetime.datetime(int(y), int(m), int(d))
        y, m, d = request.form['cierre'].split('-')
        cosecha_to_update.cierre = datetime.datetime(int(y), int(m), int(d))

        fecha = datetime.datetime.now()
        evento_user = session['usuario']
        operacion = 'Editar Cosecha'
        modulo = 'Cosecha'
        evento_desc += ";" + str(cosecha_to_update)
        evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

        try:
            db.session.add(evento)
            db.session.commit()
            flash('Se ha modificado exitosamente.')
            return redirect(url_for('cosecha'))
        except:
            error = 'No se pudo actualizar la cosecha.'
            return render_template('cosecha.html', error=error, cosechas=cosechas) 

    return render_template('cosecha.html', error=error, cosechas=cosechas) 

@app.route('/cosecha/<int:id>/habilitar', methods=['GET'])
@login_required
def habilitar_cosecha(id):
    """ Habilitar/deshabilitar cosecha """
    error=None
    cosechas = Cosecha.query.all()
    cosecha_to_update = Cosecha.query.filter_by(id=id).first()

    # Verificar que la cosecha exista en la base de datos
    if cosecha_to_update is None:
        error = "La cosecha no se encuentra registrada."
        return render_template('cosecha.html', error=error, cosechas=cosechas) 

    fecha = datetime.datetime.now()
    evento_user = session['usuario']
    operacion = 'Habilitar Cosecha' if not cosecha_to_update.estado else 'Deshabilitar Cosecha'
    modulo = 'Cosecha'
    evento_desc = str(cosecha_to_update)
    evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

    try:
        cosecha_to_update.estado = not cosecha_to_update.estado
        db.session.add(evento)
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
        return render_template('cosecha.html', error=error, cosechas=cosechas    ) 

@app.route('/cosecha/search', methods=['GET', 'POST'])
@login_required
def search_cosecha():
    """ Buscar cosecha """

    cosechas = []
    if request.method == "POST":
        palabra = request.form['search_cosecha']
        descripcion = Cosecha.query.filter(Cosecha.descripcion.like('%' + palabra + '%'))
        inicio = Cosecha.query.filter(Cosecha.inicio.like('%' + palabra + '%'))
        cierre = Cosecha.query.filter(Cosecha.cierre.like('%' + palabra + '%'))
        cosechas = descripcion.union(inicio).union(cierre).all()

    return render_template("/cosecha.html", cosechas=cosechas) 
