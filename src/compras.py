from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import func
from app import app, db
from src.models import Cosecha, TipoRecolector, Recolector, Compra
from src.decoradores import login_required
from src.verificadores import verificar_cosecha_exists
import datetime

#----------------------------------------------------------------------------------------------------------------------
# Generar Compras / Listar Compras
@app.route("/cosecha/<cosecha_id>/<tipo>", methods=['GET', 'POST'])
@login_required
def compras(cosecha_id, tipo):
    error=None
    compras = Compra.query.filter_by(cosecha_id=cosecha_id).all()
    recolectores = Recolector.query.all()
    total_cantidad = sum(compra.cantidad_total for compra in compras)
    total_monto = sum(compra.monto for compra in compras)

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
            fecha = datetime.datetime.now()
            clase_cacao = request.form['clase_cacao']
            precio = request.form.get('precio', type=float)
            cantidad = request.form.get('cantidad', type=float)
            humedad = request.form.get('humedad', type=float)
            merma_porcentaje = request.form.get('merma_porcentaje', type=float)
            merma_kg = request.form.get('merma_kg', type=float)
            cantidad_total = request.form.get('cantidad_total', type=float)
            monto = request.form.get('monto', type=float)
            observacion = request.form['observacion']
           
            compra = Compra(cosechas=cosecha, fecha=fecha, recolectores=recolector, 
                            clase_cacao=clase_cacao, precio=precio, cantidad=cantidad, humedad=humedad, 
                            merma_porcentaje=merma_porcentaje, merma_kg=merma_kg, cantidad_total=cantidad_total, monto=monto, 
                            observacion=observacion)

            db.session.add(compra)
            db.session.commit()
            flash('Se ha registrado exitosamente.')
            return redirect(url_for('compras', cosecha_id=cosecha_id, tipo=tipo))            
        except:
            error = "Hubo un error agregando la compra."

    hide = True if tipo == "listar" else False
    return render_template('compras.html', error=error, cosecha=cosecha, compras=compras, recolectores=recolectores,
                           total_cantidad=total_cantidad, total_monto=total_monto, hide=hide)

# Search Bar de Generar Compras / Listar Compras
@app.route("/cosecha/<cosecha_id>/<tipo>/search", methods=['GET', 'POST'])
@login_required
def search_compras(cosecha_id, tipo):
    error = None
    tipo_prod = TipoRecolector.query.all()
    recolectores = Recolector.query.all()
    compras = []
    
    # Verificar que la cosecha exista en la base de datos o esté habilitada
    cosecha = Cosecha.query.filter_by(id=cosecha_id).first()
    error = verificar_cosecha_exists(cosecha_id, tipo, cosecha)
    if error is not None:
        cosechas = Cosecha.query.all()
        return render_template('cosecha.html', error=error, cosechas=cosechas) 

    if request.method == "POST":
        #fecha_inicio = request.form['Desde']
        #fecha_fin = request.form['Hasta']
        #fecha_busqueda = Compra.query.filter(Compra.fecha.between(fecha_inicio, fecha_fin))

        palabra = request.form['search_compra']
        fecha = Compra.query.filter(Compra.fecha.like('%' + palabra + '%'), Compra.cosecha_id==cosecha_id)
        clase_cacao = Compra.query.filter(Compra.clase_cacao.like('%' + palabra + '%'), Compra.cosecha_id==cosecha_id)
        precio = Compra.query.filter(Compra.precio.like('%' + palabra + '%'), Compra.cosecha_id==cosecha_id)
        cantidad = Compra.query.filter(Compra.cantidad.like('%' + palabra + '%'), Compra.cosecha_id==cosecha_id)
        humedad = Compra.query.filter(Compra.humedad.like('%' + palabra + '%'), Compra.cosecha_id==cosecha_id)
        merma_porcentaje = Compra.query.filter(Compra.merma_porcentaje.like('%' + palabra + '%'), Compra.cosecha_id==cosecha_id)
        merma_kg = Compra.query.filter(Compra.merma_kg.like('%' + palabra + '%'), Compra.cosecha_id==cosecha_id)
        cantidad_total = Compra.query.filter(Compra.cantidad_total.like('%' + palabra + '%'), Compra.cosecha_id==cosecha_id)
        monto = Compra.query.filter(Compra.monto.like('%' + palabra + '%'), Compra.cosecha_id==cosecha_id)
        observacion = Compra.query.filter(Compra.observacion.like('%' + palabra + '%'), Compra.cosecha_id==cosecha_id)
        compras = fecha.union(clase_cacao, precio, cantidad, humedad, merma_porcentaje, merma_kg, cantidad_total, monto, observacion)

        tmp = Recolector.query.filter(Recolector.ci.like('%' + palabra + '%')).first()
        if tmp is not None:
            prod = Compra.query.filter(Compra.recolector_id.like('%' + str(tmp.id) + '%'), Compra.cosecha_id==cosecha_id)
            compras = compras.union(prod)

        tmp = TipoRecolector.query.filter(TipoRecolector.descripcion.like('%' + palabra + '%')).first()
        if tmp is not None:
            cmp = Compra.query.filter(Compra.recolector_id.like('%' + str(tmp.id) + '%'), Compra.cosecha_id==cosecha_id)
            compras = compras.union(cmp)    
    
    total_cantidad = sum(compra.cantidad_total for compra in compras)
    total_monto = sum(compra.monto for compra in compras)
    hide = True if tipo == "listar" else False
    return render_template('compras.html', error=error, cosecha=cosecha, compras=compras, 
                            total_cantidad=total_cantidad, total_monto=total_monto, hide=hide) 

# Borrar datos de compra
@app.route('/cosecha/<cosecha_id>/compras/<compra_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_compra(cosecha_id, compra_id):
    # Verificar que la cosecha exista en la base de datos o esté habilitada
    cosecha = Cosecha.query.filter_by(id=cosecha_id).first()
    error = verificar_cosecha_exists(cosecha_id, "compras", cosecha)
    if error is not None:
        cosechas = Cosecha.query.all()
        return render_template('cosecha.html', error=error, cosechas=cosechas) 

    compra_to_delete = Compra.query.get_or_404(compra_id)
    if request.method == "POST":
        try:
            db.session.delete(compra_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('compras', cosecha_id=cosecha_id, tipo="compras"))
        except:
            error = "Hubo un error borrando la cosecha."
    
    return redirect(url_for('compras', cosecha_id=cosecha_id, tipo="compras"))

# Editar datos de compra
@app.route('/cosecha/<cosecha_id>/compras/<compra_id>/update', methods=['GET', 'POST'])
@login_required
def update_compra(cosecha_id, compra_id):
    error=None
    tipo_prod = TipoRecolector.query.all()
    compras = Compra.query.filter_by(cosecha_id=cosecha_id).all()
    recolectores = Recolector.query.all()

    # Verificar que la cosecha exista en la base de datos o esté habilitada
    cosecha = Cosecha.query.filter_by(id=cosecha_id).first()
    error = verificar_cosecha_exists(cosecha_id, "compras", cosecha)
    if error is not None:
        cosechas = Cosecha.query.all()
        return render_template('cosecha.html', error=error, cosechas=cosechas) 

    # Verificar que la compra exista en la base de datos
    compra = Compra.query.filter_by(id=compra_id).first()
    if compra is None:
        error = "La compra no se encuentra registrada."
        return render_template('compras.html', error=error, cosecha=cosecha, compras=compras, tipo_prod=tipo_prod, recolectores=recolectores)

    if request.method == "POST":
        try:
            compra.clase_cacao = request.form['clase_cacao']
            compra.precio = request.form.get('precio', type=float)
            compra.cantidad = request.form.get('cantidad', type=float)
            compra.humedad = request.form.get('humedad', type=float)
            compra.merma_porcentaje = request.form.get('merma_porcentaje', type=float)
            compra.merma_kg = request.form.get('merma_kg', type=float)
            compra.cantidad_total = request.form.get('cantidad_total', type=float)
            compra.monto = request.form.get('monto', type=float)
            compra.observacion = request.form['observacion']

            db.session.commit()
            flash('Se ha actualizado exitosamente.')
            return redirect(url_for('compras', id=cosecha_id))
        except:
            error = "Hubo un error actualizando la cosecha."
    
    total_cantidad = sum(compra.cantidad_total for compra in compras)
    total_monto = sum(compra.monto for compra in compras)
    return render_template('compras.html', error=error, cosecha=cosecha, compras=compras, 
                            total_cantidad=total_cantidad, total_monto=total_monto)
