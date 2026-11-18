# Documento de pruebas del contenedor

Pruebas realizadas el 18/11/2026 en mi máquina virtual con Ubuntu Server 24.04 y Docker 29.10.0, conectado por SSH (`ssh -p 2222 duro@127.0.0.1`).

## Construcción de la imagen

Desde la carpeta del proyecto (`~/practica-1.4`):

```bash
docker build -t api-practica:1.0 .
docker images
```

La construcción termina con "FINISHED" y los 5 pasos del Dockerfile. La imagen api-practica:1.0 ocupa 201 MB.

![Captura 6](img/captura6.png)

## Sentencia de arranque del contenedor

```bash
docker run -d --name api-backend -p 8080:8000 api-practica:1.0
```

- `-d`: arranca el contenedor en segundo plano.
- `--name api-backend`: le pone un nombre para no tener que usar el ID.
- `-p 8080:8000`: publica el puerto 8000 del contenedor, donde escucha uvicorn, en el puerto 8080 de la VM. Usé el 8080 para no chocar con Gunicorn de la práctica 1.3, que usaba el 8000.
- `api-practica:1.0`: la imagen que construí.

```bash
docker ps
```

El contenedor aparece con estado "Up".

![Captura 7](img/captura7.png)

## Pruebas de los endpoints con curl

| Prueba | Comando | Resultado esperado | Resultado obtenido |
|---|---|---|---|
| Salud | `curl -i http://127.0.0.1:8080/health` | 200 y `{"status":"ok"}` | 200 OK, content-type application/json, server uvicorn, `{"status":"ok"}` |
| Versión | `curl http://127.0.0.1:8080/version` | `{"version":"0.1.0"}` | `{"version":"0.1.0"}` |
| Ping | `curl http://127.0.0.1:8080/ping` | `{"message":"pong"}` | `{"message":"pong"}` |
| Logs | `docker logs api-backend` | Peticiones registradas | Arranque de uvicorn en 0.0.0.0:8000 y los tres GET con 200 OK |

![Captura 8](img/captura8.png)

## Acceso a /docs (Swagger)

Como la VM está en NAT, desde el navegador del PC no llego directamente al puerto 8080. Abrí una conexión SSH con un túnel desde el PC:

```bash
ssh -p 2222 -L 8080:127.0.0.1:8080 duro@127.0.0.1
```

Con esa conexión abierta entré en `http://127.0.0.1:8080/docs` desde el navegador del PC. Aparece la documentación de Swagger con el título "API practica 1.1", la versión 0.1.0, la descripción y los tres endpoints. En /health pulsé "Try it out" y "Execute" y la respuesta fue código 200 con `{"status": "ok"}`.

![Captura 9](img/captura9.png)

## Ciclo de vida

| Acción | Comando | Resultado |
|---|---|---|
| Parar | `docker stop api-backend` | `docker ps -a` lo muestra como "Exited (0)" y curl da "Couldn't connect to server" |
| Arrancar | `docker start api-backend` | Vuelve a estar "Up" |
| Reiniciar | `docker restart api-backend` | Vuelve a estar "Up"; el primer curl justo después dio "Connection reset by peer" porque uvicorn aún estaba arrancando, y al repetirlo respondió `{"status":"ok"}` |
| Eliminar | `docker stop api-backend` y `docker rm api-backend` | Ya no aparece en `docker ps -a`, pero la imagen sigue en `docker images` |
| Volver a crear | `docker run -d --name api-backend -p 8080:8000 api-practica:1.0` | Contenedor nuevo en estado "Up" |

![Captura 10](img/captura10.png)

![Captura 11](img/captura11.png)

![Captura 12](img/captura12.png)

![Captura 13](img/captura13.png)

## Resultado

Todas las pruebas son correctas: la imagen se construye sin errores, el contenedor arranca, los tres endpoints responden con 200 y JSON, Swagger funciona en /docs y el contenedor se puede parar, arrancar, reiniciar, eliminar y volver a crear.
