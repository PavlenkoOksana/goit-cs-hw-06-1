import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import threading
import json
from datetime import datetime
from pymongo import MongoClient

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)
        
        send_to_socket_server(data_dict)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

def run_http_server():
    server_address = ('', 3000)
    http = HTTPServer(server_address, HttpHandler)
    try:
        print("HTTP Server is running on port 3000")
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def send_to_socket_server(data_dict):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 5000))
        message_str = json.dumps(data_dict)
        client_socket.sendall(message_str.encode())
        client_socket.close()
    except Exception as e:
        print(f"Error sending data to socket server: {e}")

def start_socket_server():
    mongo_host = 'localhost'
    mongo_port = 27017
    mongo_db = 'chat_database'
    collection_name = 'messages'

    client = MongoClient(mongo_host, mongo_port)
    db = client[mongo_db]
    collection = db[collection_name]

    socket_host = 'localhost'
    socket_port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((socket_host, socket_port))
    server_socket.listen(1)

    print(f"Socket Server is running on {socket_host}:{socket_port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        data = client_socket.recv(1024)
        if not data:
            break

        message_str = data.decode()

        message_dict = json.loads(message_str)

        message_dict['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        collection.insert_one(message_dict)
        print("Message saved to MongoDB:", message_dict)

        client_socket.close()

    server_socket.close()

if __name__ == '__main__':
    http_thread = threading.Thread(target=run_http_server)
    http_thread.start()

    start_socket_server()