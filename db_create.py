from app import db
from models import *
import os
import datetime

def create_db(nombre_db):
    # Crea la database y las tablas
    if not os.path.exists("database/" + nombre_db):
        db.create_all()
        print("Database creada")

    # Insertar roles
    admin = Rol(nombre='Administrador')
    analista = Rol(nombre='Analista de Ventas')
    vendedor = Rol(nombre='Vendedor')
    db.session.add(admin)
    db.session.add(analista)
    db.session.add(vendedor)

    # Insertar cosechas
    y, m, d = '2020-03-01'.split('-')
    date1 = datetime.datetime(int(y), int(m), int(d))
    y, m, d = '2020-03-31'.split('-')
    date2 = datetime.datetime(int(y), int(m), int(d))
    cosecha1 = Cosecha(descripcion='Cosecha Dic-Mar 2022', inicio=date1, cierre=date2)

    y, m, d = '2020-07-01'.split('-')
    date1 = datetime.datetime(int(y), int(m), int(d))
    y, m, d = '2020-08-31'.split('-')
    date2 = datetime.datetime(int(y), int(m), int(d))
    cosecha2 = Cosecha(descripcion='Cosecha Jul-Ago 2022', inicio=date1, cierre=date2)

    cosechas = [cosecha1, cosecha2]
    db.session.add_all(cosechas)

    # Insertar data (aquí se pueden agregar los administradores)
    user1 = Usuario(nombre_usuario="admin", nombre="Administrador", apellido="Administrador", password="admin", rols=admin)
    user2 = Usuario(nombre_usuario="user", nombre="Usuario", apellido="Usuario", password="user", rols=analista)
    db.session.add(user1)
    db.session.add(user2)
    user1.cosechas.append(cosecha1)
    user1.cosechas.append(cosecha2)
    user2.cosechas.append(cosecha2)


    prod1=TipoRecolector(descripcion="Productor 1")
    prod2=TipoRecolector(descripcion="Productor 2")
    prod3=TipoRecolector(descripcion="Productor 3")
    rev1=TipoRecolector(descripcion="Revendedor 1")
    db.session.add_all([prod1, prod2, prod3, rev1])
                                                                                                            # tipo_recolector debe ser un objeto de la clase TypeProductor
    p1 = Productor(ci="V-12345678", nombre="Productor1", apellido="Productor1", telefono="0212-1234567", celular="0212-1234567", tipo_recolector=prod1, direccion1="Direccion1", direccion2="Direccion2")
    p2 = Productor(ci="E-87654321", nombre="Productor2", apellido="Productor2", telefono="0212-1234567", celular="0212-1234567", tipo_recolector=prod2, direccion1="Direccion1", direccion2="Direccion2")
    db.session.add_all([p1, p2])

    # Guardar cambios en la database
    db.session.commit()

if __name__ == '__main__':
    create_db("data.db")

