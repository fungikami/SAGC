from app import db
from models import Rol, User, Producer, TypeProducer
from app import Roles

# Crea la database y las tablas
db.create_all()

# Insertar roles
admin = Rol(name='Administrador')
analista = Rol(name='Analista de Ventas')
vendedor = Rol(name='Vendedor')
db.session.add(admin)
db.session.add(analista)
db.session.add(vendedor)

# Insertar data (aquí se pueden agregar los administradores)
db.session.add(User(username="admin", name="Administrador", surname="Administrador", password="admin", rols=admin))
db.session.add(User(username="user", name="Usuario", surname="Usuario", password="user", rols=analista))

prod1=TypeProducer(description="Productor 1")
prod2=TypeProducer(description="Productor 2")
prod3=TypeProducer(description="Productor 3")
rev1=TypeProducer(description="Revendedor 1")
db.session.add_all([prod1, prod2, prod3, rev1])
                                                                                                        # type_producer debe ser un objeto de la clase TypeProductor
p1 = Producer(ci=12345678, name="Productor1", surname="Productor1", telephone="0212-1234567", phone="0212-1234567", type_producer=prod1, direction1="Direccion1", direction2="Direccion2")
p2 = Producer(ci=87654321, name="Productor2", surname="Productor2", telephone="0212-1234567", phone="0212-1234567", type_producer=prod2, direction1="Direccion1", direction2="Direccion2")
db.session.add_all([p1, p2])

# Guardar cambios en la database
db.session.commit()

