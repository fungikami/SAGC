from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# Configuracion (aplicación y database)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'unaclavesecreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from src.decoradores import login_required
from src.home import *
from src.cosechas import *
from src.perfiles import *
from src.recolector import *
from src.tipo_recolector import *
from src.compras import *

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