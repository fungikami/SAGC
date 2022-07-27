from flask import session, flash, redirect, url_for, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from src.models import Usuario
from src.verificadores import verificar_contrasena
from src.decoradores import logout_required, login_required

@app.route("/login", methods=['GET', 'POST'])
@logout_required
def login():
    """ Página de inicio de sesión """

    error = None 
    if request.method == 'POST':
        nombre_usuario, password = request.form['nombre_usuario'], request.form['password']
        user = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()

        if user is not None and (check_password_hash(user.password, password) or password == user.password):
            session['logged_in'] = True
            session['usuario'] = "Usuario: " + user.nombre_usuario + ", ID: " + str(user.id)
            flash('Se ha iniciado la sesion exitosamente')

            # Agregar configuración administrador y analista
            session['rol_admin'], session['rol_analyst'] = False, False
            if user.rols.nombre == "Administrador":
                session['rol_admin'] = True
                return redirect(url_for('perfiles'))

            if user.rols.nombre == "Analista de Ventas":
                session['rol_analyst'] = True
                return redirect(url_for('recolector')) 

            if user.rols.nombre == "Gerente":
                session['rol_gerente'] = True
                return redirect(url_for('cosecha'))

            return redirect(url_for('cosecha'))
        else:
            error = 'Credenciales invalidas'
            
    return render_template("login.html", error=error)

@app.route('/login/update_password/', methods=['GET', 'POST'])
@logout_required
def update_password():
    """ Cambiar contraseña """

    error = None 
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        new_password = request.form['npassword']
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
            
    return render_template("update_password.html", error=error)

@app.route('/logout')
@login_required
def logout():
    """ Cerrar sesión """
    
    session.pop('rol_admin', default=None)
    session.pop('logged_in', None)
    flash('Se ha cerrado la sesion')
    return redirect(url_for('home'))