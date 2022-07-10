import unittest
from app import *
from db_create import create_db
import os

if __name__ == '__main__':

    # Se cambia la base de datos para usar la de los test
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_db.db'
    app.config['TESTING'] = True
    # Verificamos si no existe la base de datos para los test
    if not os.path.exists("database/test_db.db"):
        create_db("database/test_db.db")

    unittest.main()