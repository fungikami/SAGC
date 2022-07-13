import unittest
from app import *
from db_create import create_db
import os
import datetime

class CosechaCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_cosecha.db'
        app.config['TESTING'] = True
        create_db("test_cosecha.db")

    @classmethod
    def tearDownClass(self):
        os.remove("database/test_cosecha.db")

    def test_flask(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        response = tester.get('/cosecha', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente 
    def test_page_loads(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        response = tester.get('/cosecha')
        self.assertIn(b'Portafolio de Cosechas', response.data)

    # Verifica que el registro funciona exitosamente
    def test_correct_register(self):
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
            self.assertIn(b'Portafolio de Cosechas', response.data)
            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba 2022-2023').first()
            self.assertTrue(type is not None)
            self.assertTrue(str(type) == "Cosecha('Cosecha Prueba 2022-2023')")

    # Verifica que se muestra error si se realiza un registro de una cosecha que ya existe
    def test_incorrect_register_A(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            # Registra cosecha
            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)
            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)           

            # Registra cosecha nuevamente.
            response = tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            self.assertIn(b'La cosecha que se intenta agregar ya se encuentra definida.', response.data)

# Verifica que se muestra error si se realiza un registro de una cosecha con fecha de inicio mayor a la de cierre
    def test_incorrect_register_B(self):
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            # Registra cosecha
            y, m, d = '2022-11-01'.split('-')
            date1 = datetime.datetime(int(y), int(m), int(d))
            y, m, d = '2008-03-31'.split('-')
            date2 = datetime.datetime(int(y), int(m), int(d))
            response = tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Error Fecha',
                    inicio= date1.strftime("%Y-%m-%d"),
                    cierre= date2.strftime("%Y-%m-%d"),
                ), follow_redirects=True)
            self.assertIn(b'La fecha de cierre debe ser posterior a la fecha de inicio.', response.data)

    #  Verifica que se puede eliminar una cosecha
    def test_correct_delete(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)
            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)

            # Elimina cosecha
            tester.post('/cosecha/delete/' + str(type.id), follow_redirects=True)
            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)

    #  Verifica que no se puede eliminar una cosecha que no existe
    def test_incorrect_delete(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            
            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)
            id = str(type.id)

            # Elimina tipo de recolector
            tester.post('/cosecha/delete/' + id, follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is None)

            # Elimina tipo de recolector de nuevo
            tester.post('/cosecha/delete/'  + id, follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is None)

    #  Verifica que se puede editar un tipo de recolector
    def test_correct_edit(self):
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
            self.assertTrue(cosecha is not None)

            # Edita tipo de cosecha
            tester.post(f'/cosecha/{cosecha.id}/update', data=dict(
                    descripcion='Cosecha Prueba Editada',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            cosecha = Cosecha.query.filter_by(descripcion='Cosecha Prueba Antes').first()
            #self.assertTrue(cosecha is None)

            cosecha = Cosecha.query.filter_by(descripcion='Cosecha Prueba Editada', inicio=date.strftime("%Y-%m-%d")).first()
            #self.assertTrue(cosecha is not None)
        
    #  Verifica que se puede buscar una cosecha
    def test_search(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)            

            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)

            tester.post('/cosecha/search', data=dict(
                    search_recolector='Cosecha Prueba'
                ), follow_redirects=True)

            # Buscar tipo de cosecha
            response = tester.get('/cosecha', follow_redirects=True)
            self.assertIn(b'Portafolio de Cosechas', response.data)
            self.assertIn(b'Cosecha Prueba', response.data)

    def test_generar_compras(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True) 
            tester.post('/cosecha/search', data=dict(
                    search_cosecha='Cosecha Abr-Jun 22'
                ), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            response = tester.get(f'/cosecha/{id}/compras', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_generar_compras_incorrect(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True) 
            cosecha = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first()
            response = tester.get(f'/cosecha/{cosecha.id}/compras', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(bytes("Portafolio de Cosechas", "utf-8"), response.data)

    def test_habilitar(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True) 
            
            # Registrar cosecha
            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            cosecha = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            estado = cosecha.estado

            # Verificar que se deshabilita 
            tester.get(f'/cosecha/{cosecha.id}/habilitar', follow_redirects=True)
            cosecha = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(cosecha.estado != estado)

            # Verificar que se habilita 
            tester.get(f'/cosecha/{cosecha.id}/habilitar', follow_redirects=True)
            cosecha = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(cosecha.estado == estado)

    def test_habilitar_incorrect(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True) 
            cosecha = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            response = tester.get(f'/cosecha/{cosecha.id}/habilitar', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(bytes("Portafolio de Cosechas", "utf-8"), response.data)

    def test_listar(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True) 
            cosecha = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            response = tester.get(f'/cosecha/{cosecha.id}/listar', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    
if __name__ == '__main__':

    # Se cambia la base de datos para usar la de los test
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_db.db'
    app.config['TESTING'] = True
    # Verificamos si no existe la base de datos para los test
    if not os.path.exists("database/test_db.db"):
        create_db("database/test_db.db")

    unittest.main()