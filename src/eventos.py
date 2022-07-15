from flask import render_template, request, redirect, url_for, flash
from app import app, db
from src.models import Usuario, Cosecha, Recolector, TipoRecolector, Compra, Evento
from src.decoradores import login_required

#----------------------------------------------------------------------------------------------------------------------
# Logger de Eventos (requiere iniciar sesión)
@app.route('/eventos')
@login_required
def eventos():

    eventos = Evento.query.all()

    return render_template('eventos.html', eventos=eventos)

# Detalles del evento (requiere iniciar sesión)
@app.route('/eventos/detalles/<evento_id>')
@login_required
def detalles(evento_id):
    
        evento = Evento.query.filter_by(id=evento_id).first()
        print(evento.descripcion)
        desc = evento.descripcion.replace('\'','').split('(', 1)
        descripcion = desc[1].rsplit(')', 1)[0].split(', ')
        print(descripcion)
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
            print(descripcion)
            descripcion.pop()
            print(descripcion)

        elif evento.modulo == 'Recolector':
            columns = ["Cédula", "Apellido", "Nombre", "Teléfono Local", "Celular", "Tipo-Recolector", "Dirección 1", "Dirección 2"]

        elif evento.modulo == 'Tipo Recolector':
            columns = ["Descripción", "Precio"]

        elif evento.modulo == 'Compra':
            columns = ["Cosecha", "Fecha", "Cédula", "Cacao", "Precio ($)", "Cantidad (Kg)", "Humedad (%)", "Merma (%)", "Merma (Kg)", "Cantidad Total (Kg)", "Monto ($)"]
        else:
            print("Ninguno")
        return render_template('eventos_detalles.html', e=evento, columns=columns, descripcion=descripcion)