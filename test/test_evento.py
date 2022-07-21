import unittest
from app import *
from db_create import create_db
import os
import datetime

class EventoCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_evento.db'
        app.config['TESTING'] = True
        create_db("test_evento.db")

    @classmethod
    def tearDownClass(self):
        os.remove("database/test_evento.db")

    def test_flask(self):
        """ Verifica que Flask funcione correctamente """
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        response = tester.get('/eventos/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_page_loads(self):
        """ Verifica que las páginas (HTML) cargan exitosamente """
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        response = tester.get('/eventos/', content_type='html/text')
        self.assertIn(b'Logger de Eventos', response.data)

    def test_correct_delete(self):
        """ Verifica que se puede eliminar un evento """
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            tester.post('/tipo_recolector', data=dict(descripcion='Prueba', precio=1.0), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)

            evento = Evento.query.filter_by(descripcion=str(type)).first()
            self.assertTrue(evento is not None)
            tester.post(f'/eventos/{evento.id}/delete', follow_redirects=True)
            evento2 = Evento.query.filter_by(descripcion=str(type)).first()
            self.assertTrue(evento2 is None)

    def test_incorrect_delete(self):
        """ Verifica que no se puede eliminar un evento que no existe """
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            response = tester.post(f'eventos/1000000000000/delete', follow_redirects=True)
            self.assertIn(b'El evento no se encuentra registrado.', response.data)
            
    def test_search(self):
        """ Verifica que se puede buscar un evento """
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)      
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)

            evento = Evento.query.filter_by(descripcion=str(type)).first()
            self.assertTrue(evento is not None)

            response = tester.post('/eventos/search', data=dict(search_evento='Agregar Tipo Recolector'), follow_redirects=True)
            self.assertIn(b'Agregar Tipo Recolector', response.data)
    
    # ---------------------------- VISTA DE PERFILES -------------------------------------------------
    def test_register_perfil(self):
        """ Verifica que se registra un evento al agregar un perfil"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="admin", password="admin"), follow_redirects=True)
            tester.post('/perfiles', data=dict(
                    nombre_usuario='Prueba', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            perfil = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(perfil is not None)

            evento = Evento.query.filter_by(descripcion=str(perfil)).first()
            self.assertTrue(evento is not None)


    def test_update_perfil(self):
        """ Verifica que se registra un evento al modificar un perfil"""
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post('/login', data=dict(nombre_usuario="admin", password="admin"), follow_redirects=True)

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    nombre_usuario='PruebaModificar', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = Usuario.query.filter_by(nombre_usuario='PruebaModificar').first()
            self.assertTrue(user is not None)

            # Edita perfil
            tester.post('/perfiles/update/' + str(user.id), data=dict(
                    nombre_usuario='PruebaModificar', nombre='Prueba2', apellido='Prueba2',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user2 = Usuario.query.filter_by(nombre_usuario='PruebaModificar').first()
            evento = Evento.query.filter_by(descripcion=str(user) + ";" + str(user2)).first()
            self.assertTrue(evento is not None)

    def test_delete_perfil(self):
        """ Verifica que se registra un evento al eliminar un perfil"""
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="admin", password="admin"), follow_redirects=True)

            tester.post('/perfiles', data=dict(
                    nombre_usuario='Prueba', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is not None)

            # Elimina perfil
            tester.post('/perfiles/delete/' + str(user.id), follow_redirects=True)
            evento = Evento.query.filter_by(evento='Eliminar Usuario', descripcion=str(user)).first()
            self.assertTrue(evento is not None)

    # ---------------------------- VISTA DE TIPO DE RECOLECTORES -------------------------------------------------
    def test_register_tipo_recolector(self):
        """ Verifica que se registra un evento al agregar un tipo de recolector"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            tester.post('/tipo_recolector', data=dict(descripcion='Prueba', precio=1.0), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()

            evento = Evento.query.filter_by(descripcion=str(type)).first()
            self.assertTrue(evento is not None)
        

    def test_update_tipo_recolector(self):
        """ Verifica que se registra un evento al modificar un tipo de recolector"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            tester.post('/tipo_recolector', data=dict(
                    descripcion='PruebaModificar',
                    precio=1.0
                ), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='PruebaModificar').first()
            self.assertTrue(type is not None)

            # Edita tipo de recolector
            tester.post('/tipo_recolector/update/' + str(type.id), data=dict(
                    descripcion='PruebaModificar2',
                    precio=1.0
                ), follow_redirects=True)
            type2 = TipoRecolector.query.filter_by(descripcion='PruebaModificar2').first()

            evento = Evento.query.filter_by(descripcion=str(type) + ";" + str(type2)).first()
            self.assertTrue(evento is not None)

    def test_delete_tipo_recolector(self):
        """ Verifica que se registra un evento al eliminar un tipo de recolector"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            tester.post('/tipo_recolector', data=dict(
                    descripcion='Prueba',
                    precio=1.0
                ), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()

            tester.post('/tipo_recolector/delete/' + str(type.id), follow_redirects=True)
            evento = Evento.query.filter_by(evento='Eliminar Tipo Recolector', descripcion=str(type)).first()
            self.assertTrue(evento is not None)

    # ---------------------------- VISTA DE RECOLECTORES -------------------------------------------------
    def test_register_recolector(self):
        """ Verifica que se registra un evento al agregar un recolector"""
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            tester.post('/tipo_recolector', data=dict(
                    descripcion='Prueba',
                    precio=1.0
                ), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()

            # Registra recolector
            tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=type.id)
            , follow_redirects=True)
            
            prod = Recolector.query.filter_by(ci="V-22222222").first()

            evento = Evento.query.filter_by(descripcion=str(prod)).first()
            self.assertTrue(evento is not None)

    def test_update_recolector(self):
        """ Verifica que se registra un evento al modificar un recolector"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            tester.post('/tipo_recolector', data=dict(
                    descripcion='Prueba',
                    precio=1.0
                ), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()

            tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=type.id)
            , follow_redirects=True)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            if str(prod) == '':
                self.assertTrue(False)
            # Edita recolector
            tester.post('/recolector/update/' + str(prod.id), data=dict(
                cedula="V-22222222", nombre='PruebaModificar', apellido='PruebaModificar',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=type.id)
            , follow_redirects=True)
            prod2 = Recolector.query.filter_by(id=prod.id).first()
            evento = Evento.query.filter_by(descripcion=f'{prod};{prod2}').first()
            self.assertTrue(evento is not None)


    def test_delete_recolector(self):
        """ Verifica que se registra un evento al eliminar un recolector"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            tester.post('/tipo_recolector', data=dict(
                    descripcion='Prueba',
                    precio=1.0
                ), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=type.id)
            , follow_redirects=True)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            if str(prod) == '':
                self.assertTrue(False)
            # Elimina recolector
            tester.post('/recolector/delete/' + str(prod.id), follow_redirects=True)
            evento = Evento.query.filter_by(evento='Eliminar Recolector', descripcion=str(prod)).first()
            self.assertTrue(evento is not None)

    # ---------------------------- VISTA DE COSECHAS -------------------------------------------------
    def test_register_cosecha(self):
        """ Verifica que se registra un evento al agregar una cosecha"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            # Registra tipo de cosecha
            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba 2022-2023',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)
            response = tester.get('/cosecha', follow_redirects=True)
            cos = Cosecha.query.filter_by(descripcion='Cosecha Prueba 2022-2023').first()

            evento = Evento.query.filter_by(descripcion=str(cos)).first()
            self.assertTrue(evento is not None)

    def test_update_cosecha(self):
        """ Verifica que se registra un evento al modificar una cosecha"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba Antes',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)
            cosecha = Cosecha.query.filter_by(descripcion='Cosecha Prueba Antes').first()

            # Edita tipo de cosecha
            tester.post(f'/cosecha/{cosecha.id}/update', data=dict(
                    descripcion='Cosecha Prueba Editada',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)
            cosecha2 = Cosecha.query.filter_by(descripcion='Cosecha Prueba Editada').first()

            evento = Evento.query.filter_by(descripcion=str(cosecha) + ";" + str(cosecha2)).first()
            self.assertTrue(evento is not None)

    def test_delete_cosecha(self):
        """ Verifica que se registra un evento al eliminar una cosecha"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)
            cos = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()

            # Elimina cosecha
            tester.post(f'/cosecha/{cos.id}/delete', follow_redirects=True)
            evento = Evento.query.filter_by(evento='Eliminar Cosecha', descripcion=str(cos)).first()
            self.assertTrue(evento is not None)

    # ---------------------------- VISTA DE COMPRAS -------------------------------------------------
    def test_register_compra(self):
        """ Verifica que se registra un evento al agregar una compra"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tester.post(f'/cosecha/{id}/compras', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0,
                    cantidad = 0, humedad = 0, merma_porcentaje = 0, 
                    monto = 0, observacion = 'PRUEBA',
                ), follow_redirects=True)

            compra = Compra.query.filter_by(observacion='PRUEBA').first()
            evento = Evento.query.filter_by(evento='Agregar Compra', descripcion=str(compra)).first()
            self.assertTrue(evento is not None)

    def test_update_compra(self):
        """ Verifica que se registra un evento al modificar una compra"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tester.post(f'/cosecha/{id}/compras', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0,
                    cantidad = 0, humedad = 0, merma_porcentaje = 0, 
                    monto = 0, observacion = 'xxxx',
                ), follow_redirects=True)
            compra = Compra.query.filter_by(observacion="xxxx").first()
            if str(compra) == '':
                self.assertTrue(False)

            tester.post(f'/cosecha/{id}/compras/{compra.id}/update', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0,
                    cantidad = 0, humedad = 0, merma_porcentaje = 0,  
                    monto = 0, observacion = 'PRUEBA EDITAR'
                ), follow_redirects=True)
            compra2 = Compra.query.filter_by(observacion='PRUEBA EDITAR').first()
            evento = Evento.query.filter_by(evento='Editar Compra', descripcion=str(compra) + ";" + str(compra2)).first()
            self.assertTrue(evento is not None)

    def test_delete_compra(self):
        """ Verifica que se registra un evento al eliminar una compra"""
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tester.post(f'/cosecha/{id}/compras', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0, 
                    cantidad = 0, humedad = 0, merma_porcentaje = 0,
                    monto = 0, observacion = 'PRUEBA',
                ), follow_redirects=True)

            compra = Compra.query.filter_by(observacion="PRUEBA").first()
            if str(compra) == '':
                self.assertTrue(False)
            tester.post(f'/cosecha/{id}/compras/{compra.id}/delete', follow_redirects=True)
            evento = Evento.query.filter_by(evento='Eliminar Compra', descripcion=str(compra)).first()
            self.assertTrue(evento is not None)
