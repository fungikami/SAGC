from flask import render_template, request, redirect, url_for, flash
from app import app, db
from src.models import Cosecha, TipoRecolector, Recolector, Compra, Evento
from src.decoradores import login_required

#----------------------------------------------------------------------------------------------------------------------
# Logger de Eventos (requiere iniciar sesión)
@app.route('/eventos')
@login_required
def eventos():

    eventos = Evento.query.all()

    return render_template('eventos.html', eventos=eventos)

# Borrar datos de /eventos
@app.route('/eventos/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_evento(id):
    evento_to_delete = Evento.query.filter_by(id=id).first()

    # Verificar que la cosecha exista en la base de datos
    if evento_to_delete is None:
        eventos = Evento.query.all()
        error = "El evento no se encuentra registrado."
        return render_template('eventos.html', error=error, eventos=eventos) 

    if request.method == "POST":
        try:
            db.session.delete(evento_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('eventos'))
        except:
            error = "Hubo un error eliminando el evento."

# Search Bar Cosechas
@app.route('/eventos/search', methods=['GET', 'POST'])
@login_required
def search_eventos():
    eventos = []

    if request.method == "POST":
        palabra = request.form['search_evento']
        usuario = Evento.query.filter(Evento.usuario.like('%' + palabra + '%'))
        evento = Evento.query.filter(Evento.evento.like('%' + palabra + '%'))
        modulo = Evento.query.filter(Evento.modulo.like('%' + palabra + '%'))
        fecha = Evento.query.filter(Evento.fecha.like('%' + palabra + '%'))
        descripcion = Evento.query.filter(Evento.descripcion.like('%' + palabra + '%'))

        eventos = descripcion.union(usuario).union(evento).union(modulo).union(fecha).all()

    return render_template("/eventos.html",eventos=eventos) 
