from flask import session, flash, redirect, url_for, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import app, db
from models import Usuario
from verificadores import verificar_contrasena
from decoradores import logout_required, login_required

#----------------------------------------------------------------------------------------------------------------------
# Página de inicio de sesión
@app.route("/login", methods=['GET', 'POST'])
@logout_required
def login():
    error = None 
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']

        if nombre_usuario != '' and password != '':
            user = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
            
            if user is not None and (check_password_hash(user.password, password) or password == user.password):
                session['logged_in'] = True
                flash('Se ha iniciado la sesion exitosamente')

                # Agregar configuración administrador y analista
                session['rol_admin'] = False
                session['rol_analyst'] = False
                if user.rols.nombre == "Administrador":
                    session['rol_admin'] = True
                    return redirect(url_for('perfiles'))

                if user.rols.nombre == "Analista de Ventas":
                    session['rol_analyst'] = True
                    return redirect(url_for('recolector')) 
            else:
                error = 'Credenciales invalidas'
        else:
            error = 'Todos los campos son obligatorios'
            
    return render_template("login.html", error=error)

# Cambiar contraseña
@app.route('/login/update_password/', methods=['GET', 'POST'])
@logout_required
def update_password():
    error = None 
    if request.method == 'POST':

        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        new_password = request.form['npassword']

        if nombre_usuario != '' and password != '':
            user = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
            
            if user is not None and (check_password_hash(user.password, password) or password == user.password):
                userID = user.id
                user_to_update = Usuario.query.get_or_404(userID)

                error = verificar_contrasena(new_password)
                if error is not None:
                    return render_template("update_password.html", error=error)  

                user_to_update.password = generate_password_hash(new_password, "sha256")

                try:
                    db.session.commit()
                    flash('La contraseña se ha modificado exitosamente.')
                    return redirect(url_for('login'))
                except:
                    error = 'No se pudo modificar la contraseña.'
                    return render_template("update_password.html", error=error)     
            else:
                error = 'Credenciales invalidas'
        else:
            error = 'Todos los campos son obligatorios'
            
    return render_template("update_password.html", error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('rol_admin', default=None)
    session.pop('logged_in', None)
    flash('Se ha cerrado la sesion')
    return redirect(url_for('home'))