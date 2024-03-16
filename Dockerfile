# Dockerfile

# Stage 1: HTTP Server
FROM python:3.8-slim AS http-server
WORKDIR /app
COPY main.py requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Socket Server
FROM python:3.8-slim AS socket-server
WORKDIR /app
COPY socket_server.py requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final Image
FROM python:3.8-slim
WORKDIR /app
COPY --from=http-server /app /http-server
COPY --from=socket-server /app /socket-server
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000 5000 27017

CMD ["python", "socket_server.py"]


ENTRYPOINT ["python", "socket_server.py"]