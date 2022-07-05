from flask import session, flash, redirect, url_for
from functools import wraps

# Decorador de login requerido (para hacer logout hay que estar login)
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Necesitas iniciar sesión primero')
            return redirect(url_for('login'))
    return wrap

# Decorador de logout requerido (para no poder entrar a login una vez ya estás loggeado)
def logout_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            flash('No puedes loggearte una vez estás dentro.') #cambiar mensaje
            if (session['rol_admin']):
                return redirect(url_for('perfiles'))
            return redirect(url_for('recolector'))
        else:
            return f(*args, **kwargs)
    return wrap

# Decorador de Administrador requerido
def admin_only(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'rol_admin' in session and session['rol_admin'] == True:
            return f(*args, **kwargs)
        else:
            flash("Debes ser administrador para ver 'Perfiles de Usuarios'.")
            return redirect(url_for('recolector'))

    return wrap

# Decorador de Analista de Ventas requerido
def analyst_only(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'rol_analyst' in session and session['rol_analyst'] == True:
            return f(*args, **kwargs)
        else:
            flash("Debes ser Analista de Ventas para acceder 'Datos del Recolector y Tipos de Recolector'.")
            return redirect(url_for('perfiles'))

    return wrap