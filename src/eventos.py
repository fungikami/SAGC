from flask import flash, redirect, url_for, request, render_template, session
from app import app, db
from src.models import Evento
from src.decoradores import login_required

@app.route('/eventos/', methods=['GET'])
@login_required
def eventos():
    """ Logger de eventos """
    return render_template('eventos.html', evento=Evento.query.all())

@app.route('/eventos/<evento_id>/detalles')
@login_required
def detalles(evento_id):
    """ Detalles del evento """
    
    evento = Evento.query.filter_by(id=evento_id).first()
    if ';' in evento.descripcion:
        desc = evento.descripcion.split(';')
    else:
        desc = [evento.descripcion]
    for i in range(len(desc)):
        d = desc[i].replace('\'','').split('(', 1)
        descripcion = d[1].rsplit(')', 1)[0].split(', ')
        desc[i] = descripcion
    if evento.modulo == 'Perfiles':
        columns = ["Nombre del Usuario", "Nombre", "Apellido", "Rol"]
        for i in range(len(desc)):
            rol = desc[i][len(desc[i])-1]
            print(rol)
            if rol == "1":
                desc[i][len(desc[i])-1] = "Administrador"
            elif rol == "2":
                desc[i][len(desc[i])-1] = "Analista de Ventas"
            elif rol == "3":
                desc[i][len(desc[i])-1] = "Vendedor"
            elif rol == "4":
                desc[i][len(desc[i])-1] = "Gerente"
        
    elif evento.modulo == 'Cosecha':
        columns = ["Descripción", "Fecha Inicio", "Fecha Fin"]

    elif evento.modulo == 'Recolector':
        columns = ["Cédula", "Apellido", "Nombre", "Teléfono Local", "Celular", "Tipo-Recolector", "Dirección 1", "Dirección 2"]

    elif evento.modulo == 'Tipo Recolector':
        columns = ["Descripción", "Precio"]

    elif evento.modulo == 'Compra':
        columns = ["Cosecha", "Fecha", "Cédula", "Cacao", "Precio ($)", "Cantidad (Kg)", "Humedad (%)", "Merma (%)", "Merma (Kg)", "Cantidad Total (Kg)", "Monto ($)"]

    print(desc)
    return render_template('eventos_detalles.html', e=evento, columns=columns, descripcion=desc, update=False if len(desc) == 1 else True)

@app.route('/eventos/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_evento(id):
    """ Borrar evento """

    # Verificar que la cosecha exista en la base de datos
    evento_to_delete = Evento.query.filter_by(id=id).first()
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

@app.route('/eventos/search', methods=['GET', 'POST'])
@login_required
def search_eventos():
    """ Buscar eventos """

    eventos = []
    if request.method == "POST":
        palabra = request.form['search_evento']
        usuario = Evento.query.filter(Evento.usuario.like('%' + palabra + '%'))
        evento = Evento.query.filter(Evento.evento.like('%' + palabra + '%'))
        modulo = Evento.query.filter(Evento.modulo.like('%' + palabra + '%'))
        fecha = Evento.query.filter(Evento.fecha.like('%' + palabra + '%'))
        descripcion = Evento.query.filter(Evento.descripcion.like('%' + palabra + '%'))
        eventos = descripcion.union(usuario).union(evento).union(modulo).union(fecha).all()

    return render_template("eventos.html", eventos=eventos) 
