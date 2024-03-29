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
    financias = Financia.query.filter_by(cosecha_id=cosecha_id).all()
    hide = True if tipo == "listar" else False
    
    # Verificar que la cosecha exista en la base de datos o esté habilitada
    cosecha = Cosecha.query.filter_by(id=cosecha_id).first()
    error = verificar_cosecha_exists(cosecha_id, "compras", cosecha)
    if error is not None:
        cosechas = Cosecha.query.all()
        return render_template('cosecha.html', error=error, cosechas=cosechas)
    
    if request.method == "POST":
        # Verifica que el recolector esté en la base de datos
        cedula = request.form['cedula']
        recolector = Recolector.query.filter_by(ci=cedula).first()

        if recolector is None:
            tipo_recolector = TipoRecolector.query.all()
            error = "El recolector no se encuentra registrado. Registre el recolector antes de agregar el financiamiento"
            return render_template("recolector.html", error=error, tipo_prod=tipo_recolector, recolector=recolectores) 

        # Verifica que la fecha de vencimiento no sea menor a la fecha actual
        fecha = datetime.datetime.now()
        y, m, d = request.form['vencimiento'].split('-')
        fecha_vencimiento = datetime.datetime(int(y), int(m), int(d))
        if fecha_vencimiento < fecha:
            error = "La fecha de vencimiento no puede ser menor a la fecha actual"
            return render_template("financias.html", error=error, cosecha=cosecha, 
                recolectores=recolectores, financias=financias, hide=hide)

        try:
            letra_cambio = request.form['letra_cambio']
            monto = request.form['monto']
            pago_respuesta = request.form['pago']
            pago = True if pago_respuesta == "Sí" else False
            observacion = request.form['observacion']

            financia = Financia(cosechas=cosecha, recolectores=recolector, fecha=fecha,
                            letra_cambio=letra_cambio, fecha_vencimiento=fecha_vencimiento,
                            monto=monto, pago=pago, observacion=observacion)

            evento_user = session['usuario']
            operacion = 'Agregar Financiamiento'
            modulo = 'Financia'
            evento_desc = str(financia)
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            # Agregar credito al banco
            if pago == True:
                nro_financia = Financia.query.count()
                concepto = 'Crédito para compras'
                transaccion = Banco(fecha=fecha, concepto=concepto, monto=monto, financia_id=nro_financia, credito=True)
                db.session.add(transaccion)

            db.session.add(evento)
            db.session.add(financia)
            db.session.commit()

            flash('Se ha registrado exitosamente.')
            return redirect(url_for('financias', cosecha_id=cosecha_id, tipo=tipo))    
        except:
            error = "Hubo un error agregando el financiamiento."

    total_recolectores = Financia.query.filter().group_by(Financia.recolector_id).filter_by(cosecha_id=cosecha_id).count()
    total_fin_cancelados = Financia.query.filter(Financia.pago == True).filter_by(cosecha_id=cosecha_id).count()
    total_fin_no_cancelados = Financia.query.filter(Financia.pago == False).filter_by(cosecha_id=cosecha_id).count()
    total_fin_plazo_vencido = Financia.query.filter(Financia.fecha_vencimiento < datetime.datetime.now()).filter_by(cosecha_id=cosecha_id).count()
    total_monto_cancelado = sum(financia.monto for financia in financias if financia.pago == True)
    total_monto_no_cancelado = sum(financia.monto for financia in financias if financia.pago == False)
    total_financiamiento = sum(financia.monto for financia in financias)

    return render_template('financias.html', error=error, cosecha=cosecha, recolectores=recolectores, financias=financias,
            hide=hide, total_recolectores=total_recolectores, total_fin_cancelados=total_fin_cancelados,
            total_fin_no_cancelados=total_fin_no_cancelados, total_fin_plazo_vencido=total_fin_plazo_vencido,
            total_monto_cancelado=total_monto_cancelado, total_monto_no_cancelado=total_monto_no_cancelado,
            total_financiamiento=total_financiamiento)

@app.route("/cosecha/<cosecha_id>/financias/<tipo>/search", methods=['GET', 'POST'])
@login_required
def search_financias(cosecha_id, tipo):
    """ Mostrar financiamientos buscados """
    error = None
    financias = []

    # Verificar que la cosecha exista en la base de datos o esté habilitada
    cosecha = Cosecha.query.filter_by(id=cosecha_id).first()
    error = verificar_cosecha_exists(cosecha_id, tipo, cosecha)
    if error is not None:
        cosechas = Cosecha.query.all()
        return render_template('cosecha.html', error=error, cosechas=cosechas) 
    
    if request.method == "POST":
        financias_desde, financias_hasta = Financia.query.filter_by(cosecha_id=cosecha_id), Financia.query.filter_by(cosecha_id=cosecha_id)
        fecha_inicio, fecha_fin = request.form['Desde'], request.form['Hasta']
        if (fecha_inicio != ''):
            financias_desde = Financia.query.filter(Financia.fecha >= fecha_inicio, Financia.cosecha_id==cosecha_id)
        if (fecha_fin != ''):
            financias_hasta = Financia.query.filter(Financia.fecha <= fecha_fin, Financia.cosecha_id==cosecha_id)
            
        # Intersecta las dos tablas de financias_desde y financias_hasta
        financias_fecha = financias_desde.intersect(financias_hasta)

        palabra = request.form['search_financia']
        fecha = Financia.query.filter(Financia.fecha.like('%' + palabra + '%'), Financia.cosecha_id==cosecha_id)
        letra_cambio = Financia.query.filter(Financia.letra_cambio.like('%' + palabra + '%'), Financia.cosecha_id==cosecha_id)
        fecha_vencimiento = Financia.query.filter(Financia.fecha_vencimiento.like('%' + palabra + '%'), Financia.cosecha_id==cosecha_id)
        monto = Financia.query.filter(Financia.monto.like('%' + palabra + '%'), Financia.cosecha_id==cosecha_id)
        pago = Financia.query.filter(Financia.pago.like('%' + palabra + '%'), Financia.cosecha_id==cosecha_id)
        observacion = Financia.query.filter(Financia.observacion.like('%' + palabra + '%'), Financia.cosecha_id==cosecha_id)
        financias = letra_cambio.union(fecha_vencimiento, letra_cambio, monto, pago, observacion, fecha)

        # Hacer búsqueda por recolector 
        tmp = Recolector.query.filter(Recolector.ci.like('%' + palabra + '%')).first()
        if tmp is not None:
            fin = Financia.query.filter(Financia.recolector_id.like('%' + str(tmp.id) + '%'), Financia.cosecha_id==cosecha_id)
            financias = financias.union(fin)

        tmp = Recolector.query.filter(Recolector.nombre.like('%' + palabra + '%')).first()
        if tmp is not None:
            fin = Financia.query.filter(Financia.recolector_id.like('%' + str(tmp.id) + '%'), Financia.cosecha_id==cosecha_id)
            financias = financias.union(fin)

        tmp = Recolector.query.filter(Recolector.apellido.like('%' + palabra + '%')).first()
        if tmp is not None:
            fin = Financia.query.filter(Financia.recolector_id.like('%' + str(tmp.id) + '%'), Financia.cosecha_id==cosecha_id)
            financias = financias.union(fin)

        tmp = Recolector.query.filter(Recolector.telefono.like('%' + palabra + '%')).first()
        if tmp is not None:
            fin = Financia.query.filter(Financia.recolector_id.like('%' + str(tmp.id) + '%'), Financia.cosecha_id==cosecha_id)
            financias = financias.union(fin)

        tmp = Recolector.query.filter(Recolector.celular.like('%' + palabra + '%')).first()
        if tmp is not None:
            fin = Financia.query.filter(Financia.recolector_id.like('%' + str(tmp.id) + '%'), Financia.cosecha_id==cosecha_id)
            financias = financias.union(fin)

        tmp = Recolector.query.filter(Recolector.direccion1.like('%' + palabra + '%')).first()
        if tmp is not None:
            fin = Financia.query.filter(Financia.recolector_id.like('%' + str(tmp.id) + '%'), Financia.cosecha_id==cosecha_id)
            financias = financias.union(fin)

        tmp = Recolector.query.filter(Recolector.direccion2.like('%' + palabra + '%')).first()
        if tmp is not None:
            fin = Financia.query.filter(Financia.recolector_id.like('%' + str(tmp.id) + '%'), Financia.cosecha_id==cosecha_id)
            financias = financias.union(fin)

        tmp = TipoRecolector.query.filter(TipoRecolector.descripcion.like('%' + palabra + '%')).first()
        if tmp is not None:
            fin = Financia.query.filter(Financia.recolector_id.like('%' + str(tmp.id) + '%'), Financia.cosecha_id==cosecha_id)
            financias = financias.union(fin)

        financias = financias_fecha.intersect(financias)

    total_recolectores = Financia.query.filter().group_by(Financia.recolector_id).count()
    total_fin_cancelados = Financia.query.filter(Financia.pago == True).count()
    total_fin_no_cancelados = Financia.query.filter(Financia.pago == False).count()
    total_fin_plazo_vencido = Financia.query.filter(Financia.fecha_vencimiento < datetime.datetime.now()).count()
    total_monto_cancelado = sum(financia.monto for financia in financias if financia.pago == True)
    total_monto_no_cancelado = sum(financia.monto for financia in financias if financia.pago == False)
    total_financiamiento = sum(financia.monto for financia in financias)

    hide = True if tipo == "listar" else False
    return render_template('financias.html', error=error, cosecha=cosecha, financias=financias,
            hide=hide, total_recolectores=total_recolectores, total_fin_cancelados=total_fin_cancelados,
            total_fin_no_cancelados=total_fin_no_cancelados, total_fin_plazo_vencido=total_fin_plazo_vencido,
            total_monto_cancelado=total_monto_cancelado, total_monto_no_cancelado=total_monto_no_cancelado,
            total_financiamiento=total_financiamiento)

@app.route("/cosecha/<cosecha_id>/financias/<financias_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_financias(cosecha_id, financias_id):
    """ Borrar datos de financiamiento """
    
    # Verificar que la cosecha exista en la base de datos o esté habilitada
    cosecha = Cosecha.query.filter_by(id=cosecha_id).first()
    error = verificar_cosecha_exists(cosecha_id, "compras", cosecha)
    if error is not None:
        cosechas = Cosecha.query.all()
        return render_template('cosecha.html', error=error, cosechas=cosechas)

    financia_to_delete = Financia.query.get_or_404(financias_id)
    if request.method == "POST":
        try:
            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Eliminar Financiamiento'
            modulo = 'Financia'
            evento_desc = str(financia_to_delete)
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            transaccion_to_delete = Banco.query.filter_by(financia_id=financias_id).first()

            db.session.add(evento)
            db.session.delete(transaccion_to_delete)
            db.session.delete(financia_to_delete)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('financias', cosecha_id=cosecha_id, tipo="generar"))
        except:
            error = "Hubo un error borrando la cosecha."

    return redirect(url_for('financias', cosecha_id=cosecha_id, tipo="generar"))

@app.route("/cosecha/<cosecha_id>/financias/<financias_id>/update", methods=['GET', 'POST'])
@login_required
def update_financias(cosecha_id, financias_id):

    """ Actualizar datos de financiamiento """
    error=None
    recolectores = Recolector.query.all()
    financias = Financia.query.all()

    # Verificar que la cosecha exista en la base de datos o esté habilitada
    cosecha = Cosecha.query.filter_by(id=cosecha_id).first()
    error = verificar_cosecha_exists(cosecha_id, 'generar', cosecha)
    if error is not None:
        cosechas = Cosecha.query.all()
        return render_template('cosecha.html', error=error, cosechas=cosechas)

    # Verificar que el financiamiento exista en la base de datos
    financia = Financia.query.filter_by(id=financias_id).first()
    if financia is None:
        error = "El financiamiento no se encuentra registrado en la base de datos."
        return render_template('financias.html', error=error, cosecha=cosecha, recolectores=recolectores, financias=financias)
    
    if request.method == "POST":
        try:
            evento_desc = str(financia)
            financia.letra_cambio = request.form['letra_cambio']
            y, m, d = request.form['vencimiento'].split('-')
            financia.fecha_vencimiento = datetime.datetime(int(y), int(m), int(d))
            financia.monto = request.form['monto']
            pago_respuesta = request.form['pago']
            financia.pago = True if pago_respuesta == "Si" else False
            financia.observacion = request.form['observacion']

            fecha = datetime.datetime.now()
            evento_user = session['usuario']
            operacion = 'Editar Financiamiento'
            modulo = 'Financia'
            evento_desc += ";" + str(financia)
            evento = Evento(usuario=evento_user, evento=operacion, modulo=modulo, fecha=fecha, descripcion=evento_desc)

            # Eliminar credito del banco si se modifica a no pagado
            if not financia.pago:
                transaccion_to_delete = Banco.query.filter_by(financia_id=financia.id).first()
                if transaccion_to_delete is not None:
                    db.session.delete(transaccion_to_delete)
                    db.session.commit()

            # Agregar credito al banco si se modifica a pagado        
            else:
                concepto = 'Crédito para compras'
                transaccion = Banco(fecha=fecha, concepto=concepto, monto=financia.monto, financia_id=financia.id, credito=True)
                db.session.add(transaccion)

            db.session.add(evento)
            db.session.commit()
            flash('Se ha actualizado exitosamente.')
            return redirect(url_for('financias', cosecha_id=cosecha_id, tipo='generar'))    
        except:
            error = "Hubo un error actualizando el financiamiento."

    total_recolectores = Financia.query.filter().group_by(Financia.recolector_id).count()
    total_fin_cancelados = Financia.query.filter(Financia.pago == True).count()
    total_fin_no_cancelados = Financia.query.filter(Financia.pago == False).count()
    total_fin_plazo_vencido = Financia.query.filter(Financia.fecha_vencimiento < datetime.datetime.now()).count()
    total_monto_cancelado = sum(financia.monto for financia in financias if financia.pago == True)
    total_monto_no_cancelado = sum(financia.monto for financia in financias if financia.pago == False)
    total_financiamiento = sum(financia.monto for financia in financias)

    hide = False
    return render_template('financias.html', error=error, cosecha=cosecha, recolectores=recolectores, financias=financias,
            hide=hide, total_recolectores=total_recolectores, total_fin_cancelados=total_fin_cancelados,
            total_fin_no_cancelados=total_fin_no_cancelados, total_fin_plazo_vencido=total_fin_plazo_vencido,
            total_monto_cancelado=total_monto_cancelado, total_monto_no_cancelado=total_monto_no_cancelado,
            total_financiamiento=total_financiamiento)