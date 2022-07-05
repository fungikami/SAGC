from email.policy import default
from __init__ import db
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
    descripcion = db.Column(db.String(120), unique=True)
    inicio = db.Column(db.DateTime, nullable=False)
    cierre = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.Boolean, default=True)

    # Una cosecha tiene compras
    compras = db.relationship('Compra', backref='cosechas')

    def __repr__(self):
        return f"Cosecha('{self.descripcion}')"

# Modelo de tipos de recolectores
class TipoRecolector(db.Model):
    __tablename__ = 'tipo_prod'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(120), nullable=False, unique=True)
    precio = db.Column(db.Float, nullable=False)
    
    # backref: crea una propiedad/columna en Recolector que se llama tipo_recolector, si se pone el mismo nombre de la tabla da error
    producer = db.relationship('Recolector', backref='tipo_recolector', lazy=True)

    # Un tipo de recolector tiene compras
    #compras = db.relationship('Compra', backref='tipo_prod', lazy=True)

    def __repr__(self):
        return f"TipoRecolector('{self.descripcion}')"

# Modelo de recolectores
class Recolector(db.Model):
    __tablename__ = 'recolectores'

    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.String(30), nullable=False, unique=True)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(12), nullable=False)
    celular = db.Column(db.String(12), nullable=False)
    tipo_prod = db.Column(db.Integer, db.ForeignKey('tipo_prod.id'), nullable=False) # ForeignKey debe estar el nombre de la tabla a linkear
    direccion1= db.Column(db.String(120), nullable=False)
    direccion2 = db.Column(db.String(120))

    # Un recolector tiene compras
    compras = db.relationship('Compra', backref='recolectores')

    def __repr__(self):
        return f"Recolector('{self.ci}', '{self.nombre}', '{self.apellido}', '{self.telefono}', '{self.celular}', '{self.tipo_prod}', '{self.direccion1}', '{self.direccion2}')"

# Modelo de Compras
class Compra(db.Model):
    __tablename__ = 'compras'

    id = db.Column(db.Integer, primary_key=True)

    # Asociado a una cosecha. Una cosecha puede tener varias compras, una compra es de una cosecha
    cosecha_id = db.Column(db.Integer, db.ForeignKey('cosechas.id'), nullable=False)

    # Asociado a un recolector. Un recolector puede tener varias compras, una compra es un recolector
    recolector_id = db.Column(db.Integer, db.ForeignKey('recolectores.id'), nullable=False)

    # Asociado a un tipo de recolector
    #tipo_recolector = db.Column(db.Integer, db.ForeignKey('tipo_prod.id'), nullable=False)

    fecha = db.Column(db.DateTime, nullable=False)
    clase_cacao = db.Column(db.String(120), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    humedad = db.Column(db.Float, nullable=False)
    merma_porcentaje = db.Column(db.Float, nullable=False)
    merma_kg = db.Column(db.Float, nullable=False)
    cantidad_total = db.Column(db.Float, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    observacion = db.Column(db.String(120))

    def __repr__(self):
        return f"Compra('{self.cosecha_id}', '{self.recolector_id}', '{self.tipo_recolector}', '{self.fecha}', '{self.clase_cacao}', '{self.precio}', '{self.cantidad}', '{self.humedad}', '{self.merma_porcentaje}', '{self.merma_kg}', '{self.cantidad_total}', '{self.monto}', '{self.observacion}')"
