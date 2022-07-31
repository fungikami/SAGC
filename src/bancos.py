from flask import flash, redirect, url_for, request, render_template, session
from app import app, db
from src.models import Banco
from src.decoradores import login_required
import datetime

@app.route('/bancos/', methods=['GET', 'POST'])
@login_required
def bancos():
    """ Logger de transacciones bancarias """
    bancos = Banco.query.all()
    error=None

    if request.method == "POST":
        try:
            fecha = datetime.datetime.now()
            concepto = 'Crédito por compra'
            monto = request.form['agregar_credito']

            banco = Banco(fecha = fecha, concepto = concepto, monto=monto, compra_id = NULL)

            db.session.add(banco)
            db.session.commit()
            flash('Se ha registrado el crédito exitosamente.')
            return redirect(url_for('bancos')) 
        except:
            error = "Hubo un error agregando la compra."

    return render_template('bancos.html', error=error, bancos=bancos)

@app.route('/bancos/search', methods=['GET', 'POST'])
@login_required
def search_bancos():
    """ Buscar transaccion bancaria """
    bancos = []
    if request.method == "POST":
        palabra = request.form['search_bancos']
        concepto = Banco.query.filter(Banco.concepto.like('%' + palabra + '%'))
        monto = Banco.query.filter(Banco.monto.like('%' + palabra + '%'))
        fecha = Banco.query.filter(Banco.fecha.like('%' + palabra + '%'))
        bancos = concepto.union(monto, fecha)

    return render_template("bancos.html", bancos=bancos) 
