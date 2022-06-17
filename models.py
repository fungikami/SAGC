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
class Productor(db.Model):
    __tablename__ = 'productores'

    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    telephone = db.Column(db.String(12), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    #type_prod = db.Column(db.Integer, db.ForeignKey('type_prod.id'), nullable=False)
    type_prod = db.Column(db.String(20), nullable=False)
    direction1= db.Column(db.String(120), nullable=False)
    direction2 = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"Productor('{self.ci}', '{self.name}', '{self.surname}', '{self.telephone}', '{self.phone}', '{self.type_prod}', '{self.direction1}', '{self.direction2}')"

class TypeProductor(db.Model):
    __tablename__ = 'type_prod'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False, unique=True)
    #productor = db.relationship('Productor', backref='type_productor', lazy=True)

    def __repr__(self):
        return f"Productor('{self.description}')"