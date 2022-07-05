from flask import render_template
from __init__ import app
from decoradores import login_required
from home import *
from cosechas import *
from perfiles import *
from recolector import *
from tipo_recolector import *
import compras


#----------------------------------------------------------------------------------------------------------------------
# Página principal (no requiere iniciar sesión)
@app.route("/")
def home():
    return render_template("home.html")

#----------------------------------------------------------------------------------------------------------------------
# Logger de Eventos (requiere iniciar sesión)
@app.route('/eventos')
@login_required
def eventos():
    return render_template('eventos.html')

if __name__ == '__main__':
    app.run(debug=True)