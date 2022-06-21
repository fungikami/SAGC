from flask.sessions import NullSession
from app import db

# Crear modelo de usuario (python db_create_user.py)

# Modelo de roles
class Rol(db.Model):
    __tablename__ = 'rols'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    user = db.relationship('Usuario', backref='rols', lazy=True)

    def __repr__(self):
        return f"Rol('{self.name}')"

user_cosecha = db.Table('user_cosecha',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')),
    db.Column('cosecha_id', db.Integer, db.ForeignKey('cosechas.id', ondelete='CASCADE'))
)

# Modelo de usuarios
class Usuario(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    rol = db.Column(db.Integer, db.ForeignKey('rols.id'), nullable=False)
    cosechas = db.relationship('Cosecha', secondary=user_cosecha, backref='users', lazy=True)

    def __repr__(self):
        return f"Usuario('{self.username}', '{self.name}', '{self.surname}', '{self.password}', '{self.rol}')"

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
        return f"Productor('{self.descripcion}')"

# Modelo de productores
class Productor(db.Model):
    __tablename__ = 'producers'

    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    telephone = db.Column(db.String(12), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    tipo_prod = db.Column(db.Integer, db.ForeignKey('tipo_prod.id'), nullable=False) # ForeignKey debe estar el nombre de la tabla a linkear
    #tipo_prod = db.Column(db.String(20), nullable=False)
    direction1= db.Column(db.String(120), nullable=False)
    direction2 = db.Column(db.String(120))

    def __repr__(self):
        return f"Productor('{self.ci}', '{self.name}', '{self.surname}', '{self.telephone}', '{self.phone}', '{self.tipo_prod}', '{self.direction1}', '{self.direction2}')"