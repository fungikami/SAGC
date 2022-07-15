from flask import render_template, request, redirect, url_for, flash
from app import app, db
from src.models import Evento
from src.decoradores import login_required

#----------------------------------------------------------------------------------------------------------------------
# Logger de Eventos (requiere iniciar sesión)
#@app.route('/eventos')
#@login_required
#def eventos():

#    eventos = Evento.query.all()
#    return render_template('eventos.html', eventos=eventos)

# Paginacion Eventos
@app.route('/eventos/')
@login_required
def eventos():
    ROWS_PER_PAGE = 2

    page = request.args.get('page', 1, type=int)

    eventos = Evento.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template('eventos.html', eventos=eventos)

# Detalles del evento (requiere iniciar sesión)
@app.route('/eventos/detalles/<evento_id>')
@login_required
def detalles(evento_id):
    
        evento = Evento.query.filter_by(id=evento_id).first()
        desc = evento.descripcion.replace('\'','').split('(', 1)
        descripcion = desc[1].rsplit(')', 1)[0].split(', ')
        if evento.modulo == 'Perfiles':
            columns = ["Nombre del Usuario", "Nombre", "Apellido", "Rol"]
            rol = descripcion[len(descripcion)-1]
            if rol == "'1'":
                descripcion[len(descripcion)-1] = "Administrador"
            elif rol == "'2'":
                descripcion[len(descripcion)-1] = "Analista de Ventas"
            elif rol == "'3'":
                descripcion[len(descripcion)-1] = "Vendedor"
            else:
                descripcion[len(descripcion)-1] = "Gerente"
            
        elif evento.modulo == 'Cosecha':
            columns = ["Descripción", "Fecha Inicio", "Fecha Fin"]
            descripcion.pop()

        elif evento.modulo == 'Recolector':
            columns = ["Cédula", "Apellido", "Nombre", "Teléfono Local", "Celular", "Tipo-Recolector", "Dirección 1", "Dirección 2"]

        elif evento.modulo == 'Tipo Recolector':
            columns = ["Descripción", "Precio"]

        elif evento.modulo == 'Compra':
            columns = ["Cosecha", "Fecha", "Cédula", "Cacao", "Precio ($)", "Cantidad (Kg)", "Humedad (%)", "Merma (%)", "Merma (Kg)", "Cantidad Total (Kg)", "Monto ($)"]

        return render_template('eventos_detalles.html', e=evento, columns=columns, descripcion=descripcion)

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

# Search Bar Eventos
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
