from flask.sessions import NullSession
from app import db

# Crear modelo de usuario (python db_create_user.py)
class Rol(db.Model):
    __tablename__ = 'rols'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    user = db.relationship('User', backref='rols', lazy=True)

    def __repr__(self):
        return f"Rol('{self.name}')"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    rol = db.Column(db.Integer, db.ForeignKey('rols.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.name}', '{self.surname}', '{self.password}', '{self.rol}')"
class TypeProducer(db.Model):
    __tablename__ = 'type_prod'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False, unique=True)
    # backref: crea una propiedad/columna en Producer que se llama type_producer, si se pone el mismo nombre de la tabla da error
    producer = db.relationship('Producer', backref='type_producer', lazy=True)

    def __repr__(self):
        return f"Producer('{self.description}')"

class Producer(db.Model):
    __tablename__ = 'producers'

    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    telephone = db.Column(db.String(12), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    type_prod = db.Column(db.Integer, db.ForeignKey('type_prod.id'), nullable=False) # ForeignKey debe estar el nombre de la tabla a linkear
    #type_prod = db.Column(db.String(20), nullable=False)
    direction1= db.Column(db.String(120), nullable=False)
    direction2 = db.Column(db.String(120))

    def __repr__(self):
        return f"Producer('{self.ci}', '{self.name}', '{self.surname}', '{self.telephone}', '{self.phone}', '{self.type_prod}', '{self.direction1}', '{self.direction2}')"