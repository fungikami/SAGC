from flask import render_template, request, redirect, url_for, flash
from app import app, db
from src.models import Cosecha, TipoRecolector, Recolector, Compra
from src.decoradores import login_required

#----------------------------------------------------------------------------------------------------------------------
# Logger de Eventos (requiere iniciar sesión)
@app.route('/eventos')
@login_required
def eventos():
    return render_template('eventos.html')