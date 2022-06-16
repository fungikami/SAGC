from app import db
from models import User, Producer, TypeProducer
from app import Roles

# Crea la database y las tablas
db.create_all()

# Insertar data (aquí se pueden agregar los administradores)
db.session.add(User(username="admin", name="Administrador", surname="Administrador", password="admin", rol=Roles.Administrador.name))
db.session.add(User(username="user", name="Usuario", surname="Usuario", password="user", rol=Roles.Usuario.name))

prod1=TypeProducer(description="Productor1")
prod2=TypeProducer(description="Productor2")
db.session.add_all([prod1, prod2])
                                                                                                        # type_producer debe ser un objeto de la clase TypeProductor
p1 = Producer(ci=12345678, name="Productor1", surname="Productor1", telephone="0212-1234567", phone="0212-1234567", type_producer=prod1, direction1="Direccion1", direction2="Direccion2")
p2 = Producer(ci=87654321, name="Productor2", surname="Productor2", telephone="0212-1234567", phone="0212-1234567", type_producer=prod2, direction1="Direccion1", direction2="Direccion2")
db.session.add_all([p1, p2])

# Guardar cambios en la database
db.session.commit()

