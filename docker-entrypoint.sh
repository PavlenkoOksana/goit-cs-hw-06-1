#!/bin/sh

# Start MongoDB
docker run -d --name mongodb -p 27017:27017 mongo

# Start Socket Server
docker exec -d mongodb python /socket-server/socket_server.py &

# Start HTTP Server
python /http-server/main.py