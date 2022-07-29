from flask import flash, redirect, url_for, request, render_template, session
from app import app, db
from src.models import Banco
from src.decoradores import login_required

@app.route('/bancos/', methods=['GET'])
@login_required
def bancos():
    """ Logger de transacciones bancarias """
    bancos = Banco.query.all()
    return render_template('bancos.html', bancos=bancos)

@app.route('/bancos/search', methods=['GET'])
@login_required
def search_bancos():
    """ Buscar transaccion bancaria """
    bancos = []
    if request.method == "POST":
        palabra = request.form['search_bancos']
        concepto = Evento.query.filter(Banco.concepto.like('%' + palabra + '%'))
        monto = Evento.query.filter(Banco.monto.like('%' + palabra + '%'))
        fecha = Evento.query.filter(Banco.fecha.like('%' + palabra + '%'))
        bancos = concepto.union(monto, fecha)

    return render_template("bancos.html", bancos=bancos) 
