import unittest
from app import app, Usuario
from db_create import create_db
from flask import url_for, request
import os

class PerfilesTestCase(unittest.TestCase):

    # Verifica que el registro funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="admin", password="admin"), follow_redirects=True)
            
            # Registra perfil
            tester.post('/perfiles', data=dict(
                    nombre_usuario='Prueba', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )

            response = tester.get('/perfiles', follow_redirects=True)
            self.assertIn(b'Perfiles de Usuarios', response.data)
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is not None)

    # Verifica que se muestra error si se realiza un registro incorrecto (ya sea un user que ya existe, una contraseña mala...)
    def test_incorrect_register(self):
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="admin", password="admin"), follow_redirects=True)

            # Registro con usuario largo
            response = tester.post('/perfiles', data=dict(
                nombre_usuario="adminadminadminadminadmin", nombre="Administrador", apellido="Administrador", 
                password="admin", rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'El nombre de usuario no puede tener mas de 20 caracteres', response.data)

            # Registrarse a si mismo
            response = tester.post('/perfiles', data=dict(
                nombre_usuario="admin", nombre="Administrador", apellido="Administrador", 
                password="admin", rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'El nombre de usuario ya se encuentra en uso', response.data)
            
            # Registrarse con contraseña muy corta
            response = tester.post('/perfiles', data=dict(
                nombre_usuario="prueba", nombre="Prueba", apellido="Prueba",
                password="pr", rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'debe tener al menos 8 caracteres', response.data)
            
            # Registrarse con contraseña muy larga
            response = tester.post('/perfiles', data=dict(
                nombre_usuario="prueba", nombre="Prueba", apellido="Prueba",
                password="prprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprpr", 
                rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'no puede tener mas de 80 caracteres', response.data)
    
    #  Verifica que se puede eliminar un perfil
    def test_correct_delete(self):
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
            response = tester.post('/perfiles/delete/' + str(user.id), follow_redirects=True)
            self.assertIn(b'Se ha eliminado exitosamente.', response.data)
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is None)

    #  Verifica que no se puede eliminar un perfil que no existe
    def test_incorrect_delete(self):
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
            id = str(user.id)

            # Elimina perfil
            response = tester.post('/perfiles/delete/' + str(user.id), follow_redirects=True)
            self.assertIn(b'Se ha eliminado exitosamente.', response.data)
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is None)

            # Elimina perfil que no existe
            tester.post('/perfiles/delete/' + id, follow_redirects=True)
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is None)

    #  Verifica que se puede editar un perfil
    def test_correct_edit(self):
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
            response = tester.post('/perfiles/update/' + str(user.id), data=dict(
                    nombre_usuario='PruebaModificar', nombre='Prueba2', apellido='Prueba2',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            self.assertIn(b'Se ha modificado exitosamente.', response.data)

            user = Usuario.query.filter_by(nombre_usuario='PruebaModificar', nombre='Prueba2').first()
            self.assertTrue(user is not None)

    #  Verifica que no se puede editar perfil que no existe
    def test_incorrect_edit(self):
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="admin", password="admin"), follow_redirects=True)

            tester.post('/perfiles', data=dict(
                    nombre_usuario='PruebaModificar', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = Usuario.query.filter_by(nombre_usuario='PruebaModificar').first()
            self.assertTrue(user is not None)

            # Edita perfil con un nombre_usuario que ya existe
            response = tester.post('/perfiles/update/' + str(user.id), data=dict(
                    nombre_usuario='admin', nombre='Prueba2', apellido='Prueba2',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            self.assertIn(b'El nombre de usuario ya se encuentra en uso.', response.data)

            user = Usuario.query.filter_by(nombre='Prueba2').first()
            self.assertTrue(user is not None)

    #  Verifica que se puede buscar un perfil
    def test_search(self):
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

            # Busca perfil
            response = tester.post('/perfiles/search', data=dict(
                    search_perfil='Prueba'
                ), follow_redirects=True
            )
            self.assertIn(b'Prueba', response.data)

if __name__ == '__main__':

    # Se cambia la base de datos para usar la de los test
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_db.db'
    app.config['TESTING'] = True
    # Verificamos si no existe la base de datos para los test
    if not os.path.exists("database/test_db.db"):
        create_db("database/test_db.db")

    unittest.main()