import socket
import json
from pymongo import MongoClient
# Verbindung zur MongoDB-Datenbank herstellen
client = MongoClient('mongodb://localhost:27017/')
db = client['chat_database']  # Datenbank 'form_data' auswählen
collection = db['entries']  # Collection 'entries' auswählen

# Socket-Server einrichten
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5000))
server_socket.listen(5)

print("Socket-Server läuft auf Port 5000...")

while True:
    # Auf eingehende Verbindungen warten
    client_socket, addr = server_socket.accept()
    print('Verbindung von', addr)

    # Daten empfangen und in JSON umwandeln
    data = client_socket.recv(1024).decode()
    form_data = json.loads(data)

    # Daten in MongoDB speichern
    collection.insert_one(form_data)

    print("Daten erfolgreich in MongoDB gespeichert:", form_data)

    # Verbindung schließen
    client_socket.close()