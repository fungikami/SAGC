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
            banco = Banco(fecha=fecha, concepto=concepto, monto=monto, credito=True, agg_gerente=True)

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
        banco_desde, banco_hasta = Banco.query.filter(), Banco.query.filter()
        fecha_inicio, fecha_fin = request.form['Desde'], request.form['Hasta']
        if (fecha_inicio != ''):
            banco_desde = Banco.query.filter(Banco.fecha >= fecha_inicio)
        if (fecha_fin != ''):
            banco_hasta = Banco.query.filter(Banco.fecha <= fecha_fin)
            
        # Intersecta las dos tablas de banco_desde y banco_hasta
        banco_fecha = banco_desde.intersect(banco_hasta)

        palabra = request.form['search_bancos']
        concepto = Banco.query.filter(Banco.concepto.like('%' + palabra + '%'))
        monto = Banco.query.filter(Banco.monto.like('%' + palabra + '%'))
        fecha = Banco.query.filter(Banco.fecha.like('%' + palabra + '%'))
        bancos = concepto.union(monto, fecha)
        bancos = bancos.intersect(banco_fecha)

    saldo = sum([b.monto for b in bancos if b.credito]) - sum([b.monto for b in bancos if not b.credito])
    return render_template("bancos.html", bancos=bancos, saldo=saldo) 

@app.route('/bancos/<banco_id>/revertir', methods=['GET', 'POST'])
@login_required
def revertir_bancos(banco_id):
    """ Revertir transacciones bancarias """
    bancos = Banco.query.all()
    saldo = sum([b.monto for b in bancos if b.credito]) - sum([b.monto for b in bancos if not b.credito])

    credito = Banco.query.filter(Banco.id == banco_id).first()

    # Verifica si el crédito existe
    if credito is None:
        error = "El crédito no existe."
        return render_template("bancos.html", error=error, bancos=bancos, saldo=saldo)

    # Verifica que sea un crédito de gerente
    if not credito or not credito.agg_gerente:
        error = "El crédito no es de gerente."
        return render_template("bancos.html", error=error, bancos=bancos, saldo=saldo)

    if request.method == "POST":
        try:
            # Crear reverso
            fecha = datetime.datetime.now()
            concepto = 'Reverso de crédito'
            monto = credito.monto
            nuevo = Banco(fecha=fecha, concepto=concepto, monto=monto, credito=False)
            db.session.add(nuevo)

            # Actualizar crédito como revertido = True
            credito.revertido = True

            db.session.commit()
            flash('Se ha revertido el crédito exitosamente.')
            return redirect(url_for('bancos')) 
        except:
            error = "Hubo un error al revertir el crédito."

    saldo = sum([b.monto for b in bancos if b.credito]) - sum([b.monto for b in bancos if not b.credito])
    return redirect(url_for('bancos', error=error, bancos=bancos, saldo=saldo))