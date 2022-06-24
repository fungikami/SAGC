from flask.sessions import NullSession
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# Crear modelo de usuario (python db_create_user.py)

# Modelo de roles
class Rol(db.Model):
    __tablename__ = 'rols'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False, unique=True)
    user = db.relationship('Usuario', backref='rols', lazy=True)

    def __repr__(self):
        return f"Rol('{self.nombre}')"

user_cosecha = db.Table('user_cosecha',
    db.Column('user_id', db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE')),
    db.Column('cosecha_id', db.Integer, db.ForeignKey('cosechas.id', ondelete='CASCADE'))
)

# Modelo de usuarios
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(20), nullable=False, unique=True)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    rol = db.Column(db.Integer, db.ForeignKey('rols.id'), nullable=False)
    cosechas = db.relationship('Cosecha', secondary=user_cosecha, backref='usuarios', lazy=True)

    #@property
    #def password(self):
	#    raise AttributeError('La contraseña no es un atributo legible.')

    #@password.setter
    #def password(self, password):
	#    self.password = generate_password_hash(password)

    #def verify_password(self, password):
	#    return check_password_hash(self.password, password)

    def __repr__(self):
        return f"Usuario('{self.nombre_usuario}', '{self.nombre}', '{self.apellido}', '{self.password}', '{self.rol}')"

# Modelo de cosechas
class Cosecha(db.Model):
    __tablename__ = 'cosechas'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return f"Cosecha('{self.date}')"

# Modelo de tipos de productores
class TipoProductor(db.Model):
    __tablename__ = 'tipo_prod'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(120), nullable=False, unique=True)
    # backref: crea una propiedad/columna en Productor que se llama tipo_productor, si se pone el mismo nombre de la tabla da error
    producer = db.relationship('Productor', backref='tipo_productor', lazy=True)

    def __repr__(self):
        return f"TipoProductor('{self.descripcion}')"

# Modelo de productores
class Productor(db.Model):
    __tablename__ = 'productores'

    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.String(30), nullable=False, unique=True)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(12), nullable=False)
    celular = db.Column(db.String(12), nullable=False)
    tipo_prod = db.Column(db.Integer, db.ForeignKey('tipo_prod.id'), nullable=False) # ForeignKey debe estar el nombre de la tabla a linkear
    #tipo_prod = db.Column(db.String(20), nullable=False)
    direccion1= db.Column(db.String(120), nullable=False)
    direccion2 = db.Column(db.String(120))

    def __repr__(self):
        return f"Productor('{self.ci}', '{self.nombre}', '{self.apellido}', '{self.telefono}', '{self.celular}', '{self.tipo_prod}', '{self.direccion1}', '{self.direccion2}')"