from flask import flash, redirect, url_for, request, render_template
from app import app, db
from src.decoradores import login_required, analyst_only
from src.models import TipoRecolector
from src.verificadores import verificar_tipo_recolector

#----------------------------------------------------------------------------------------------------------------------------
# Tipos de Recolector (requiere iniciar sesión)
@app.route('/tipo_recolector', methods=['GET', 'POST'])
@login_required
@analyst_only
def tipo_recolector():
    error=None
    tipo_prod = TipoRecolector.query.all()

    if request.method == 'POST':
        error = verificar_tipo_recolector(request.form, TipoRecolector)
        if error is not None:
            return render_template("tipo_recolector.html", error=error, tipo_prod=tipo_prod) 

        try:
            descripcion, precio = request.form['descripcion'], request.form['precio']
            new_type = TipoRecolector(descripcion=descripcion, precio=precio)
            db.session.add(new_type)
            db.session.commit()
            flash('Se ha registrado exitosamente.')
            return redirect(url_for('tipo_recolector'))
        except:
            error = 'No se pudo guardar el tipo de recolector en la base de datos'
            
    return render_template("tipo_recolector.html", error=error, tipo_prod=tipo_prod) 

# Actualizar datos de /tipo_recolector
@app.route('/tipo_recolector/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_tipo_recolector(id):
    error=None
    tipo_prod = TipoRecolector.query.all()
    tipo = TipoRecolector.query.get_or_404(id)

    if request.method == "POST":
        error = verificar_tipo_recolector(request.form, TipoRecolector, tipo)
        if error is not None:
            return render_template("tipo_recolector.html", error=error, tipo_prod=tipo_prod) 

        try:
            tipo.descripcion = request.form['descripcion']
            tipo.precio = request.form['precio']
            db.session.commit()
            flash('Se ha modificado exitosamente.')
            return redirect(url_for('tipo_recolector'))
        except:
            error = 'No se pudo actualizar el tipo de recolector.'
    
    return render_template("tipo_recolector.html", error=error, tipo_prod=tipo_prod) 

# Borrar datos de /tipo_recolector
@app.route('/tipo_recolector/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_tipo_recolector(id):
    error=None
    tipo_prod = TipoRecolector.query.all()
    tipo = TipoRecolector.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(tipo)
            db.session.commit()
            flash('Se ha eliminado exitosamente.')
            return redirect(url_for('tipo_recolector'))
        except:
            return "Hubo un error eliminando el tipo de recolector."

    return render_template("tipo_recolector.html", error=error, tipo_prod=tipo_prod)

# Search Bar Tipo Recolector
@app.route('/tipo_recolector/search', methods=['GET', 'POST'])
@login_required
def search_tipo_recolector():
    tipo_prod = []

    if request.method == "POST":
        palabra = request.form['search_tipo_recolector']
        tipo_prod = TipoRecolector.query.filter(TipoRecolector.descripcion.like('%' + palabra + '%'))
        
    return render_template("/tipo_recolector.html", tipo_prod=tipo_prod) 