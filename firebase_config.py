import firebase_admin
from firebase_admin import credentials, firestore
import sys, os

def init_firebase():
    """
    Inicializa la conexión con Firebase usando el archivo de credenciales.
    Devuelve el cliente de Firestore para hacer consultas a la base de datos.
    """
    cred = credentials.Certificate("dishtrack-58422-firebase-adminsdk-fbsvc-55fb6d08bb.json")
    firebase_admin.initialize_app(cred)
    return firestore.client()