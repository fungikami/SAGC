from app import db

class Rol(db.Model):
    """ Modelo de roles """
    __tablename__ = 'rols'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False, unique=True)
    user = db.relationship('Usuario', backref='rols', lazy=True)

    def __repr__(self):
        return f"Rol('{self.nombre}')"

# Enlace de la tabla rols con la tabla usuarios
user_cosecha = db.Table('user_cosecha',
    db.Column('user_id', db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE')),
    db.Column('cosecha_id', db.Integer, db.ForeignKey('cosechas.id', ondelete='CASCADE'))
)

class Usuario(db.Model):
    """ Modelo de usuarios """
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(20), nullable=False, unique=True)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    rol = db.Column(db.Integer, db.ForeignKey('rols.id'), nullable=False)
    cosechas = db.relationship('Cosecha', secondary=user_cosecha, backref='usuarios', lazy=True)

    def __repr__(self):
        return f"Usuario('{self.nombre_usuario}', '{self.nombre}', '{self.apellido}', '{self.rol}')"

class Cosecha(db.Model):
    """ Modelo de cosechas """
    __tablename__ = 'cosechas'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(120), unique=True)
    inicio = db.Column(db.DateTime, nullable=False)
    cierre = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.Boolean, default=True)
    compras = db.relationship('Compra', backref='cosechas')
    financias = db.relationship('Financia', backref='cosechas')

    def __repr__(self):
        return f"Cosecha('{self.descripcion}', '{self.inicio}', '{self.cierre}')"

class TipoRecolector(db.Model):
    """ Modelo de tipos de recolectores """
    __tablename__ = 'tipo_prod'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(120), nullable=False, unique=True)
    precio = db.Column(db.Float, nullable=False)
    producer = db.relationship('Recolector', backref='tipo_recolector', lazy=True)

    def __repr__(self):
        return f"TipoRecolector('{self.descripcion}', '{self.precio}')"

class Recolector(db.Model):
    """ Modelo de recolectores """
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
    compras = db.relationship('Compra', backref='recolectores')
    financias = db.relationship('Financia', backref='recolectores')

    def __repr__(self):
        return f"Recolector('{self.ci}', '{self.nombre}', '{self.apellido}', '{self.telefono}', '{self.celular}', '{self.tipo_recolector.descripcion}', '{self.direccion1}', '{self.direccion2}')"

class Compra(db.Model):
    """ Modelo de compras """
    __tablename__ = 'compras'

    id = db.Column(db.Integer, primary_key=True)
    cosecha_id = db.Column(db.Integer, db.ForeignKey('cosechas.id'), nullable=False)
    recolector_id = db.Column(db.Integer, db.ForeignKey('recolectores.id'), nullable=False)
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
    almendra = db.Column(db.Boolean, default=False)     # True si es verde

    def __repr__(self):
        return f"Compra('{self.cosechas.descripcion}', '{self.fecha}', '{self.recolectores.ci}', '{self.clase_cacao}', '{self.precio}', '{self.cantidad}', '{self.humedad}', '{self.merma_porcentaje}', '{self.merma_kg}', '{self.cantidad_total}', '{self.monto}')"

    def merma_porc(self):
        """ Calcula la humedad de superficie """
        return 100 * self.merma_kg / self.cantidad_total
    
    def ha(self):
        """ Calcula la humedad de la almendra """
        hs = self.cantidad * self.merma_porc()
        return hs * 2 if self.almendra else hs

class Evento(db.Model):
    """ Modelo de eventos """
    __tablename__ = 'eventos'

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    evento = db.Column(db.String(120), nullable=False)
    modulo = db.Column(db.String(120), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    descripcion = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"Evento('{self.usuario}', '{self.evento}', '{self.modulo}', '{self.fecha}', '{self.descripcion}')"

class Financia(db.Model):
    """ Modelo de financias """
    __tablename__ = 'financias'

    id = db.Column(db.Integer, primary_key=True)
    cosecha_id = db.Column(db.Integer, db.ForeignKey('cosechas.id'), nullable=False)
    recolector_id = db.Column(db.Integer, db.ForeignKey('recolectores.id'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    letra_cambio = db.Column(db.String(120), nullable=False)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    pago = db.Column(db.Boolean, default=False)
    observacion = db.Column(db.String(120))

    def __repr__(self):
        return f"Financia('{self.cosechas.descripcion}', '{self.fecha}', '{self.recolectores.ci}', '{self.letra_cambio}', '{self.fecha_vencimiento}', '{self.monto}', '{self.pago}')"

class Banco(db.Model):
    """ Modelo de banco """
    __tablename__ = 'bancos'

    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, nullable=True, unique=True)
    financia_id = db.Column(db.Integer, nullable=True, unique=True)
    fecha = db.Column(db.DateTime, nullable=False)
    concepto = db.Column(db.String(120), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    credito = db.Column(db.Boolean, nullable=False)
    agg_gerente = db.Column(db.Boolean, default=False)
    revertido = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Banco('{self.compra_id}', '{self.financia_id}','{self.fecha}', '{self.concepto}', '{self.monto}', '{self.credito}', '{self.agg_gerente}')"