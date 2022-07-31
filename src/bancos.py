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
            concepto = 'Crédito para compras'
            monto = request.form['agregar_credito']
            #aggGerente = True
            banco = Banco(fecha=fecha, concepto=concepto, monto=monto, credito=True)

            db.session.add(banco)
            db.session.commit()
            flash('Se ha registrado el crédito exitosamente.')
            return redirect(url_for('bancos')) 
        except:
            error = "Hubo un error agregando la compra."
    saldo = sum([b.monto for b in bancos if b.credito]) - sum([b.monto for b in bancos if not b.credito])
    return render_template('bancos.html', error=error, bancos=bancos, saldo=saldo)

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

@app.route('/bancos/<bancos_id>/revertir', methods=['GET', 'POST'])
@login_required
def revertir_bancos():
    """ Revertir transacciones bancarias """

    if request.method == "POST":
        try:
            fecha = datetime.datetime.now()
            concepto = 'Reverso de crédito'
            monto = Banco.query.filter(Banco.id == bancos_id).first().monto
            banco = Banco(fecha=fecha, concepto=concepto, monto=monto, credito=False)

            db.session.add(banco)
            db.session.commit()
            flash('Se ha registrado el crédito exitosamente.')
            return redirect(url_for('bancos')) 
        except:
            error = "Hubo un error agregando la compra."
    return redirect(url_for('bancos', error=error, bancos=bancos))