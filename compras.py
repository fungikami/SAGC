from flask import render_template, request, redirect, url_for, flash
from __init__ import app, db
from models import Cosecha, TipoRecolector, Recolector, Compra
from decoradores import login_required
import datetime

from tipo_recolector import tipo_recolector

#----------------------------------------------------------------------------------------------------------------------
# Generar Compras 
@app.route("/cosecha/<int:id>/compras", methods=['GET', 'POST'])
@login_required
def compras(id):
    error=None
    cosecha= Cosecha.query.get_or_404(id)
    compras = Compra.query.filter_by(cosecha_id=id).all()
    recolectores = Recolector.query.all()
    #tipo_prod = TipoRecolector.query.all()

    if request.method == "POST":
        try:
            y, m, d = request.form['fecha'].split('-')
            fecha = datetime.datetime(int(y), int(m), int(d))
            
            prod = Recolector.query.filter_by(ci=request.form['cedula']).first()
            tipo_recolector = TipoRecolector.query.filter_by(id=prod.tipo_prod).first()

            clase_cacao = request.form['clase_cacao']
            precio = request.form.get('precio', type=float)
            cantidad = request.form.get('cantidad', type=float)
            humedad = request.form.get('humedad', type=float)
            merma_porcentaje = request.form.get('merma_porcentaje', type=float)
            merma_kg = request.form.get('merma_kg', type=float)
            cantidad_total = request.form.get('cantidad_total', type=float)
            monto = request.form.get('monto', type=float)
            observacion = request.form['observacion']
           
            compra = Compra(cosechas=cosecha, fecha=fecha, recolectores=prod, tipo_prod=tipo_recolector, 
                            clase_cacao=clase_cacao, precio=precio, cantidad=cantidad, humedad=humedad, 
                            merma_porcentaje=merma_porcentaje, merma_kg=merma_kg, cantidad_total=cantidad_total, monto=monto, 
                            observacion=observacion)

            db.session.add(compra)
            db.session.commit()
            flash('Se ha registrado exitosamente.')
            return redirect(url_for('compras', id=id))            
        except:
            error = "Hubo un error agregando la compra."

    return render_template('compras.html', error=error, cosecha=cosecha, compras=compras, recolectores=recolectores) 

# Search Bar de compras
@app.route("/cosecha/<int:id>/compras/search", methods=['GET', 'POST'])
@login_required
def search_compras(id):
    error = None
    cosecha= Cosecha.query.get_or_404(id)
    tipo_prod = TipoRecolector.query.all()
    recolectores = Recolector.query.all()
    compras = []

    if request.method == "POST":
        palabra = request.form['search_compra']
        fecha = Compra.query.filter(Compra.fecha.like('%' + palabra + '%'), Compra.cosecha_id==id)
        clase_cacao = Compra.query.filter(Compra.clase_cacao.like('%' + palabra + '%'), Compra.cosecha_id==id)
        precio = Compra.query.filter(Compra.precio.like('%' + palabra + '%'), Compra.cosecha_id==id)
        cantidad = Compra.query.filter(Compra.cantidad.like('%' + palabra + '%'), Compra.cosecha_id==id)
        humedad = Compra.query.filter(Compra.humedad.like('%' + palabra + '%'), Compra.cosecha_id==id)
        merma_porcentaje = Compra.query.filter(Compra.merma_porcentaje.like('%' + palabra + '%'), Compra.cosecha_id==id)
        merma_kg = Compra.query.filter(Compra.merma_kg.like('%' + palabra + '%'), Compra.cosecha_id==id)
        cantidad_total = Compra.query.filter(Compra.cantidad_total.like('%' + palabra + '%'), Compra.cosecha_id==id)
        monto = Compra.query.filter(Compra.monto.like('%' + palabra + '%'), Compra.cosecha_id==id)
        observacion = Compra.query.filter(Compra.observacion.like('%' + palabra + '%'), Compra.cosecha_id==id)
        compras = fecha.union(clase_cacao, precio, cantidad, humedad, merma_porcentaje, merma_kg, cantidad_total, monto, observacion)

        tmp = Recolector.query.filter(Recolector.ci.like('%' + palabra + '%')).first()
        if tmp is not None:
            prod = Compra.query.filter(Compra.recolector_id.like('%' + str(tmp.id) + '%'), Compra.cosecha_id==id)
            compras = compras.union(prod)

        tmp = TipoRecolector.query.filter(TipoRecolector.descripcion.like('%' + palabra + '%')).first()
        if tmp is not None:
            #tipo = Compra.query.filter(Compra.tipo_recolector.like('%' + str(tmp.id) + '%'), Compra.cosecha_id==id)
            tipo = Compra.query.filter(Compra.recolector_id.like('%' + str(tmp.id) + '%'), Compra.cosecha_id==id)
            compras = compras.union(tipo)    

    return render_template('compras.html', error=error, cosecha=cosecha, compras=compras, tipo_prod=tipo_prod, recolectores=recolectores) 

# Borrar datos de compra
@app.route('/cosecha/<int:cosecha_id>/compras/<int:compra_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_compra(cosecha_id, compra_id):
    compra_to_delete = Compra.query.get_or_404(compra_id)
    if request.method == "POST":
        try:
            db.session.delete(compra_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('compras', id=cosecha_id))
        except:
            error = "Hubo un error borrando la cosecha."

# Editar datos de compra
@app.route('/cosecha/<int:cosecha_id>/compras/<int:compra_id>/update', methods=['GET', 'POST'])
@login_required
def update_compra(cosecha_id, compra_id):
    error=None
    cosecha = Cosecha.query.get_or_404(cosecha_id)
    compra_to_update = Compra.query.get_or_404(compra_id)
    tipo_prod = TipoRecolector.query.all()
    compras = Compra.query.filter_by(cosecha_id=cosecha_id).all()
    recolectores = Recolector.query.all()

    if request.method == "POST":
        try:
            compra_to_update.clase_cacao = request.form['clase_cacao']
            compra_to_update.precio = request.form.get('precio', type=float)
            compra_to_update.cantidad = request.form.get('cantidad', type=float)
            compra_to_update.humedad = request.form.get('humedad', type=float)
            compra_to_update.merma_porcentaje = request.form.get('merma_porcentaje', type=float)
            compra_to_update.merma_kg = request.form.get('merma_kg', type=float)
            compra_to_update.cantidad_total = request.form.get('cantidad_total', type=float)
            compra_to_update.monto = request.form.get('monto', type=float)
            compra_to_update.observacion = request.form['observacion']

            db.session.commit()
            flash('Se ha actualizado exitosamente.')
            return redirect(url_for('compras', id=cosecha_id))
        except:
            error = "Hubo un error actualizando la cosecha."
    
    return render_template('compras.html', error=error, cosecha=cosecha, compras=compras, tipo_prod=tipo_prod, recolectores=recolectores)
