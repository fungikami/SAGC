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
    cosecha1 = Cosecha(descripcion='Cosecha Dic-Mar 2022', inicio=date1, cierre=date2, estado=False)

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

    # Insertar recolectores
    prod1=TipoRecolector(descripcion="Productor 1", precio=0.0)
    prod2=TipoRecolector(descripcion="Productor 2", precio=0.15)
    prod3=TipoRecolector(descripcion="Productor 3", precio=0.2)
    rev1=TipoRecolector(descripcion="Revendedor 1", precio=0.25)
    db.session.add_all([prod1, prod2, prod3, rev1])
    
    # Insertar Productores, tipo_recolector debe ser un objeto de la clase TypeProductor
    p1 = Productor(ci="V-12345678", nombre="Productor1", apellido="Productor1", telefono="0212-1234567", celular="0212-1234567", tipo_recolector=prod1, direccion1="Direccion1", direccion2="Direccion2")
    p2 = Productor(ci="E-87654321", nombre="Productor2", apellido="Productor2", telefono="0212-1234567", celular="0212-1234567", tipo_recolector=prod2, direccion1="Direccion1", direccion2="Direccion2")
    db.session.add_all([p1, p2])

    # Insertar Compra de una cosecha
    c1 = Compra(cosechas=cosecha1, productores=p1, tipo_prod=prod1, fecha=date1, clase_cacao="Fermentado (F1)",
        precio=1.1, cantidad=1500.0, humedad=14.0, merma_porcentaje=3.0, merma_kg=45.00, cantidad_total=1445.0, monto=2384.25, observacion="xxxx")

    c2 = Compra(cosechas=cosecha2, productores=p2, tipo_prod=prod2, fecha=date1, clase_cacao="Fermentado (F1)",
        precio=1.1, cantidad=1500.0, humedad=14.0, merma_porcentaje=3.0, merma_kg=45.00, cantidad_total=1445.0, monto=2384.25, observacion="xxxx")
        
    db.session.add_all([c1, c2])

    # Guardar cambios en la database
    db.session.commit()

if __name__ == '__main__':
    create_db("data.db")

