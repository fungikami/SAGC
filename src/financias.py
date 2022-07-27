from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy import func
from app import app, db
from src.models import *
from src.decoradores import login_required
from src.verificadores import verificar_cosecha_exists
import datetime

@app.route("/cosecha/<cosecha_id>/financias/<tipo>", methods=['GET', 'POST'])
@login_required
def financias(cosecha_id, tipo):
    """ Generar financias / Listar financias """

    error=None
    recolectores = Recolector.query.all()

    # Verificar que la cosecha exista en la base de datos o esté habilitada
    cosecha = Cosecha.query.filter_by(id=cosecha_id).first()
    error = verificar_cosecha_exists(cosecha_id, tipo, cosecha)
    if error is not None:
        cosechas = Cosecha.query.all()
        return render_template('cosecha.html', error=error, cosechas=cosechas) 
    
    if request.method == "POST":
        # Verifica que el recolector esté en la base de datos
        cedula = request.form['cedula']
        recolector = Recolector.query.filter_by(ci=cedula).first()
        if recolector is None:
            tipo_recolector = TipoRecolector.query.all()
            error = "El recolector no se encuentra registrado. Registre el recolector antes de realizar la compra"
            return render_template("recolector.html", error=error, tipo_prod=tipo_recolector, recolector=recolectores) 

        try:
            print("todo")            
        except:
            error = "Hubo un error agregando el financiamiento."

    hide = True if tipo == "listar" else False
    return render_template('financias.html', error=error, cosecha=cosecha, recolectores=recolectores, 
            hide=hide)
