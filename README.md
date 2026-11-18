# Práctica 1.4: Docker y primer contenedor

Backend de FastAPI de la práctica 1.1 (endpoints /health, /version y /ping) empaquetado en una imagen Docker.

## Estructura

```
app/
  __init__.py
  main.py
docs/
  arquitectura.md   comparación instalación directa vs contenedor y nube
  pruebas.md        sentencia de arranque, pruebas y Swagger
  img/              capturas
Dockerfile
.dockerignore
requirements.txt
```

## Cómo usarlo

Hace falta tener Docker instalado.

```bash
docker build -t api-practica:1.0 .
docker run -d --name api-backend -p 8080:8000 api-practica:1.0
curl http://127.0.0.1:8080/health
```

La documentación de Swagger está en `http://127.0.0.1:8080/docs`.

Para parar y eliminar el contenedor:

```bash
docker stop api-backend
docker rm api-backend
```

## Decisiones

- Imagen base python:3.13-slim: trae Python 3.13 y es mucho más ligera que la imagen completa.
- Primero se copia requirements.txt y se instalan las dependencias, y después el código. Así Docker reutiliza la capa de dependencias en caché si solo cambia el código.
- Versiones fijadas en requirements.txt para que la imagen sea reproducible.
- `--no-cache-dir` en pip para no guardar la caché de descargas dentro de la imagen.
- uvicorn escucha en 0.0.0.0 dentro del contenedor, porque si escuchara en 127.0.0.1 no se podría llegar desde fuera del contenedor.
- Puerto 8080 en la VM para no chocar con el 8000 que usé con Gunicorn en la práctica 1.3.
- .dockerignore para no meter en la imagen el entorno virtual, la caché de Python, git ni la documentación.
